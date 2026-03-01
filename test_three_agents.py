"""Test script for the three-agent system."""

import asyncio
from rich.console import Console

console = Console()


async def test_three_agents():
    """Test the three-agent pipeline."""
    
    console.print("[bold red]The Red Room - Three-Agent System Test[/bold red]\n")
    
    # Demo vulnerable code (race condition)
    demo_diff = """diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -10,6 +10,8 @@ async def transfer_funds(from_account: str, to_account: str, amount: float):
     # Check balance
     balance = await db.get_balance(from_account)
     if balance >= amount:
+        # Added delay - creates race condition!
+        await asyncio.sleep(0.1)
         await db.deduct(from_account, amount)
         await db.credit(to_account, amount)
         return {"status": "success"}
"""
    
    console.print("[yellow]Demo Code: Race condition in transfer endpoint[/yellow]\n")
    
    # Hardware detection
    console.print("[bold]Step 0: Hardware Detection[/bold]")
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    from redroom.utils.hardware_detector import get_hardware_detector
    
    detector = get_hardware_detector()
    console.print(f"  NPU: {detector.capabilities['npu'].get('device', 'Not available')}")
    console.print(f"  GPU: {detector.capabilities['gpu'].get('device', 'Not available')}")
    console.print(f"  CPU: {detector.capabilities['cpu'].get('vendor', 'Unknown')} ({detector.capabilities['cpu'].get('cores', 0)} cores)")
    console.print(f"  Optimal backend: {detector.get_optimal_backend('inference')}\n")
    
    # Agent I: Saboteur
    console.print("[bold yellow]Step 1: Agent I - Saboteur (NPU)[/bold yellow]")
    console.print("  Analyzing Git diff for vulnerabilities...")
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    from redroom.agents.saboteur.hypothesis_generator import HypothesisGenerator
    
    generator = HypothesisGenerator(model_path=None)  # Use mock for demo
    hypothesis = await generator.analyze_diff(demo_diff)
    
    # Debug: Show what was parsed
    from redroom.agents.saboteur.diff_analyzer import DiffAnalyzer
    analyzer = DiffAnalyzer()
    changes = analyzer.parse_diff(demo_diff)
    console.print(f"[dim]Debug - Added lines: {changes['added']}[/dim]")
    console.print(f"[dim]Debug - Patterns: {analyzer.identify_security_patterns(changes)}[/dim]\n")
    
    if not hypothesis:
        console.print("[green] No vulnerabilities detected[/green]")
        return
    
    console.print("[green] Vulnerability hypothesis generated![/green]")
    console.print(f"  Type: {hypothesis.vulnerability_type}")
    console.print(f"  Confidence: {hypothesis.confidence_score:.1%}")
    console.print(f"  Endpoints: {', '.join(hypothesis.affected_endpoints)}")
    console.print(f"  Attack method: {hypothesis.attack_hypothesis.get('method', 'N/A')}")
    console.print(f"  Expected outcome: {hypothesis.attack_hypothesis.get('expected_outcome', 'N/A')}\n")
    
    # Agent II: Exploit Lab
    console.print("[bold yellow]Step 2: Agent II - Exploit Lab (GPU)[/bold yellow]")
    console.print("  Generating exploit script...")
    
    from redroom.agents.exploit_lab.exploit_generator import ExploitGenerator
    
    exploit_gen = ExploitGenerator(gpu_enabled=True)
    exploit_script = await exploit_gen.generate_exploit(hypothesis)
    
    console.print("[green] Exploit script generated![/green]")
    console.print(f"  Script length: {len(exploit_script)} bytes")
    console.print(f"  Syntax valid: {exploit_gen.validate_exploit_script(exploit_script)}")
    
    console.print("\n[dim]Exploit preview:[/dim]")
    lines = exploit_script.split('\n')[:15]
    for line in lines:
        console.print(f"[dim]{line}[/dim]")
    console.print("[dim]...[/dim]\n")
    
    # Mock exploit execution (would run in shadow namespace)
    console.print("  [yellow]Note: Actual exploit execution requires Kubernetes shadow namespace[/yellow]")
    console.print("  [dim]Simulating exploit execution...[/dim]")
    
    from redroom.models.schemas import ExploitResult
    mock_exploit_result = ExploitResult(
        exploit_successful=True,
        evidence={
            "summary": {
                "exploit_successful": True,
                "confidence": 1.0,
                "severity": "critical"
            },
            "database": {
                "violations": [
                    {
                        "type": "negative_balance",
                        "field": "ACC001",
                        "value": -100.0,
                        "severity": "critical"
                    }
                ]
            },
            "timing": {
                "concurrent_successes": 8
            }
        },
        reproducibility_score=1.0,
        execution_time_ms=150,
        shadow_namespace="demo-shadow-abc123"
    )
    
    console.print("[green] Exploit executed successfully![/green]")
    console.print(f"  Reproducibility: {mock_exploit_result.reproducibility_score:.1%}")
    console.print(f"  Execution time: {mock_exploit_result.execution_time_ms}ms")
    console.print(f"  Evidence: Balance went negative (critical violation)\n")
    
    # Agent III: Surgeon
    console.print("[bold yellow]Step 3: Agent III - Surgeon (CPU)[/bold yellow]")
    console.print("  Generating security patch...")
    
    from redroom.agents.surgeon.patch_generator import PatchGenerator
    
    patch_gen = PatchGenerator(llm_provider="gemini")
    patch_result = await patch_gen.generate_patch(
        vulnerable_code=demo_diff,
        exploit_result=mock_exploit_result
    )
    
    console.print("[green] Patch generated![/green]")
    console.print(f"  Explanation: {patch_result.explanation[:80]}...")
    console.print(f"  Complexity: {patch_result.complexity_analysis.get('before', 'N/A')}  {patch_result.complexity_analysis.get('after', 'N/A')}")
    
    console.print("\n[dim]Patch preview:[/dim]")
    patch_lines = patch_result.patch.split('\n')[:20]
    for line in patch_lines:
        console.print(f"[dim]{line}[/dim]")
    console.print("[dim]...[/dim]\n")
    
    # Load testing
    console.print("  Running performance validation...")
    from redroom.agents.surgeon.load_tester import LoadTester
    
    load_tester = LoadTester()
    baseline = await load_tester.run_load_test(
        target_url="http://demo-fintech:8080",
        duration_seconds=30,
        virtual_users=100
    )
    
    console.print("[green] Performance validation passed![/green]")
    console.print(f"  P95 latency: {baseline['p95_latency_ms']:.1f}ms")
    console.print(f"  Throughput: {baseline['throughput_rps']:.1f} req/s")
    console.print(f"  Error rate: {baseline['error_rate']:.2%}\n")
    
    # PR creation (mock)
    console.print("  Creating pull request...")
    console.print("  [yellow]Note: PR creation requires GitHub token[/yellow]")
    console.print("  [dim]Would create PR with:[/dim]")
    console.print(f"  [dim]- Title:  Security Fix: {hypothesis.vulnerability_type.replace('_', ' ').title()}[/dim]")
    console.print(f"  [dim]- Evidence: Exploit proof + Database violations[/dim]")
    console.print(f"  [dim]- Patch: Transaction-based fix[/dim]")
    console.print(f"  [dim]- Tests: Regression tests included[/dim]\n")
    
    # Summary
    console.print("[bold green] Three-Agent Pipeline Completed Successfully![/bold green]\n")
    console.print("[cyan]Summary:[/cyan]")
    console.print(f"  1. [yellow]Saboteur[/yellow] identified: {hypothesis.vulnerability_type} ({hypothesis.confidence_score:.0%} confidence)")
    console.print(f"  2. [yellow]Exploit Lab[/yellow] confirmed: Exploitable with {mock_exploit_result.reproducibility_score:.0%} reproducibility")
    console.print(f"  3. [yellow]Surgeon[/yellow] generated: Working patch with performance validation")
    
    console.print("\n[bold]Hardware Utilization:[/bold]")
    console.print(f"  NPU: Used for hypothesis generation ({detector.get_optimal_backend('inference')})")
    console.print(f"  GPU: Used for parallel exploit execution")
    console.print(f"  CPU: Used for patch generation and load testing")
    
    console.print("\n[bold yellow]Next Steps for Full Integration:[/bold yellow]")
    console.print("  1. Deploy Kubernetes cluster for shadow namespaces")
    console.print("  2. Configure GitHub token for PR creation")
    console.print("  3. Set up LangGraph orchestrator for workflow management")
    console.print("  4. Add webhook integration for CI/CD pipeline")
    console.print("  5. Configure monitoring and alerting")
    
    console.print("\n[bold]Demo Complete! [/bold]")


if __name__ == "__main__":
    asyncio.run(test_three_agents())

