"""Full scan workflow: Deploy → Test → Analyze → Fix."""

import asyncio
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, Any
import structlog

from redroom.agents.scanner.web_scanner import WebScanner
from redroom.agents.saboteur.hypothesis_generator import HypothesisGenerator
from redroom.agents.exploit_lab.exploit_generator import ExploitGenerator
from redroom.agents.surgeon.patch_generator import PatchGenerator
from redroom.utils.hardware_detector import get_hardware_detector

logger = structlog.get_logger()


class FullScanWorkflow:
    """
    Complete workflow: Deploy app → Scan → Analyze → Generate fixes.
    
    Hardware acceleration:
    - NPU: Hypothesis generation
    - GPU: Parallel vulnerability testing (70 tests)
    - CPU: Patch generation
    """
    
    def __init__(self, project_path: str):
        """
        Initialize workflow.
        
        Args:
            project_path: Path to project folder or GitHub repo
        """
        self.project_path = Path(project_path)
        self.hw_detector = get_hardware_detector()
        
        # Initialize agents
        self.hypothesis_gen = HypothesisGenerator(model_path=None)
        self.exploit_gen = ExploitGenerator(gpu_enabled=True)
        self.patch_gen = PatchGenerator(llm_provider="gemini")
        
        logger.info(
            "workflow_initialized",
            project=str(self.project_path),
            hardware=self.hw_detector.get_performance_profile()
        )
    
    async def run(self, port: int = 8080) -> Dict[str, Any]:
        """
        Run complete workflow.
        
        Steps:
        1. Deploy app in Docker
        2. Run 70 vulnerability tests (GPU-accelerated)
        3. Analyze vulnerabilities (NPU-accelerated)
        4. Generate fixes (CPU)
        
        Args:
            port: Port to run the app on
            
        Returns:
            Complete scan results with fixes
        """
        logger.info("starting_full_scan_workflow", port=port)
        
        results = {
            "project_path": str(self.project_path),
            "hardware_used": {},
            "deployment": {},
            "scan_results": {},
            "vulnerabilities": [],
            "fixes": []
        }
        
        # Step 1: Deploy in Docker
        logger.info("step_1_deploying_app_in_docker")
        deployment = await self._deploy_in_docker(port)
        results["deployment"] = deployment
        
        if not deployment["success"]:
            logger.error("deployment_failed", error=deployment.get("error"))
            return results
        
        try:
            # Step 2: Run 70 vulnerability tests (GPU-accelerated)
            logger.info("step_2_running_vulnerability_tests", backend=self.hw_detector.get_optimal_backend("parallel"))
            scan_results = await self._run_vulnerability_tests(f"http://localhost:{port}")
            results["scan_results"] = scan_results
            results["hardware_used"]["scanner"] = self.hw_detector.get_optimal_backend("parallel")
            
            # Step 3: Analyze each vulnerability (NPU-accelerated)
            if scan_results.get("vulnerabilities"):
                logger.info(
                    "step_3_analyzing_vulnerabilities",
                    count=len(scan_results["vulnerabilities"]),
                    backend=self.hw_detector.get_optimal_backend("inference")
                )
                
                for vuln in scan_results["vulnerabilities"]:
                    analysis = await self._analyze_vulnerability(vuln)
                    results["vulnerabilities"].append(analysis)
                
                results["hardware_used"]["analysis"] = self.hw_detector.get_optimal_backend("inference")
            
            # Step 4: Generate fixes (CPU)
            if results["vulnerabilities"]:
                logger.info("step_4_generating_fixes", count=len(results["vulnerabilities"]))
                
                for vuln_analysis in results["vulnerabilities"]:
                    if vuln_analysis.get("hypothesis"):
                        fix = await self._generate_fix(vuln_analysis)
                        results["fixes"].append(fix)
                
                results["hardware_used"]["patching"] = "cpu"
            
            logger.info(
                "workflow_complete",
                vulnerabilities_found=len(results["vulnerabilities"]),
                fixes_generated=len(results["fixes"])
            )
            
        finally:
            # Cleanup: Stop Docker container
            logger.info("cleaning_up_docker_container")
            await self._cleanup_docker(deployment.get("container_id"))
        
        return results
    
    async def _deploy_in_docker(self, port: int) -> Dict[str, Any]:
        """
        Deploy application in Docker container.
        
        Looks for:
        1. Dockerfile in project root
        2. docker-compose.yml
        3. Auto-detects framework (Flask, FastAPI, Express, etc.)
        
        Args:
            port: Port to expose
            
        Returns:
            Deployment info
        """
        logger.info("deploying_in_docker", project=str(self.project_path), port=port)
        
        # Check for Dockerfile
        dockerfile = self.project_path / "Dockerfile"
        docker_compose = self.project_path / "docker-compose.yml"
        
        if dockerfile.exists():
            # Build and run from Dockerfile
            return await self._deploy_from_dockerfile(dockerfile, port)
        
        elif docker_compose.exists():
            # Use docker-compose
            return await self._deploy_from_compose(docker_compose, port)
        
        else:
            # Auto-detect framework and create Dockerfile
            return await self._auto_deploy(port)
    
    async def _deploy_from_dockerfile(self, dockerfile: Path, port: int) -> Dict[str, Any]:
        """Deploy from existing Dockerfile."""
        try:
            # Build image
            build_cmd = [
                "docker", "build",
                "-t", "redroom-target",
                "-f", str(dockerfile),
                str(self.project_path)
            ]
            
            logger.info("building_docker_image", cmd=" ".join(build_cmd))
            build_result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if build_result.returncode != 0:
                return {
                    "success": False,
                    "error": build_result.stderr
                }
            
            # Run container
            run_cmd = [
                "docker", "run",
                "-d",  # Detached
                "-p", f"{port}:8080",  # Port mapping
                "--name", "redroom-target-container",
                "redroom-target"
            ]
            
            logger.info("starting_container", cmd=" ".join(run_cmd))
            run_result = subprocess.run(run_cmd, capture_output=True, text=True)
            
            if run_result.returncode != 0:
                return {
                    "success": False,
                    "error": run_result.stderr
                }
            
            container_id = run_result.stdout.strip()
            
            # Wait for app to start
            await asyncio.sleep(5)
            
            return {
                "success": True,
                "container_id": container_id,
                "method": "dockerfile",
                "url": f"http://localhost:{port}"
            }
            
        except Exception as e:
            logger.error("deployment_failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _deploy_from_compose(self, compose_file: Path, port: int) -> Dict[str, Any]:
        """Deploy using docker-compose."""
        try:
            cmd = ["docker-compose", "-f", str(compose_file), "up", "-d"]
            
            logger.info("starting_docker_compose", cmd=" ".join(cmd))
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.project_path))
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            # Wait for services to start
            await asyncio.sleep(10)
            
            return {
                "success": True,
                "method": "docker-compose",
                "url": f"http://localhost:{port}"
            }
            
        except Exception as e:
            logger.error("compose_deployment_failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _auto_deploy(self, port: int) -> Dict[str, Any]:
        """Auto-detect framework and deploy."""
        logger.info("auto_detecting_framework")
        
        # Check for common files
        if (self.project_path / "app.py").exists():
            framework = "flask"
        elif (self.project_path / "main.py").exists():
            framework = "fastapi"
        elif (self.project_path / "package.json").exists():
            framework = "node"
        else:
            return {
                "success": False,
                "error": "Could not auto-detect framework. Please provide Dockerfile."
            }
        
        logger.info("framework_detected", framework=framework)
        
        # Create temporary Dockerfile
        dockerfile_content = self._generate_dockerfile(framework)
        temp_dockerfile = self.project_path / "Dockerfile.redroom"
        temp_dockerfile.write_text(dockerfile_content)
        
        try:
            result = await self._deploy_from_dockerfile(temp_dockerfile, port)
            return result
        finally:
            # Cleanup temp Dockerfile
            if temp_dockerfile.exists():
                temp_dockerfile.unlink()
    
    def _generate_dockerfile(self, framework: str) -> str:
        """Generate Dockerfile for detected framework."""
        if framework == "flask":
            return """FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
"""
        elif framework == "fastapi":
            return """FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
"""
        elif framework == "node":
            return """FROM node:18-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8080
CMD ["npm", "start"]
"""
        else:
            return ""
    
    async def _run_vulnerability_tests(self, url: str) -> Dict[str, Any]:
        """
        Run 70 vulnerability tests (GPU-accelerated).
        
        Uses GPU for parallel execution when available.
        """
        logger.info("running_vulnerability_tests", url=url, tests=70)
        
        scanner = WebScanner(url)
        results = await scanner.scan()
        
        logger.info(
            "vulnerability_tests_complete",
            vulnerabilities_found=results["vulnerabilities_found"],
            endpoints_scanned=results["endpoints_found"]
        )
        
        return results
    
    async def _analyze_vulnerability(self, vuln: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze vulnerability using NPU-accelerated inference.
        
        Generates hypothesis about the vulnerability.
        """
        logger.info("analyzing_vulnerability", type=vuln["type"], endpoint=vuln["endpoint"])
        
        # Create a mock diff for the vulnerability
        # In production, this would extract actual code from the repo
        mock_diff = f"""
diff --git a/{vuln['endpoint']}.py b/{vuln['endpoint']}.py
--- a/{vuln['endpoint']}.py
+++ b/{vuln['endpoint']}.py
@@ -1,5 +1,5 @@
 # Vulnerability: {vuln['type']}
 # Endpoint: {vuln['endpoint']}
 # Severity: {vuln['severity']}
"""
        
        hypothesis = await self.hypothesis_gen.analyze_diff(mock_diff)
        
        return {
            "vulnerability": vuln,
            "hypothesis": hypothesis.dict() if hypothesis else None
        }
    
    async def _generate_fix(self, vuln_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fix using CPU.
        
        Creates patch for the vulnerability.
        """
        vuln = vuln_analysis["vulnerability"]
        hypothesis = vuln_analysis.get("hypothesis")
        
        logger.info("generating_fix", type=vuln["type"], endpoint=vuln["endpoint"])
        
        # Mock exploit result for patch generation
        from redroom.models.schemas import ExploitResult
        mock_exploit = ExploitResult(
            exploit_successful=True,
            evidence={"summary": {"exploit_successful": True}},
            reproducibility_score=1.0,
            execution_time_ms=100,
            shadow_namespace="local"
        )
        
        # Generate patch
        patch_result = await self.patch_gen.generate_patch(
            vulnerable_code=f"# Vulnerable code at {vuln['endpoint']}",
            exploit_result=mock_exploit
        )
        
        return {
            "vulnerability": vuln,
            "patch": patch_result.dict()
        }
    
    async def _cleanup_docker(self, container_id: Optional[str] = None):
        """Stop and remove Docker container."""
        if container_id:
            try:
                subprocess.run(["docker", "stop", container_id], capture_output=True)
                subprocess.run(["docker", "rm", container_id], capture_output=True)
                logger.info("docker_container_cleaned_up", container_id=container_id)
            except Exception as e:
                logger.error("cleanup_failed", error=str(e))
        
        # Also try to stop by name
        try:
            subprocess.run(["docker", "stop", "redroom-target-container"], capture_output=True)
            subprocess.run(["docker", "rm", "redroom-target-container"], capture_output=True)
        except:
            pass
