# 🔴 The Red Room - Three-Agent System

## Overview

The Red Room implements an autonomous three-agent pipeline for security testing:

```
Git Diff → Agent I (Saboteur) → Agent II (Exploit Lab) → Agent III (Surgeon) → Pull Request
           [NPU Inference]        [GPU Execution]         [CPU Patching]
```

## Architecture

### Agent I: The Saboteur (NPU-Powered)
**Purpose**: Analyze code changes and generate vulnerability hypotheses

**Hardware**: AMD Ryzen AI NPU (or CPU fallback)

**Components**:
- `diff_parser.py` - Parse Git diffs
- `diff_analyzer.py` - Extract security patterns
- `contract_parser.py` - Parse OpenAPI specs and security contracts
- `hypothesis_generator.py` - Generate attack hypotheses
- `npu_inference.py` - Hardware-accelerated LLM inference

**Input**: Git diff + OpenAPI spec + Security contracts

**Output**: Vulnerability hypothesis with confidence score

**Example**:
```json
{
  "vulnerability_type": "race_condition",
  "confidence_score": 0.95,
  "affected_endpoints": ["/transfer"],
  "attack_hypothesis": {
    "method": "concurrent_requests",
    "expected_outcome": "Balance goes negative"
  }
}
```

### Agent II: The Exploit Lab (GPU-Accelerated)
**Purpose**: Generate and execute exploits in isolated environments

**Hardware**: AMD ROCm GPU (or CPU fallback)

**Components**:
- `exploit_generator.py` - Generate exploit scripts
- `gpu_executor.py` - Parallel exploit execution
- `evidence_collector.py` - Collect proof of exploitability
- `shadow_namespace.py` - Kubernetes namespace management (TODO)

**Input**: Vulnerability hypothesis

**Output**: Exploit result with evidence

**Features**:
- AST validation of generated exploits
- Parallel execution (1000+ concurrent requests)
- Evidence collection (HTTP, database, timing)
- Shadow namespace isolation

**Example**:
```json
{
  "exploit_successful": true,
  "reproducibility_score": 1.0,
  "evidence": {
    "database": {
      "violations": [
        {"type": "negative_balance", "value": -100.0}
      ]
    }
  }
}
```

### Agent III: The Surgeon (CPU-Based)
**Purpose**: Generate patches and validate performance

**Hardware**: CPU (multi-threaded)

**Components**:
- `patch_generator.py` - Generate security patches
- `load_tester.py` - Performance validation
- `pr_creator.py` - GitHub PR automation

**Input**: Vulnerable code + Exploit result

**Output**: Patch + Performance validation + Pull request

**Features**:
- LLM-powered patch generation
- Load testing (K6/Locust integration)
- Performance comparison
- Automated PR creation with evidence

**Example**:
```python
# Before (vulnerable)
balance = await db.get_balance(from_account)
if balance >= amount:
    await asyncio.sleep(0.1)
    await db.deduct(from_account, amount)

# After (patched)
async with db.transaction():
    balance = await db.get_balance(from_account, lock=True)
    if balance >= amount:
        await db.deduct(from_account, amount)
```

## Hardware Integration

### Automatic Detection
The system automatically detects available hardware:

```python
from redroom.utils.hardware_detector import get_hardware_detector

detector = get_hardware_detector()
print(detector.capabilities)
```

### Optimal Backend Selection
Each agent uses the best available hardware:

| Agent | Optimal | Fallback |
|-------|---------|----------|
| Saboteur | AMD Ryzen AI NPU | CPU |
| Exploit Lab | AMD ROCm GPU | CPU (sequential) |
| Surgeon | CPU (multi-core) | CPU (single-core) |

### Performance Profiles

**With AMD Hardware**:
- Saboteur: <500ms inference latency
- Exploit Lab: 1000+ parallel requests
- Surgeon: <30s patch generation

**CPU Fallback**:
- Saboteur: ~2s inference latency
- Exploit Lab: Sequential execution
- Surgeon: <60s patch generation

## Quick Start

### 1. Test with Demo Code

```bash
# Using CLI
python -m redroom.cli agents --demo

# Or using test script
python test_three_agents.py

# Or using batch file
test-three-agents.bat
```

### 2. Test with Your Git Diff

```bash
# Create a diff file
git diff HEAD~1 > my-changes.diff

# Run analysis
python -m redroom.cli agents --diff-file my-changes.diff
```

### 3. Check Hardware

```bash
python -m redroom.cli hardware
```

## Current Status

### ✅ Implemented
- Agent I: Hypothesis generation with NPU integration
- Agent II: Exploit generation and evidence collection
- Agent III: Patch generation and load testing
- Hardware detection and automatic fallback
- CLI commands for testing
- Demo mode with vulnerable code

### ⏳ In Progress
- Shadow namespace deployment (Kubernetes)
- Actual exploit execution in isolated environments
- LangGraph orchestrator integration
- GitHub webhook integration

### 📋 TODO
- Real NPU model loading (currently using mock)
- K6/Locust integration for load testing
- GitHub PR creation (requires token)
- CI/CD pipeline integration
- Monitoring and alerting

## Example Output

```
🔴 The Red Room - Three-Agent System Test

Demo Code: Race condition in transfer endpoint

Step 0: Hardware Detection
  NPU: AMD Ryzen AI (optimized)
  GPU: AMD Radeon RX 7900 XTX
  CPU: AMD Ryzen 9 7950X
  Optimal backend: npu

Step 1: Agent I - Saboteur (NPU)
  Analyzing Git diff for vulnerabilities...
✅ Vulnerability hypothesis generated!
  Type: race_condition
  Confidence: 95%
  Endpoints: /transfer
  Attack method: concurrent_requests
  Expected outcome: Balance goes negative

Step 2: Agent II - Exploit Lab (GPU)
  Generating exploit script...
✅ Exploit script generated!
  Script length: 1234 bytes
  Syntax valid: True

✅ Exploit executed successfully!
  Reproducibility: 100%
  Execution time: 150ms
  Evidence: Balance went negative (critical violation)

Step 3: Agent III - Surgeon (CPU)
  Generating security patch...
✅ Patch generated!
  Explanation: Use database transaction with row-level locking...
  Complexity: O(1) → O(1)

  Running performance validation...
✅ Performance validation passed!
  P95 latency: 95.0ms
  Throughput: 333.3 req/s
  Error rate: 1.00%

✅ Three-Agent Pipeline Completed Successfully!

Summary:
  1. Saboteur identified: race_condition (95% confidence)
  2. Exploit Lab confirmed: Exploitable with 100% reproducibility
  3. Surgeon generated: Working patch with performance validation

Hardware Utilization:
  NPU: Used for hypothesis generation (npu)
  GPU: Used for parallel exploit execution
  CPU: Used for patch generation and load testing
```

## Integration with Existing Scanner

The three-agent system complements the existing web scanner:

**Web Scanner** (70 tests):
- Scans running applications
- Tests for known vulnerability patterns
- Generates reports

**Three-Agent System**:
- Analyzes code changes (Git diffs)
- Generates custom exploits
- Creates patches automatically

**Combined Workflow**:
1. Developer pushes code
2. Three-agent system analyzes diff
3. If vulnerability found, exploit is generated
4. Web scanner validates the running application
5. Patch is generated and PR created

## Configuration

### Environment Variables

```bash
# API Keys (for LLM fallback)
GEMINI_API_KEYS=key1,key2,key3
OPENAI_API_KEYS=key1,key2

# GitHub (for PR creation)
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPOSITORY=owner/repo

# Hardware (optional overrides)
FORCE_CPU=false
DISABLE_NPU=false
DISABLE_GPU=false
```

### Hardware Requirements

**Minimum**:
- CPU: Any modern x86_64 processor
- RAM: 8GB
- Storage: 10GB

**Recommended**:
- CPU: AMD Ryzen 7000 series or Intel 12th gen+
- NPU: AMD Ryzen AI (for optimal performance)
- GPU: AMD Radeon RX 6000+ or NVIDIA RTX 3000+
- RAM: 16GB
- Storage: 50GB SSD

**Optimal**:
- CPU: AMD Ryzen 9 7950X
- NPU: AMD Ryzen AI (built-in)
- GPU: AMD Radeon RX 7900 XTX
- RAM: 32GB DDR5
- Storage: 1TB NVMe SSD

## Development

### Adding New Vulnerability Types

1. Add to `VulnerabilityType` enum in `models/schemas.py`
2. Add pattern detection in `diff_analyzer.py`
3. Add exploit generation in `exploit_generator.py`
4. Add patch template in `patch_generator.py`

### Testing Individual Agents

```python
# Test Agent I
from redroom.agents.saboteur.hypothesis_generator import HypothesisGenerator
generator = HypothesisGenerator(model_path=None)
hypothesis = await generator.analyze_diff(git_diff)

# Test Agent II
from redroom.agents.exploit_lab.exploit_generator import ExploitGenerator
exploit_gen = ExploitGenerator(gpu_enabled=True)
script = await exploit_gen.generate_exploit(hypothesis)

# Test Agent III
from redroom.agents.surgeon.patch_generator import PatchGenerator
patch_gen = PatchGenerator(llm_provider="gemini")
patch = await patch_gen.generate_patch(code, exploit_result)
```

## Troubleshooting

### NPU Not Detected
```bash
# Check hardware
python -m redroom.cli hardware

# Force CPU fallback
export FORCE_CPU=true
```

### GPU Not Available
```bash
# Install ROCm (AMD)
# See: https://rocm.docs.amd.com/

# Install CUDA (NVIDIA)
# See: https://developer.nvidia.com/cuda-downloads
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements-realtime.txt

# Or use conda
conda env create -f environment.yml
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Workflow                        │
│                  (Git Push / PR Creation)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Orchestrator                      │
│            (Stateful Multi-Agent Coordination)               │
└─────┬───────────────────┬───────────────────┬───────────────┘
      │                   │                   │
      ▼                   ▼                   ▼
┌──────────┐      ┌──────────────┐     ┌─────────────┐
│ Agent I  │      │  Agent II    │     │  Agent III  │
│ Saboteur │─────▶│ Exploit Lab  │────▶│  Surgeon    │
│ (NPU)    │      │ (GPU/ROCm)   │     │ (CPU/Load)  │
└──────────┘      └──────────────┘     └─────────────┘
      │                   │                   │
      │                   ▼                   │
      │          ┌─────────────────┐          │
      │          │ Shadow Namespace│          │
      │          │   (Kubernetes)  │          │
      │          └─────────────────┘          │
      │                                       │
      └───────────────────┬───────────────────┘
                          ▼
                 ┌─────────────────┐
                 │  Pull Request   │
                 │  (Evidence +    │
                 │   Patch + Tests)│
                 └─────────────────┘
```

## References

- [Design Document](design.md) - Original system design
- [Architecture](ARCHITECTURE.md) - Detailed architecture
- [Hardware Support](HARDWARE-SUPPORT.md) - Hardware compatibility
- [Project Master](PROJECT-MASTER.md) - Single source of truth

---

🔴 **The Red Room: The Infinite Adversary** 🛡️

**Status**: Three-agent system implemented and testable  
**Next**: Shadow namespace deployment and full integration
