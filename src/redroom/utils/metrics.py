"""Metrics collection and reporting."""

from typing import Dict, Any
from datetime import datetime
import structlog

logger = structlog.get_logger()


class MetricsCollector:
    """Collects and reports system metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {}
        logger.info("metrics_collector_initialized")
    
    def record_execution(
        self,
        execution_id: str,
        status: str,
        duration_ms: float
    ):
        """Record execution metrics."""
        if "executions" not in self.metrics:
            self.metrics["executions"] = []
        
        self.metrics["executions"].append({
            "execution_id": execution_id,
            "status": status,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(
            "execution_recorded",
            execution_id=execution_id,
            status=status,
            duration_ms=duration_ms
        )
    
    def record_agent_performance(
        self,
        agent_name: str,
        operation: str,
        duration_ms: float,
        success: bool
    ):
        """Record agent performance metrics."""
        key = f"agent_{agent_name}"
        
        if key not in self.metrics:
            self.metrics[key] = []
        
        self.metrics[key].append({
            "operation": operation,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        summary = {
            "total_executions": len(self.metrics.get("executions", [])),
            "successful_executions": sum(
                1 for e in self.metrics.get("executions", [])
                if e["status"] == "completed"
            ),
            "avg_execution_time_ms": 0.0,
            "agents": {}
        }
        
        # Calculate average execution time
        executions = self.metrics.get("executions", [])
        if executions:
            summary["avg_execution_time_ms"] = sum(
                e["duration_ms"] for e in executions
            ) / len(executions)
        
        # Agent summaries
        for key, values in self.metrics.items():
            if key.startswith("agent_"):
                agent_name = key.replace("agent_", "")
                summary["agents"][agent_name] = {
                    "total_operations": len(values),
                    "successful_operations": sum(1 for v in values if v["success"]),
                    "avg_duration_ms": sum(v["duration_ms"] for v in values) / len(values) if values else 0
                }
        
        return summary
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        summary = self.get_summary()
        
        metrics = f"""
# HELP redroom_executions_total Total number of executions
# TYPE redroom_executions_total counter
redroom_executions_total {summary['total_executions']}

# HELP redroom_executions_successful Successful executions
# TYPE redroom_executions_successful counter
redroom_executions_successful {summary['successful_executions']}

# HELP redroom_execution_duration_ms Average execution duration
# TYPE redroom_execution_duration_ms gauge
redroom_execution_duration_ms {summary['avg_execution_time_ms']}
"""
        
        for agent_name, agent_metrics in summary["agents"].items():
            metrics += f"""
# HELP redroom_agent_{agent_name}_operations_total Total operations
# TYPE redroom_agent_{agent_name}_operations_total counter
redroom_agent_{agent_name}_operations_total {agent_metrics['total_operations']}

# HELP redroom_agent_{agent_name}_duration_ms Average duration
# TYPE redroom_agent_{agent_name}_duration_ms gauge
redroom_agent_{agent_name}_duration_ms {agent_metrics['avg_duration_ms']}
"""
        
        return metrics
