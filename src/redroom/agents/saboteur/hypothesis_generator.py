"""Hypothesis generation for vulnerability detection."""

import json
from typing import Dict, Any, Optional, List
import structlog
from redroom.models.schemas import Hypothesis, VulnerabilityType
from redroom.agents.saboteur.npu_inference import NPUInference
from redroom.agents.saboteur.diff_analyzer import DiffAnalyzer
from redroom.agents.saboteur.contract_parser import ContractParser

logger = structlog.get_logger()


class HypothesisGenerator:
    """Generates attack hypotheses from code analysis."""
    
    def __init__(self, model_path: str):
        """Initialize with NPU model path."""
        self.model_path = model_path
        self.npu = NPUInference(model_path)
        self.diff_analyzer = DiffAnalyzer()
        self.contract_parser = ContractParser()
        
        logger.info("hypothesis_generator_initialized", model_path=model_path)
    
    async def analyze_diff(
        self,
        git_diff: str,
        openapi_spec: Optional[Dict[str, Any]] = None,
        security_contracts: Optional[Dict[str, Any]] = None
    ) -> Optional[Hypothesis]:
        """
        Analyze git diff and generate vulnerability hypothesis.
        
        Args:
            git_diff: Git diff content
            openapi_spec: OpenAPI specification
            security_contracts: Security contract definitions
            
        Returns:
            Hypothesis if vulnerability detected, None otherwise
        """
        logger.info("analyzing_diff", diff_size=len(git_diff))
        
        # Parse diff
        changes = self.diff_analyzer.parse_diff(git_diff)
        
        # Identify security patterns
        patterns = self.diff_analyzer.identify_security_patterns(changes)
        
        # Calculate risk score
        risk_score = self.diff_analyzer.calculate_risk_score(changes, patterns)
        
        logger.info(
            "diff_analysis_complete",
            patterns=patterns,
            risk_score=risk_score
        )
        
        # If no patterns detected, return None
        if not patterns:
            logger.info("no_security_patterns_detected")
            return None
        
        # Parse contracts if provided
        contracts = []
        if security_contracts:
            contracts = self.contract_parser.parse_security_contracts(security_contracts)
        
        # Build prompt for NPU
        prompt = self._build_analysis_prompt(
            changes=changes,
            patterns=patterns,
            contracts=contracts,
            openapi_spec=openapi_spec
        )
        
        # Generate hypothesis using NPU
        response = self.npu.generate(prompt)
        
        # Parse response
        try:
            hypothesis_data = json.loads(response)
            
            # If no vulnerability detected
            if not hypothesis_data.get("vulnerability_type"):
                return None
            
            # Create Hypothesis object
            hypothesis = Hypothesis(
                vulnerability_type=VulnerabilityType(hypothesis_data["vulnerability_type"]),
                confidence_score=hypothesis_data["confidence_score"],
                affected_endpoints=hypothesis_data["affected_endpoints"],
                invariant_break=hypothesis_data["invariant_break"],
                attack_hypothesis=hypothesis_data["attack_hypothesis"]
            )
            
            logger.info(
                "hypothesis_generated",
                vuln_type=hypothesis.vulnerability_type,
                confidence=hypothesis.confidence_score
            )
            
            return hypothesis
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error("failed_to_parse_hypothesis", error=str(e))
            return None
    
    def _build_analysis_prompt(
        self,
        changes: Dict[str, Any],
        patterns: List[str],
        contracts: List[Dict[str, Any]],
        openapi_spec: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for NPU analysis."""
        
        prompt = f"""Analyze this code change for security vulnerabilities:

ADDED CODE:
{chr(10).join(changes['added'][:20])}

REMOVED CODE:
{chr(10).join(changes['removed'][:10])}

CONTEXT (surrounding code):
{chr(10).join(changes['context'][:30])}

DETECTED PATTERNS:
{', '.join(patterns)}

"""
        
        if contracts:
            prompt += f"""
SECURITY CONTRACTS:
{json.dumps(contracts, indent=2)}
"""
        
        if openapi_spec:
            prompt += f"""
API SPECIFICATION:
{json.dumps(openapi_spec.get('paths', {}), indent=2)[:500]}  # Limited
"""
        
        prompt += """
Analyze the code and output JSON with this structure:
{
  "vulnerability_type": "race_condition|auth_bypass|injection|logic_flaw|crypto_weakness|timing_attack",
  "confidence_score": 0.0-1.0,
  "affected_endpoints": ["list of endpoints"],
  "invariant_break": {
    "expected_behavior": "description",
    "actual_behavior": "description",
    "contract_violation": "contract name"
  },
  "attack_hypothesis": {
    "method": "attack method",
    "payload": {},
    "timing_requirements": {},
    "expected_outcome": "description"
  }
}

If no vulnerability is found, return {"vulnerability_type": null, "confidence_score": 0.0}
"""
        
        return prompt
