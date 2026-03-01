"""Hardware detection and capability management."""

import platform
import subprocess
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


class HardwareDetector:
    """Detects available hardware and provides capability information."""
    
    def __init__(self):
        """Initialize hardware detector."""
        self.capabilities = self._detect_capabilities()
        logger.info("hardware_detected", capabilities=self.capabilities)
    
    def _detect_capabilities(self) -> Dict[str, Any]:
        """Detect available hardware capabilities."""
        caps = {
            "cpu": self._detect_cpu(),
            "gpu": self._detect_gpu(),
            "npu": self._detect_npu(),
            "memory_gb": self._detect_memory(),
            "platform": platform.system()
        }
        return caps
    
    def _detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU information."""
        return {
            "vendor": platform.processor() or "Unknown",
            "cores": self._get_cpu_count(),
            "available": True
        }
    
    def _get_cpu_count(self) -> int:
        """Get CPU core count."""
        try:
            import os
            return os.cpu_count() or 4
        except:
            return 4
    
    def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU availability and type."""
        gpu_info = {
            "available": False,
            "vendor": None,
            "device": None,
            "backend": None
        }
        
        # Try AMD ROCm
        if self._check_rocm():
            gpu_info.update({
                "available": True,
                "vendor": "AMD",
                "backend": "ROCm",
                "optimized": True
            })
            return gpu_info
        
        # Try NVIDIA CUDA
        if self._check_cuda():
            gpu_info.update({
                "available": True,
                "vendor": "NVIDIA",
                "backend": "CUDA",
                "optimized": False  # Works but not optimized
            })
            return gpu_info
        
        # Try Intel
        if self._check_intel_gpu():
            gpu_info.update({
                "available": True,
                "vendor": "Intel",
                "backend": "OpenCL",
                "optimized": False
            })
            return gpu_info
        
        # CPU fallback
        gpu_info.update({
            "available": True,
            "vendor": "CPU",
            "backend": "CPU",
            "optimized": False,
            "note": "Using CPU fallback for GPU operations"
        })
        
        return gpu_info
    
    def _check_rocm(self) -> bool:
        """Check if AMD ROCm is available."""
        try:
            import torch
            return torch.cuda.is_available() and "AMD" in torch.cuda.get_device_name(0)
        except:
            pass
        
        try:
            result = subprocess.run(
                ["rocm-smi"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_cuda(self) -> bool:
        """Check if NVIDIA CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available() and "NVIDIA" in torch.cuda.get_device_name(0)
        except:
            pass
        
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_intel_gpu(self) -> bool:
        """Check if Intel GPU is available."""
        try:
            # Check for Intel GPU on Windows
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    timeout=2,
                    text=True
                )
                return "Intel" in result.stdout
        except:
            pass
        return False
    
    def _detect_npu(self) -> Dict[str, Any]:
        """Detect NPU availability."""
        npu_info = {
            "available": False,
            "vendor": None,
            "device": None
        }
        
        # Check for AMD Ryzen AI NPU
        if self._check_amd_npu():
            npu_info.update({
                "available": True,
                "vendor": "AMD",
                "device": "Ryzen AI",
                "optimized": True
            })
            return npu_info
        
        # Check for Intel NPU
        if self._check_intel_npu():
            npu_info.update({
                "available": True,
                "vendor": "Intel",
                "device": "AI Boost",
                "optimized": False
            })
            return npu_info
        
        # CPU fallback for inference
        npu_info.update({
            "available": True,
            "vendor": "CPU",
            "device": "CPU Inference",
            "optimized": False,
            "note": "Using CPU fallback for NPU operations"
        })
        
        return npu_info
    
    def _check_amd_npu(self) -> bool:
        """Check for AMD Ryzen AI NPU."""
        try:
            # Check for ONNX Runtime with Vitis AI EP
            import onnxruntime as ort
            providers = ort.get_available_providers()
            return "VitisAIExecutionProvider" in providers
        except:
            pass
        
        try:
            # Check for xdna-util (AMD NPU utility)
            result = subprocess.run(
                ["xdna-util", "status"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_intel_npu(self) -> bool:
        """Check for Intel NPU."""
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            return "OpenVINOExecutionProvider" in providers
        except:
            return False
    
    def _detect_memory(self) -> float:
        """Detect available system memory in GB."""
        try:
            import psutil
            return psutil.virtual_memory().total / (1024 ** 3)
        except:
            return 8.0  # Default assumption
    
    def get_optimal_backend(self, operation: str) -> str:
        """
        Get optimal backend for a given operation.
        
        Args:
            operation: Operation type ('inference', 'parallel', 'patch')
            
        Returns:
            Backend name
        """
        if operation == "inference":
            if self.capabilities["npu"]["available"] and self.capabilities["npu"].get("optimized"):
                return "npu"
            return "cpu"
        
        elif operation == "parallel":
            if self.capabilities["gpu"]["available"]:
                return self.capabilities["gpu"]["backend"].lower()
            return "cpu"
        
        elif operation == "patch":
            return "llm"  # Always use LLM API
        
        return "cpu"
    
    def get_concurrency_limit(self) -> int:
        """Get optimal concurrency limit based on hardware."""
        if self.capabilities["gpu"]["available"] and self.capabilities["gpu"].get("optimized"):
            return 10000  # High concurrency with AMD GPU
        elif self.capabilities["gpu"]["available"]:
            return 5000   # Medium concurrency with other GPUs
        else:
            return 1000   # Lower concurrency with CPU
    
    def supports_hardware_acceleration(self) -> bool:
        """Check if any hardware acceleration is available."""
        return (
            self.capabilities["gpu"]["available"] or
            self.capabilities["npu"]["available"]
        )
    
    def get_performance_profile(self) -> Dict[str, Any]:
        """Get expected performance profile based on hardware."""
        profile = {
            "inference_latency_ms": 2000,  # CPU baseline
            "parallel_rps": 1000,           # CPU baseline
            "memory_limit_gb": self.capabilities["memory_gb"]
        }
        
        # Adjust for NPU
        if self.capabilities["npu"].get("optimized"):
            profile["inference_latency_ms"] = 450  # AMD NPU optimized
        
        # Adjust for GPU
        if self.capabilities["gpu"].get("optimized"):
            profile["parallel_rps"] = 10000  # AMD GPU optimized
        elif self.capabilities["gpu"]["available"]:
            profile["parallel_rps"] = 5000   # Other GPU
        
        return profile
    
    def print_capabilities(self):
        """Print detected capabilities."""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Hardware Capabilities")
        
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # CPU
        cpu = self.capabilities["cpu"]
        table.add_row(
            "CPU",
            "✅ Available",
            f"{cpu['vendor']} ({cpu['cores']} cores)"
        )
        
        # GPU
        gpu = self.capabilities["gpu"]
        status = "✅ Available" if gpu["available"] else "❌ Not Available"
        optimized = " (Optimized)" if gpu.get("optimized") else " (Fallback)"
        details = f"{gpu.get('vendor', 'N/A')} - {gpu.get('backend', 'N/A')}{optimized if gpu['available'] else ''}"
        table.add_row("GPU", status, details)
        
        # NPU
        npu = self.capabilities["npu"]
        status = "✅ Available" if npu["available"] else "❌ Not Available"
        optimized = " (Optimized)" if npu.get("optimized") else " (Fallback)"
        details = f"{npu.get('vendor', 'N/A')} - {npu.get('device', 'N/A')}{optimized if npu['available'] else ''}"
        table.add_row("NPU", status, details)
        
        # Memory
        table.add_row(
            "Memory",
            "✅ Available",
            f"{self.capabilities['memory_gb']:.1f} GB"
        )
        
        console.print(table)
        
        # Performance profile
        profile = self.get_performance_profile()
        console.print(f"\n[bold]Expected Performance:[/bold]")
        console.print(f"  Inference Latency: {profile['inference_latency_ms']}ms")
        console.print(f"  Parallel Throughput: {profile['parallel_rps']} req/s")
        console.print(f"  Concurrency Limit: {self.get_concurrency_limit()}")


# Global hardware detector instance
_detector: Optional[HardwareDetector] = None


def get_hardware_detector() -> HardwareDetector:
    """Get global hardware detector instance."""
    global _detector
    if _detector is None:
        _detector = HardwareDetector()
    return _detector
