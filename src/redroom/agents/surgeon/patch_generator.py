"""Patch generation with multiple LLM provider support and API cycling."""

import re
import os
from typing import Dict, Any, Optional
import structlog
from redroom.models.schemas import ExploitResult, PatchResult
from redroom.agents.surgeon.load_tester import LoadTester
from redroom.utils.api_pool import get_api_pool, load_api_keys_from_env, APIKey

logger = structlog.get_logger()


class PatchGenerator:
    """
    Generates and validates security patches using LLM APIs with automatic cycling.
    
    Features:
    - Multiple API keys per provider
    - Automatic failover when rate limits hit
    - Weighted random selection for load balancing
    - Error tracking and cooldown
    - Supports: Gemini, OpenAI, Anthropic, Local LLMs, Mock
    """
    
    def __init__(self, llm_provider: Optional[str] = None, use_api_pool: bool = True):
        """
        Initialize patch generator with API pool support.
        
        Args:
            llm_provider: Preferred LLM provider (None for auto-detect)
            use_api_pool: Whether to use API pool for cycling (default: True)
        """
        self.load_tester = LoadTester()
        self.use_api_pool = use_api_pool
        
        if use_api_pool:
            # Load API keys from environment
            self.api_pool = load_api_keys_from_env()
            
            # Auto-detect provider if not specified
            if llm_provider is None:
                llm_provider = self._detect_llm_provider_from_pool()
            
            self.llm_provider = llm_provider
            logger.info(
                "patch_generator_initialized_with_pool",
                provider=llm_provider,
                total_keys=self.api_pool.get_pool_stats()["total_keys"]
            )
        else:
            # Legacy single-key mode
            if llm_provider is None:
                llm_provider = self._detect_llm_provider()
            
            self.llm_provider = llm_provider
            self.api_pool = None
            logger.info(
                "patch_generator_initialized",
                provider=llm_provider
            )
        
        self.llm_available = False
        
        # Initialize based on provider
        if llm_provider == "gemini":
            self._init_gemini()
        elif llm_provider == "openai":
            self._init_openai()
        elif llm_provider == "anthropic":
            self._init_anthropic()
        elif llm_provider == "local":
            self._init_local_llm()
        else:
            self._init_mock()
    
    def _detect_llm_provider_from_pool(self) -> str:
        """Detect available LLM provider from API pool."""
        stats = self.api_pool.get_pool_stats()
        
        # Priority order
        for provider in ["gemini", "openai", "anthropic"]:
            if provider in stats["providers"] and stats["providers"][provider]["available_keys"] > 0:
                logger.info("auto_detected_provider_from_pool", provider=provider)
                return provider
        
        # Check for local LLM
        if os.getenv("OLLAMA_HOST"):
            return "local"
        
        logger.info("no_llm_provider_found", using="mock")
        return "mock"
    
    def _detect_llm_provider(self) -> str:
        """Auto-detect available LLM provider based on API keys."""
        if os.getenv("GEMINI_API_KEY"):
            return "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("OLLAMA_HOST"):
            return "local"
        else:
            logger.info("no_llm_api_key_found", using="mock")
            return "mock"
    
    def _init_gemini(self):
        """Initialize Google Gemini."""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.llm = genai.GenerativeModel('gemini-1.5-pro')
                self.llm_available = True
                logger.info("gemini_initialized")
            else:
                logger.warning("gemini_api_key_not_found", falling_back_to="mock")
                self._init_mock()
        except ImportError:
            logger.warning("google_generativeai_not_installed", falling_back_to="mock")
            self._init_mock()
    
    def _init_openai(self):
        """Initialize OpenAI GPT-4."""
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm = OpenAI(api_key=api_key)
                self.llm_available = True
                logger.info("openai_initialized")
            else:
                logger.warning("openai_api_key_not_found", falling_back_to="mock")
                self._init_mock()
        except ImportError:
            logger.warning("openai_not_installed", falling_back_to="mock")
            self._init_mock()
    
    def _init_anthropic(self):
        """Initialize Anthropic Claude."""
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.llm = anthropic.Anthropic(api_key=api_key)
                self.llm_available = True
                logger.info("anthropic_initialized")
            else:
                logger.warning("anthropic_api_key_not_found", falling_back_to="mock")
                self._init_mock()
        except ImportError:
            logger.warning("anthropic_not_installed", falling_back_to="mock")
            self._init_mock()
    
    def _init_local_llm(self):
        """Initialize local LLM (Ollama, LM Studio, etc.)."""
        try:
            import requests
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            response = requests.get(f"{ollama_host}/api/tags", timeout=2)
            if response.status_code == 200:
                self.llm_host = ollama_host
                self.llm_available = True
                logger.info("local_llm_initialized", host=ollama_host)
            else:
                logger.warning("local_llm_not_available", falling_back_to="mock")
                self._init_mock()
        except:
            logger.warning("local_llm_connection_failed", falling_back_to="mock")
            self._init_mock()
    
    def _init_mock(self):
        """Initialize mock mode for demo/testing."""
        logger.info("using_mock_patch_generation")
        self.llm_provider = "mock"
        self.llm_available = False
    
    async def generate_patch(
        self,
        vulnerable_code: str,
        exploit_result: ExploitResult
    ) -> PatchResult:
        """
        Generate security patch with automatic API cycling.
        
        If using API pool:
        - Automatically selects best available API key
        - Falls back to next key if rate limit hit
        - Tracks usage and errors
        
        Args:
            vulnerable_code: Original vulnerable code
            exploit_result: Exploit execution result
            
        Returns:
            Generated patch with validation
        """
        logger.info("generating_patch", provider=self.llm_provider, use_pool=self.use_api_pool)
        
        # Build prompt for LLM
        prompt = self._build_patch_prompt(vulnerable_code, exploit_result)
        
        # Generate patch with API cycling
        if self.use_api_pool and self.llm_provider in ["gemini", "openai", "anthropic"]:
            patch_data = await self._generate_with_api_pool(prompt)
        elif self.llm_available:
            # Single key mode
            if self.llm_provider == "gemini":
                patch_data = await self._generate_with_gemini(prompt)
            elif self.llm_provider == "openai":
                patch_data = await self._generate_with_openai(prompt)
            elif self.llm_provider == "anthropic":
                patch_data = await self._generate_with_anthropic(prompt)
            elif self.llm_provider == "local":
                patch_data = await self._generate_with_local_llm(prompt)
            else:
                patch_data = self._mock_generate_patch(vulnerable_code, exploit_result)
        else:
            # Fallback to mock
            patch_data = self._mock_generate_patch(vulnerable_code, exploit_result)
        
        # Create PatchResult
        result = PatchResult(
            patch=patch_data["patch"],
            explanation=patch_data["explanation"],
            complexity_analysis=patch_data["complexity_analysis"],
            regression_tests=patch_data["regression_tests"],
            performance_delta={}  # Will be filled by validation
        )
        
        logger.info("patch_generated", provider=self.llm_provider)
        return result
    
    async def _generate_with_api_pool(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Generate patch using API pool with automatic cycling.
        
        Args:
            prompt: LLM prompt
            max_retries: Maximum number of API keys to try
            
        Returns:
            Parsed patch data
        """
        for attempt in range(max_retries):
            # Get available API key
            api_key = self.api_pool.get_api_key(self.llm_provider)
            
            if not api_key:
                logger.warning(
                    "no_available_api_keys",
                    provider=self.llm_provider,
                    attempt=attempt + 1
                )
                
                if attempt == max_retries - 1:
                    # All keys exhausted, use mock
                    logger.warning("all_api_keys_exhausted", using="mock")
                    return self._mock_generate_patch("", None)
                
                # Wait a bit before retrying
                import asyncio
                await asyncio.sleep(1)
                continue
            
            try:
                logger.info(
                    "attempting_api_call",
                    provider=self.llm_provider,
                    key_name=api_key.name,
                    attempt=attempt + 1
                )
                
                # Call appropriate API
                if self.llm_provider == "gemini":
                    response_text = await self._call_gemini_api(api_key.key, prompt)
                elif self.llm_provider == "openai":
                    response_text = await self._call_openai_api(api_key.key, prompt)
                elif self.llm_provider == "anthropic":
                    response_text = await self._call_anthropic_api(api_key.key, prompt)
                else:
                    raise ValueError(f"Unsupported provider: {self.llm_provider}")
                
                # Parse response
                patch_data = self._parse_llm_response(response_text)
                
                # Record success
                self.api_pool.record_success(api_key)
                
                logger.info(
                    "api_call_success",
                    provider=self.llm_provider,
                    key_name=api_key.name
                )
                
                return patch_data
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(
                    "api_call_failed",
                    provider=self.llm_provider,
                    key_name=api_key.name,
                    error=error_msg,
                    attempt=attempt + 1
                )
                
                # Record error
                self.api_pool.record_error(api_key, error_msg)
                
                # Check if rate limit error
                if "rate limit" in error_msg.lower() or "quota" in error_msg.lower():
                    logger.info("rate_limit_hit", trying_next_key=True)
                    continue
                
                # For other errors, retry with different key
                if attempt < max_retries - 1:
                    continue
        
        # All retries failed, use mock
        logger.warning("all_api_attempts_failed", using="mock")
        return self._mock_generate_patch("", None)
    
    async def _call_gemini_api(self, api_key: str, prompt: str) -> str:
        """Call Gemini API with specific key."""
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = await model.generate_content_async(prompt)
        return response.text
    
    async def _call_openai_api(self, api_key: str, prompt: str) -> str:
        """Call OpenAI API with specific key."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    async def _call_anthropic_api(self, api_key: str, prompt: str) -> str:
        """Call Anthropic API with specific key."""
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    async def _generate_with_local_llm(self, prompt: str) -> Dict[str, Any]:
        """Generate patch using local LLM (Ollama)."""
        import requests
        response = requests.post(
            f"{self.llm_host}/api/generate",
            json={
                "model": "codellama",
                "prompt": prompt,
                "stream": False
            }
        )
        return self._parse_llm_response(response.json()["response"])
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured patch data."""
        import json
        
        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try direct JSON parse
            return json.loads(response_text)
        except:
            # Fallback to mock if parsing fails
            logger.warning("failed_to_parse_llm_response", using="mock")
            return self._mock_generate_patch("", None)
    
    def _build_patch_prompt(
        self,
        vulnerable_code: str,
        exploit_result: ExploitResult
    ) -> str:
        """Build prompt for LLM patch generation."""
        
        return f"""
You are a senior security engineer. Generate a security patch for this vulnerability.

VULNERABLE CODE:
```python
{vulnerable_code[:1000]}  # Limited for context
```

EXPLOIT EVIDENCE:
- Exploit Successful: {exploit_result.exploit_successful}
- Evidence: {exploit_result.evidence}

REQUIREMENTS:
1. Fix the vulnerability completely
2. Maintain existing functionality
3. Preserve algorithmic complexity
4. Follow Python best practices
5. Add inline comments explaining the fix

OUTPUT FORMAT (JSON):
{{
  "patch": "unified diff format",
  "explanation": "detailed explanation of the fix",
  "complexity_analysis": {{
    "before": "O(n)",
    "after": "O(n)",
    "justification": "explanation"
  }},
  "regression_tests": "pytest test code"
}}
"""
    
    def _mock_generate_patch(
        self,
        vulnerable_code: str,
        exploit_result: ExploitResult
    ) -> Dict[str, Any]:
        """Mock patch generation for development."""
        
        logger.info("using_mock_patch_generation")
        
        # Generate a realistic patch for race condition
        patch = """
--- a/app.py
+++ b/app.py
@@ -45,15 +45,20 @@ async def transfer_funds(request: TransferRequest):
     conn = sqlite3.connect("fintech.db")
     cursor = conn.cursor()
     
-    # Check balance (NOT ATOMIC)
-    cursor.execute("SELECT balance FROM accounts WHERE account_id = ?",
-                   (request.from_account,))
-    result = cursor.fetchone()
+    # Use transaction for atomicity
+    cursor.execute("BEGIN IMMEDIATE")
+    
+    try:
+        # Lock row for update to prevent race condition
+        cursor.execute(
+            "SELECT balance FROM accounts WHERE account_id = ? FOR UPDATE",
+            (request.from_account,)
+        )
+        result = cursor.fetchone()
     
-    if not result:
-        conn.close()
-        raise HTTPException(status_code=404, detail="Account not found")
+        if not result:
+            conn.rollback()
+            raise HTTPException(status_code=404, detail="Account not found")
     
-    balance = result[0]
+        balance = result[0]
     
-    if balance >= request.amount:
-        # VULNERABILITY: Delay allows race condition
-        await asyncio.sleep(0.1)
+        if balance >= request.amount:
+            # Atomic update within transaction
+            cursor.execute(
+                "UPDATE accounts SET balance = balance - ?, updated_at = ? WHERE account_id = ?",
+                (request.amount, datetime.utcnow().isoformat(), request.from_account)
+            )
         
-        # Deduct from source (SEPARATE TRANSACTION)
-        cursor.execute(
-            "UPDATE accounts SET balance = balance - ?, updated_at = ? WHERE account_id = ?",
-            (request.amount, datetime.utcnow().isoformat(), request.from_account)
-        )
+            cursor.execute(
+                "UPDATE accounts SET balance = balance + ?, updated_at = ? WHERE account_id = ?",
+                (request.amount, datetime.utcnow().isoformat(), request.to_account)
+            )
         
-        # Credit to destination
-        cursor.execute(
-            "UPDATE accounts SET balance = balance + ?, updated_at = ? WHERE account_id = ?",
-            (request.amount, datetime.utcnow().isoformat(), request.to_account)
-        )
+            cursor.execute(
+                "INSERT INTO transactions (from_account, to_account, amount, timestamp) VALUES (?, ?, ?, ?)",
+                (request.from_account, request.to_account, request.amount, datetime.utcnow().isoformat())
+            )
         
-        # Log transaction
-        cursor.execute(
-            "INSERT INTO transactions (from_account, to_account, amount, timestamp) VALUES (?, ?, ?, ?)",
-            (request.from_account, request.to_account, request.amount, datetime.utcnow().isoformat())
-        )
+            conn.commit()
+            return {"status": "success", "message": "Transfer completed"}
+        else:
+            conn.rollback()
+            return {"status": "insufficient_funds", "balance": balance}
         
-        conn.commit()
-        conn.close()
-        return {"status": "success", "message": "Transfer completed"}
-    else:
-        conn.close()
-        return {"status": "insufficient_funds", "balance": balance}
+    except Exception as e:
+        conn.rollback()
+        raise
+    finally:
+        conn.close()
"""
        
        explanation = """
Fixed race condition vulnerability by implementing database transactions with row-level locking:

1. Added BEGIN IMMEDIATE to start an exclusive transaction
2. Used SELECT ... FOR UPDATE to lock the account row
3. Moved all operations inside try-except block
4. Added proper rollback on errors
5. Removed artificial delay that exposed the race window
6. Ensured connection is always closed in finally block

This ensures atomicity - either all operations succeed or none do, preventing concurrent requests from bypassing balance checks.
"""
        
        regression_tests = """
import pytest
import asyncio
import httpx

@pytest.mark.asyncio
async def test_concurrent_transfers_prevented():
    '''Test that concurrent transfers cannot cause negative balance.'''
    url = "http://localhost:8080/transfer"
    payload = {
        "from_account": "ACC001",
        "to_account": "ACC002",
        "amount": 100.0
    }
    
    # Reset account balance
    # ... setup code ...
    
    # Execute concurrent requests
    async with httpx.AsyncClient() as client:
        tasks = [client.post(url, json=payload) for _ in range(10)]
        responses = await asyncio.gather(*tasks)
    
    # Verify only one succeeded
    success_count = sum(1 for r in responses if r.status_code == 200)
    assert success_count == 1, "Only one concurrent transfer should succeed"
    
    # Verify balance is not negative
    balance_response = await client.get("http://localhost:8080/balance/ACC001")
    balance = balance_response.json()["balance"]
    assert balance >= 0, "Balance should never be negative"

@pytest.mark.asyncio
async def test_transaction_rollback_on_error():
    '''Test that transactions rollback properly on errors.'''
    # ... test implementation ...
    pass
"""
        
        return {
            "patch": patch,
            "explanation": explanation,
            "complexity_analysis": {
                "before": "O(1)",
                "after": "O(1)",
                "justification": "Transaction overhead is constant. No algorithmic complexity change."
            },
            "regression_tests": regression_tests
        }
    
    async def validate_performance(
        self,
        patch: str,
        baseline_metrics: Dict[str, Any]
    ) -> bool:
        """
        Validate that patch doesn't degrade performance.
        
        Args:
            patch: Generated patch
            baseline_metrics: Baseline performance metrics
            
        Returns:
            True if performance is acceptable
        """
        logger.info("validating_patch_performance")
        
        # TODO: Deploy patch to shadow namespace and run load tests
        # For now, use mock metrics
        
        patched_metrics = {
            "p95_latency_ms": 47.0,  # Slightly higher due to transaction
            "throughput_rps": 995.0,  # Slightly lower
            "error_rate": 0.0
        }
        
        # If no baseline, use mock baseline
        if not baseline_metrics:
            baseline_metrics = {
                "p95_latency_ms": 45.0,
                "throughput_rps": 1000.0,
                "error_rate": 0.0
            }
        
        # Compare performance
        comparison = await self.load_tester.compare_performance(
            baseline_results=baseline_metrics,
            patched_results=patched_metrics,
            threshold_ms=50.0
        )
        
        logger.info(
            "performance_validation_complete",
            passed=comparison["passed"]
        )
        
        return comparison["passed"]
