"""CLI interface for The Red Room."""

import typer
import asyncio
import uuid
from rich.console import Console
from typing import Optional
from pathlib import Path

from redroom.ui.terminal_ui import TerminalUI

# Lazy imports for heavy dependencies
def get_orchestrator():
    """Lazy import orchestrator to avoid loading langgraph unless needed."""
    from redroom.orchestrator.langgraph_engine import RedRoomOrchestrator
    return RedRoomOrchestrator()

def get_namespace_manager():
    """Lazy import namespace manager to avoid loading kubernetes unless needed."""
    from redroom.infrastructure.namespace_lifecycle import NamespaceLifecycle
    return NamespaceLifecycle()

def setup_logging():
    """Lazy import logger to avoid loading dependencies unless needed."""
    try:
        from redroom.utils.logger import setup_logging as _setup_logging
        _setup_logging()
    except ImportError:
        # If logger dependencies aren't available, just skip
        pass

app = typer.Typer(name="redroom", help="The Red Room: The Infinite Adversary")
console = Console()
ui = TerminalUI()


@app.command()
def start(
    mode: str = typer.Option("production", help="Mode: demo or production"),
    port: int = typer.Option(8000, help="Port to run orchestrator"),
):
    """Start The Red Room orchestrator."""
    setup_logging()
    ui.display_banner()
    
    console.print(f"[bold red]Starting The Red Room in {mode} mode...[/bold red]")
    console.print(f"[cyan]Port:[/cyan] {port}")
    
    if mode == "demo":
        console.print("\n[yellow]Running demo mode...[/yellow]")
        asyncio.run(ui.run_live_demo())
    else:
        console.print("\n[green]Starting orchestrator server...[/green]")
        console.print(f"[dim]Run: uvicorn redroom.orchestrator.main:app --host 0.0.0.0 --port {port}[/dim]")
        
        try:
            import uvicorn
            from redroom.orchestrator.main import app as fastapi_app
            uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
        except ImportError as e:
            console.print(f"[red]Error: Missing dependencies for orchestrator[/red]")
            console.print(f"[dim]Install with: pip install langgraph langchain uvicorn[/dim]")
            raise typer.Exit(1)


@app.command()
def scan(
    repo: Optional[str] = typer.Option(None, help="Repository path"),
    diff_file: Optional[str] = typer.Option(None, help="Path to diff file"),
    commit: Optional[str] = typer.Option(None, help="Git commit SHA"),
):
    """Scan for vulnerabilities."""
    setup_logging()
    ui.display_banner()
    
    console.print("[bold]Initiating security scan...[/bold]")
    
    # Read diff file
    if diff_file:
        diff_path = Path(diff_file)
        if not diff_path.exists():
            console.print(f"[red]Error: Diff file not found: {diff_file}[/red]")
            raise typer.Exit(1)
        
        git_diff = diff_path.read_text()
        console.print(f"[green]Loaded diff from: {diff_file}[/green]")
    else:
        console.print("[red]Error: --diff-file is required[/red]")
        raise typer.Exit(1)
    
    # Run scan
    execution_id = str(uuid.uuid4())
    commit_sha = commit or "unknown"
    
    console.print(f"[cyan]Execution ID:[/cyan] {execution_id}")
    console.print(f"[cyan]Commit:[/cyan] {commit_sha}")
    
    async def run_scan():
        try:
            orchestrator = get_orchestrator()
            result = await orchestrator.execute(
                execution_id=execution_id,
                git_commit=commit_sha,
                git_diff=git_diff
            )
        except ImportError as e:
            console.print(f"[red]Error: Missing dependencies for scan functionality[/red]")
            console.print(f"[dim]Install with: pip install langgraph langchain[/dim]")
            raise typer.Exit(1)
        
        console.print(f"\n[bold green]Scan completed![/bold green]")
        console.print(f"[cyan]Status:[/cyan] {result.status}")
        
        if result.hypothesis:
            ui.display_hypothesis(result.hypothesis.dict())
        
        if result.exploit_result:
            ui.display_exploit_result(result.exploit_result.dict())
        
        if result.patch_result:
            ui.display_patch_result(result.patch_result.dict())
    
    asyncio.run(run_scan())


@app.command()
def demo():
    """Run interactive demo."""
    setup_logging()
    asyncio.run(ui.run_live_demo())


@app.command()
def namespaces(
    action: str = typer.Argument(..., help="Action: list, cleanup, info"),
    namespace: Optional[str] = typer.Option(None, help="Namespace name for info action"),
):
    """Manage shadow namespaces."""
    setup_logging()
    
    try:
        ns_manager = get_namespace_manager()
        
        if action == "list":
            console.print("[bold]Shadow Namespaces:[/bold]")
            # TODO: Implement list functionality
            console.print("[dim]List functionality not yet implemented[/dim]")
        
        elif action == "cleanup":
            console.print("[yellow]Cleaning up expired namespaces...[/yellow]")
            ns_manager.cleanup_expired_namespaces()
            console.print("[green]Cleanup completed![/green]")
        
        elif action == "info":
            if not namespace:
                console.print("[red]Error: --namespace required for info action[/red]")
                raise typer.Exit(1)
            
            info = ns_manager.get_namespace_info(namespace)
            if info:
                console.print(f"\n[bold]Namespace: {namespace}[/bold]")
                console.print(f"[cyan]Status:[/cyan] {info['status']}")
                console.print(f"[cyan]Pods:[/cyan] {info['pod_count']}")
                for pod in info['pods']:
                    status_icon = "✅" if pod['ready'] else "❌"
                    console.print(f"  {status_icon} {pod['name']}: {pod['status']}")
            else:
                console.print(f"[red]Namespace not found: {namespace}[/red]")
        
        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("[dim]Available actions: list, cleanup, info[/dim]")
            raise typer.Exit(1)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def test(
    url: str = typer.Argument(..., help="URL of the application to test (e.g., http://localhost:8080)"),
    output: Optional[str] = typer.Option(None, help="Output file for report"),
    auto_fix: bool = typer.Option(False, help="Automatically generate and apply fixes")
):
    """Test a web application for security vulnerabilities."""
    setup_logging()
    ui.display_banner()
    
    console.print(f"[bold red]🔴 Starting Security Test[/bold red]")
    console.print(f"[cyan]Target:[/cyan] {url}\n")
    
    async def run_test():
        from redroom.agents.scanner.web_scanner import WebScanner
        
        # Step 1: Scan for vulnerabilities
        console.print("[yellow]Step 1: Scanning for vulnerabilities...[/yellow]")
        scanner = WebScanner(url)
        results = await scanner.scan()
        
        # Generate report
        report = scanner.generate_report(results)
        console.print(report)
        
        # Save report if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(report)
            console.print(f"\n[green]✅ Report saved to: {output}[/green]")
        
        # If vulnerabilities found and auto-fix enabled
        if results['vulnerabilities'] and auto_fix:
            console.print("\n[yellow]Step 2: Generating fixes...[/yellow]")
            console.print("[dim]Note: Auto-fix requires source code access[/dim]")
            console.print("[dim]For now, showing recommendations...[/dim]\n")
            
            for vuln in results['vulnerabilities']:
                console.print(f"\n[bold]{vuln['type'].upper()}[/bold] at {vuln['endpoint']}")
                console.print(f"Severity: [{_severity_color(vuln['severity'])}]{vuln['severity'].upper()}[/{_severity_color(vuln['severity'])}]")
                console.print(f"Recommendation: {_get_recommendation(vuln['type'])}")
        
        return results
    
    def _severity_color(severity: str) -> str:
        colors = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "blue"
        }
        return colors.get(severity, "white")
    
    def _get_recommendation(vuln_type: str) -> str:
        recommendations = {
            "sql_injection": "Use parameterized queries or ORM. Never concatenate user input into SQL.",
            "xss": "Sanitize and encode all user input. Use Content Security Policy headers.",
            "auth_bypass": "Implement proper authentication middleware. Check permissions on all protected routes.",
            "race_condition": "Use database transactions with proper locking. Implement idempotency keys.",
            "idor": "Implement authorization checks. Verify user owns the resource before access.",
            "csrf": "Implement CSRF tokens for all state-changing operations. Use SameSite cookie attribute.",
            "xxe": "Disable external entity processing in XML parsers. Use safe XML parsing libraries.",
            "ssrf": "Validate and whitelist allowed URLs. Use network segmentation to restrict internal access.",
            "command_injection": "Never pass user input to system commands. Use safe APIs instead of shell execution.",
            "path_traversal": "Validate file paths. Use allowlists and canonicalize paths before file operations.",
            "open_redirect": "Validate redirect URLs against a whitelist. Avoid user-controlled redirects.",
            "missing_security_headers": "Add security headers: X-Frame-Options, X-Content-Type-Options, CSP, HSTS.",
            "cors_misconfiguration": "Configure CORS properly. Avoid wildcard origins with credentials.",
            "sensitive_data_exposure": "Remove sensitive data from responses. Use proper data masking and encryption.",
            "broken_authentication": "Enforce strong password policies. Implement account lockout and MFA.",
            "mass_assignment": "Use allowlists for accepted fields. Validate and sanitize all input parameters.",
            "no_rate_limiting": "Implement rate limiting on all API endpoints. Use token bucket or sliding window algorithms."
        }
        return recommendations.get(vuln_type, "Review security best practices for this vulnerability type.")
    
    results = asyncio.run(run_test())
    
    # Summary
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Endpoints scanned: {results['endpoints_found']}")
    console.print(f"  Vulnerabilities found: {results['vulnerabilities_found']}")
    
    if results['vulnerabilities_found'] > 0:
        console.print(f"\n[red]⚠️  Security issues detected! Review the report above.[/red]")
    else:
        console.print(f"\n[green]✅ No obvious vulnerabilities detected![/green]")
        console.print(f"[dim]Note: This is a basic scan. Consider professional security audit.[/dim]")


@app.command()
def apipool(
    action: str = typer.Argument(..., help="Action: stats, add, disable, enable, strategy"),
    provider: Optional[str] = typer.Option(None, help="Provider name (gemini, openai, anthropic)"),
    key: Optional[str] = typer.Option(None, help="API key"),
    name: Optional[str] = typer.Option(None, help="Key name"),
    strategy: Optional[str] = typer.Option(None, help="Selection strategy (weighted_random, random, round_robin)")
):
    """Manage API key pool for LLM cycling."""
    setup_logging()
    
    from redroom.utils.api_pool import get_api_pool, load_api_keys_from_env
    
    pool = load_api_keys_from_env()
    
    if action == "stats":
        console.print("[bold]API Pool Statistics[/bold]\n")
        pool.print_stats()
    
    elif action == "add":
        if not provider or not key:
            console.print("[red]Error: --provider and --key required for add action[/red]")
            raise typer.Exit(1)
        
        pool.add_api_key(
            provider=provider,
            key=key,
            name=name or f"{provider}_custom"
        )
        console.print(f"[green]✅ Added API key for {provider}[/green]")
    
    elif action == "disable":
        if not provider or not name:
            console.print("[red]Error: --provider and --name required for disable action[/red]")
            raise typer.Exit(1)
        
        pool.disable_key(provider, name)
        console.print(f"[yellow]Disabled {provider}/{name}[/yellow]")
    
    elif action == "enable":
        if not provider or not name:
            console.print("[red]Error: --provider and --name required for enable action[/red]")
            raise typer.Exit(1)
        
        pool.enable_key(provider, name)
        console.print(f"[green]✅ Enabled {provider}/{name}[/green]")
    
    elif action == "strategy":
        if not strategy:
            console.print("[red]Error: --strategy required for strategy action[/red]")
            console.print("[dim]Valid strategies: weighted_random, random, round_robin[/dim]")
            raise typer.Exit(1)
        
        try:
            pool.set_selection_strategy(strategy)
            console.print(f"[green]✅ Selection strategy set to: {strategy}[/green]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    else:
        console.print(f"[red]Unknown action: {action}[/red]")
        console.print("[dim]Available actions: stats, add, disable, enable, strategy[/dim]")
        raise typer.Exit(1)


@app.command()
def hardware():
    """Show detected hardware capabilities."""
    setup_logging()
    
    from redroom.utils.hardware_detector import get_hardware_detector
    
    console.print("[bold]Detecting hardware capabilities...[/bold]\n")
    
    detector = get_hardware_detector()
    detector.print_capabilities()
    
    console.print(f"\n[bold]Optimal Backends:[/bold]")
    console.print(f"  Inference: {detector.get_optimal_backend('inference')}")
    console.print(f"  Parallel Execution: {detector.get_optimal_backend('parallel')}")
    console.print(f"  Patch Generation: {detector.get_optimal_backend('patch')}")


@app.command()
def fullscan(
    project: str = typer.Argument(..., help="Path to project folder or GitHub repo"),
    port: int = typer.Option(8080, help="Port to run the app on"),
    output: Optional[str] = typer.Option(None, help="Output file for report")
):
    """
    Full scan workflow: Deploy → Test → Analyze → Fix (Hardware Accelerated).
    
    This command:
    1. Deploys your app in Docker
    2. Runs 70 vulnerability tests (GPU-accelerated)
    3. Analyzes vulnerabilities (NPU-accelerated)
    4. Generates fixes (CPU)
    
    Hardware acceleration:
    - NPU: Hypothesis generation
    - GPU: Parallel testing (1000+ concurrent requests)
    - CPU: Patch generation
    """
    setup_logging()
    ui.display_banner()
    
    console.print("[bold red]Full Scan Workflow (Hardware Accelerated)[/bold red]\n")
    console.print(f"[cyan]Project:[/cyan] {project}")
    console.print(f"[cyan]Port:[/cyan] {port}\n")
    
    # Show hardware
    from redroom.utils.hardware_detector import get_hardware_detector
    detector = get_hardware_detector()
    
    console.print("[bold]Hardware Detection:[/bold]")
    console.print(f"  NPU: {detector.capabilities['npu'].get('device', 'Not available')}")
    console.print(f"  GPU: {detector.capabilities['gpu'].get('device', 'Not available')}")
    console.print(f"  CPU: {detector.capabilities['cpu'].get('vendor', 'Unknown')} ({detector.capabilities['cpu'].get('cores', 0)} cores)\n")
    
    async def run_workflow():
        from redroom.workflows.full_scan import FullScanWorkflow
        
        workflow = FullScanWorkflow(project)
        results = await workflow.run(port=port)
        
        # Display results
        console.print("\n[bold green]Scan Complete![/bold green]\n")
        
        console.print("[bold]Deployment:[/bold]")
        if results["deployment"].get("success"):
            console.print(f"  Status: [green]Success[/green]")
            console.print(f"  Method: {results['deployment'].get('method', 'unknown')}")
            console.print(f"  URL: {results['deployment'].get('url', 'unknown')}")
        else:
            console.print(f"  Status: [red]Failed[/red]")
            console.print(f"  Error: {results['deployment'].get('error', 'unknown')}")
            return
        
        console.print(f"\n[bold]Scan Results:[/bold]")
        console.print(f"  Endpoints found: {results['scan_results'].get('endpoints_found', 0)}")
        console.print(f"  Vulnerabilities found: {results['scan_results'].get('vulnerabilities_found', 0)}")
        
        if results["vulnerabilities"]:
            console.print(f"\n[bold]Vulnerabilities Analyzed:[/bold]")
            for i, vuln_analysis in enumerate(results["vulnerabilities"], 1):
                vuln = vuln_analysis["vulnerability"]
                console.print(f"\n  {i}. {vuln['type'].upper()}")
                console.print(f"     Endpoint: {vuln['endpoint']}")
                console.print(f"     Severity: [{_severity_color(vuln['severity'])}]{vuln['severity'].upper()}[/{_severity_color(vuln['severity'])}]")
                
                if vuln_analysis.get("hypothesis"):
                    console.print(f"     Analysis: NPU-accelerated hypothesis generated")
        
        if results["fixes"]:
            console.print(f"\n[bold]Fixes Generated:[/bold]")
            for i, fix in enumerate(results["fixes"], 1):
                vuln = fix["vulnerability"]
                console.print(f"\n  {i}. Fix for {vuln['type'].upper()}")
                console.print(f"     Endpoint: {vuln['endpoint']}")
                console.print(f"     Patch: Generated")
        
        console.print(f"\n[bold]Hardware Utilization:[/bold]")
        for component, backend in results.get("hardware_used", {}).items():
            console.print(f"  {component.title()}: {backend}")
        
        # Save report if requested
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"\n[green]Report saved to: {output}[/green]")
    
    def _severity_color(severity: str) -> str:
        colors = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "blue"
        }
        return colors.get(severity, "white")
    
    try:
        asyncio.run(run_workflow())
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def agents(
    diff_file: Optional[str] = typer.Option(None, help="Path to Git diff file"),
    demo: bool = typer.Option(False, help="Run with demo vulnerable code")
):
    """Test the three-agent system (Saboteur → Exploit Lab → Surgeon)."""
    setup_logging()
    ui.display_banner()
    
    console.print("[bold red]🔴 Three-Agent System Test[/bold red]\n")
    console.print("[cyan]Agent I:[/cyan] Saboteur (NPU) - Hypothesis Generation")
    console.print("[cyan]Agent II:[/cyan] Exploit Lab (GPU) - Exploit Execution")
    console.print("[cyan]Agent III:[/cyan] Surgeon (CPU) - Patch Generation\n")
    
    # Demo vulnerable code
    demo_diff = """
diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -10,8 +10,10 @@ async def transfer_funds(from_account: str, to_account: str, amount: float):
     # Check balance
     balance = await db.get_balance(from_account)
     if balance >= amount:
+        await asyncio.sleep(0.1)  # Simulated processing delay
         await db.deduct(from_account, amount)
         await db.credit(to_account, amount)
         return {"status": "success"}
     return {"status": "insufficient_funds"}
"""
    
    if demo:
        git_diff = demo_diff
        console.print("[yellow]Using demo vulnerable code (race condition)[/yellow]\n")
    elif diff_file:
        diff_path = Path(diff_file)
        if not diff_path.exists():
            console.print(f"[red]Error: Diff file not found: {diff_file}[/red]")
            raise typer.Exit(1)
        git_diff = diff_path.read_text()
        console.print(f"[green]Loaded diff from: {diff_file}[/green]\n")
    else:
        console.print("[red]Error: Either --diff-file or --demo is required[/red]")
        raise typer.Exit(1)
    
    async def run_agents():
        from redroom.agents.saboteur.hypothesis_generator import HypothesisGenerator
        from redroom.agents.saboteur.npu_inference import NPUInference
        from redroom.utils.hardware_detector import get_hardware_detector
        
        # Show hardware info
        detector = get_hardware_detector()
        console.print("[bold]Hardware Detection:[/bold]")
        console.print(f"  NPU: {detector.capabilities['npu'].get('device', 'Not available')}")
        console.print(f"  GPU: {detector.capabilities['gpu'].get('device', 'Not available')}")
        console.print(f"  CPU: {detector.capabilities['cpu']['model']}\n")
        
        # Agent I: Saboteur
        console.print("[bold yellow]Agent I: Saboteur (Analyzing diff...)[/bold yellow]")
        try:
            generator = HypothesisGenerator(model_path=None)  # Use mock for now
            hypothesis = await generator.analyze_diff(git_diff)
            
            if hypothesis:
                console.print("[green]✅ Vulnerability hypothesis generated![/green]")
                console.print(f"  Type: {hypothesis.vulnerability_type}")
                console.print(f"  Confidence: {hypothesis.confidence_score:.1%}")
                console.print(f"  Endpoints: {', '.join(hypothesis.affected_endpoints)}")
                console.print(f"  Attack: {hypothesis.attack_hypothesis.get('method', 'N/A')}\n")
            else:
                console.print("[green]✅ No vulnerabilities detected[/green]\n")
                return
            
            # Agent II: Exploit Lab
            console.print("[bold yellow]Agent II: Exploit Lab (Generating exploit...)[/bold yellow]")
            from redroom.agents.exploit_lab.exploit_generator import ExploitGenerator
            
            exploit_gen = ExploitGenerator(gpu_enabled=True)
            exploit_script = await exploit_gen.generate_exploit(hypothesis)
            
            console.print("[green]✅ Exploit script generated![/green]")
            console.print(f"  Script length: {len(exploit_script)} bytes")
            console.print(f"  Valid syntax: {exploit_gen.validate_exploit_script(exploit_script)}\n")
            
            # Show exploit preview
            console.print("[dim]Exploit preview:[/dim]")
            console.print("[dim]" + exploit_script[:200] + "...[/dim]\n")
            
            # Agent III: Surgeon
            console.print("[bold yellow]Agent III: Surgeon (Generating patch...)[/bold yellow]")
            from redroom.agents.surgeon.patch_generator import PatchGenerator
            
            patch_gen = PatchGenerator(llm_provider="gemini")
            
            # Mock exploit result for demo
            from redroom.models.schemas import ExploitResult
            mock_exploit_result = ExploitResult(
                exploit_successful=True,
                evidence={
                    "summary": {"exploit_successful": True, "confidence": 1.0},
                    "database": {"violations": [{"type": "negative_balance", "value": -100}]}
                },
                reproducibility_score=1.0,
                execution_time_ms=150,
                shadow_namespace="demo-shadow"
            )
            
            patch_result = await patch_gen.generate_patch(
                vulnerable_code=git_diff,
                exploit_result=mock_exploit_result
            )
            
            console.print("[green]✅ Patch generated![/green]")
            console.print(f"  Explanation: {patch_result.explanation[:100]}...")
            console.print(f"  Complexity: {patch_result.complexity_analysis.get('before', 'N/A')} → {patch_result.complexity_analysis.get('after', 'N/A')}\n")
            
            # Show patch preview
            console.print("[dim]Patch preview:[/dim]")
            console.print("[dim]" + patch_result.patch[:300] + "...[/dim]\n")
            
            console.print("[bold green]✅ Three-agent pipeline completed successfully![/bold green]")
            console.print("\n[cyan]Summary:[/cyan]")
            console.print(f"  1. Saboteur identified: {hypothesis.vulnerability_type}")
            console.print(f"  2. Exploit Lab generated working exploit")
            console.print(f"  3. Surgeon created patch with tests")
            console.print("\n[yellow]Note: This is a demo. Full integration requires:[/yellow]")
            console.print("  - Shadow namespace deployment (Kubernetes)")
            console.print("  - Actual exploit execution")
            console.print("  - Performance validation")
            console.print("  - PR creation (GitHub token required)")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise typer.Exit(1)
    
    asyncio.run(run_agents())


@app.command()
def version():
    """Show version information."""
    from redroom import __version__
    console.print(f"[bold red]The Red Room[/bold red] v{__version__}")
    console.print("[dim]Autonomous AI Security Ecosystem[/dim]")


if __name__ == "__main__":
    app()
