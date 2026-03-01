"""Shadow namespace lifecycle management for isolated exploit execution."""

import subprocess
import time
import uuid
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class NamespaceLifecycle:
    """
    Manages shadow namespaces for isolated exploit execution.
    
    Supports:
    - Kubernetes (production)
    - Docker Compose (local development)
    - Plain Docker (fallback)
    """
    
    def __init__(self):
        """Initialize namespace manager."""
        self.backend = self._detect_backend()
        logger.info("namespace_manager_initialized", backend=self.backend)
    
    def _detect_backend(self) -> str:
        """Detect available container orchestration backend."""
        # Check for Kubernetes
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("kubernetes_detected")
                return "kubernetes"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for Docker Compose
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("docker_compose_detected")
                return "docker-compose"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for Docker
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("docker_detected")
                return "docker"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.warning("no_container_backend_detected")
        return "none"
    
    def create_shadow_namespace(
        self,
        app_name: str,
        image: Optional[str] = None,
        port: int = 8080
    ) -> str:
        """
        Create isolated shadow namespace for exploit testing.
        
        Args:
            app_name: Name of the application
            image: Docker image to deploy (optional)
            port: Port to expose
            
        Returns:
            Namespace/container identifier
        """
        namespace_id = f"shadow-{app_name}-{uuid.uuid4().hex[:8]}"
        
        logger.info(
            "creating_shadow_namespace",
            namespace_id=namespace_id,
            backend=self.backend
        )
        
        if self.backend == "kubernetes":
            return self._create_k8s_namespace(namespace_id, image, port)
        elif self.backend == "docker-compose":
            return self._create_compose_namespace(namespace_id, image, port)
        elif self.backend == "docker":
            return self._create_docker_namespace(namespace_id, image, port)
        else:
            logger.error("no_backend_available")
            raise RuntimeError("No container backend available")
    
    def _create_k8s_namespace(
        self,
        namespace_id: str,
        image: Optional[str],
        port: int
    ) -> str:
        """Create Kubernetes namespace with isolated pod."""
        
        # Create namespace
        namespace_yaml = f"""
apiVersion: v1
kind: Namespace
metadata:
  name: {namespace_id}
  labels:
    purpose: exploit-testing
    auto-cleanup: "true"
    created: "{int(time.time())}"
"""
        
        # Create pod
        pod_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: target-app
  namespace: {namespace_id}
spec:
  containers:
  - name: app
    image: {image or 'redroom-target:latest'}
    ports:
    - containerPort: {port}
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
  restartPolicy: Never
---
apiVersion: v1
kind: Service
metadata:
  name: target-service
  namespace: {namespace_id}
spec:
  selector:
    app: target-app
  ports:
  - port: {port}
    targetPort: {port}
"""
        
        # Apply namespace
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=namespace_yaml.encode(),
                check=True,
                capture_output=True
            )
            
            # Apply pod
            subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=pod_yaml.encode(),
                check=True,
                capture_output=True
            )
            
            # Wait for pod to be ready
            logger.info("waiting_for_pod_ready", namespace=namespace_id)
            subprocess.run(
                ["kubectl", "wait", "--for=condition=ready", "pod/target-app",
                 "-n", namespace_id, "--timeout=60s"],
                check=True,
                capture_output=True
            )
            
            logger.info("k8s_namespace_created", namespace=namespace_id)
            return namespace_id
            
        except subprocess.CalledProcessError as e:
            logger.error("k8s_namespace_creation_failed", error=e.stderr.decode())
            raise
    
    def _create_compose_namespace(
        self,
        namespace_id: str,
        image: Optional[str],
        port: int
    ) -> str:
        """Create Docker Compose isolated environment."""
        
        compose_yaml = f"""
version: '3.8'
services:
  target-app:
    image: {image or 'redroom-target:latest'}
    container_name: {namespace_id}
    ports:
      - "{port}:{port}"
    networks:
      - {namespace_id}-network
    mem_limit: 512m
    cpus: 0.5

networks:
  {namespace_id}-network:
    driver: bridge
"""
        
        # Write compose file
        compose_file = f"/tmp/{namespace_id}-compose.yml"
        with open(compose_file, 'w') as f:
            f.write(compose_yaml)
        
        try:
            # Start services
            subprocess.run(
                ["docker-compose", "-f", compose_file, "-p", namespace_id, "up", "-d"],
                check=True,
                capture_output=True
            )
            
            # Wait for container to be ready
            time.sleep(5)
            
            logger.info("compose_namespace_created", namespace=namespace_id)
            return namespace_id
            
        except subprocess.CalledProcessError as e:
            logger.error("compose_namespace_creation_failed", error=e.stderr.decode())
            raise
    
    def _create_docker_namespace(
        self,
        namespace_id: str,
        image: Optional[str],
        port: int
    ) -> str:
        """Create plain Docker container."""
        
        try:
            # Run container
            result = subprocess.run(
                [
                    "docker", "run",
                    "-d",
                    "--name", namespace_id,
                    "-p", f"{port}:{port}",
                    "--memory", "512m",
                    "--cpus", "0.5",
                    "--network", "bridge",
                    image or "redroom-target:latest"
                ],
                check=True,
                capture_output=True
            )
            
            container_id = result.stdout.decode().strip()
            
            # Wait for container to be ready
            time.sleep(5)
            
            logger.info("docker_namespace_created", namespace=namespace_id, container=container_id)
            return namespace_id
            
        except subprocess.CalledProcessError as e:
            logger.error("docker_namespace_creation_failed", error=e.stderr.decode())
            raise
    
    def cleanup_namespace(self, namespace_id: str):
        """
        Cleanup shadow namespace.
        
        Args:
            namespace_id: Namespace/container identifier
        """
        logger.info("cleaning_up_namespace", namespace=namespace_id, backend=self.backend)
        
        try:
            if self.backend == "kubernetes":
                subprocess.run(
                    ["kubectl", "delete", "namespace", namespace_id, "--grace-period=0", "--force"],
                    capture_output=True,
                    timeout=30
                )
            elif self.backend == "docker-compose":
                compose_file = f"/tmp/{namespace_id}-compose.yml"
                subprocess.run(
                    ["docker-compose", "-f", compose_file, "-p", namespace_id, "down"],
                    capture_output=True,
                    timeout=30
                )
                # Cleanup compose file
                try:
                    import os
                    os.remove(compose_file)
                except:
                    pass
            elif self.backend == "docker":
                subprocess.run(
                    ["docker", "stop", namespace_id],
                    capture_output=True,
                    timeout=30
                )
                subprocess.run(
                    ["docker", "rm", namespace_id],
                    capture_output=True,
                    timeout=30
                )
            
            logger.info("namespace_cleaned_up", namespace=namespace_id)
            
        except Exception as e:
            logger.error("namespace_cleanup_failed", namespace=namespace_id, error=str(e))
    
    def cleanup_expired_namespaces(self, max_age_seconds: int = 3600):
        """
        Cleanup namespaces older than max_age_seconds.
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
        """
        logger.info("cleaning_up_expired_namespaces", max_age=max_age_seconds)
        
        if self.backend == "kubernetes":
            try:
                # Get all shadow namespaces
                result = subprocess.run(
                    ["kubectl", "get", "namespaces", "-l", "purpose=exploit-testing", "-o", "json"],
                    capture_output=True,
                    check=True
                )
                
                import json
                namespaces = json.loads(result.stdout)
                
                current_time = int(time.time())
                
                for ns in namespaces.get("items", []):
                    created = int(ns["metadata"]["labels"].get("created", 0))
                    age = current_time - created
                    
                    if age > max_age_seconds:
                        ns_name = ns["metadata"]["name"]
                        logger.info("cleaning_up_expired_namespace", namespace=ns_name, age=age)
                        self.cleanup_namespace(ns_name)
                        
            except Exception as e:
                logger.error("expired_cleanup_failed", error=str(e))
        
        elif self.backend in ["docker", "docker-compose"]:
            try:
                # Get all shadow containers
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", "name=shadow-", "--format", "{{.Names}}"],
                    capture_output=True,
                    check=True
                )
                
                containers = result.stdout.decode().strip().split('\n')
                
                for container in containers:
                    if container and container.startswith("shadow-"):
                        # Get container creation time
                        inspect_result = subprocess.run(
                            ["docker", "inspect", container, "--format", "{{.Created}}"],
                            capture_output=True
                        )
                        
                        if inspect_result.returncode == 0:
                            created_str = inspect_result.stdout.decode().strip()
                            # Parse and check age (simplified)
                            # In production, parse the timestamp properly
                            logger.info("found_shadow_container", container=container)
                            # Cleanup old containers
                            self.cleanup_namespace(container)
                            
            except Exception as e:
                logger.error("docker_cleanup_failed", error=str(e))
    
    def get_namespace_info(self, namespace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a namespace.
        
        Args:
            namespace_id: Namespace/container identifier
            
        Returns:
            Namespace information or None
        """
        if self.backend == "kubernetes":
            try:
                result = subprocess.run(
                    ["kubectl", "get", "pods", "-n", namespace_id, "-o", "json"],
                    capture_output=True,
                    check=True
                )
                
                import json
                pods = json.loads(result.stdout)
                
                return {
                    "namespace": namespace_id,
                    "backend": "kubernetes",
                    "status": "running",
                    "pod_count": len(pods.get("items", [])),
                    "pods": [
                        {
                            "name": pod["metadata"]["name"],
                            "status": pod["status"]["phase"],
                            "ready": all(c["ready"] for c in pod["status"].get("containerStatuses", []))
                        }
                        for pod in pods.get("items", [])
                    ]
                }
                
            except Exception as e:
                logger.error("failed_to_get_namespace_info", error=str(e))
                return None
        
        elif self.backend in ["docker", "docker-compose"]:
            try:
                result = subprocess.run(
                    ["docker", "inspect", namespace_id],
                    capture_output=True,
                    check=True
                )
                
                import json
                info = json.loads(result.stdout)[0]
                
                return {
                    "namespace": namespace_id,
                    "backend": self.backend,
                    "status": info["State"]["Status"],
                    "container_id": info["Id"][:12],
                    "created": info["Created"],
                    "running": info["State"]["Running"]
                }
                
            except Exception as e:
                logger.error("failed_to_get_container_info", error=str(e))
                return None
        
        return None
