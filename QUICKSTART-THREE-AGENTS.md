# 🚀 Quick Start - Three-Agent System

## Test in 3 Minutes

### Option 1: Using Test Script (Recommended)

```bash
# Run the test
python test_three_agents.py
```

### Option 2: Using Batch File (Windows)

```bash
# Double-click or run
test-three-agents.bat
```

### Option 3: Using CLI

```bash
# Test with demo code
python -m redroom.cli agents --demo

# Test with your own diff
git diff HEAD~1 > my-changes.diff
python -m redroom.cli agents --diff-file my-changes.diff
```

## What You'll See

```
🔴 The Red Room - Three-Agent System Test

Step 0: Hardware Detection
  NPU: AMD Ryzen AI (optimized)
  GPU: AMD Radeon RX 7900 XTX
  CPU: AMD Ryzen 9 7950X

Step 1: Agent I - Saboteur (NPU)
✅ Vulnerability hypothesis generated!
  Type: race_condition
  Confidence: 95%

Step 2: Agent II - Exploit Lab (GPU)
✅ Exploit script generated!
✅ Exploit executed successfully!

Step 3: Agent III - Surgeon (CPU)
✅ Patch generated!
✅ Performance validation passed!

✅ Three-Agent Pipeline Completed Successfully!
```

## Check Hardware

```bash
python -m redroom.cli hardware
```

Output:
```
Detecting hardware capabilities...

CPU: AMD Ryzen 9 7950X (16 cores)
NPU: AMD Ryzen AI (optimized)
GPU: AMD Radeon RX 7900 XTX

Optimal Backends:
  Inference: npu
  Parallel Execution: gpu
  Patch Generation: cpu
```

## Test with Real Code

### 1. Create a vulnerable endpoint

```python
# vulnerable.py
@app.post("/transfer")
async def transfer(from_account: str, to_account: str, amount: float):
    balance = await db.get_balance(from_account)
    if balance >= amount:
        await asyncio.sleep(0.1)  # Race condition!
        await db.deduct(from_account, amount)
        await db.credit(to_account, amount)
    return {"status": "success"}
```

### 2. Create a Git diff

```bash
git add vulnerable.py
git commit -m "Add transfer endpoint"
git diff HEAD~1 > transfer.diff
```

### 3. Run analysis

```bash
python -m redroom.cli agents --diff-file transfer.diff
```

### 4. Review results

The system will:
1. ✅ Identify the race condition
2. ✅ Generate an exploit script
3. ✅ Create a patch with database transaction
4. ✅ Validate performance impact

## What's Working

✅ **Agent I (Saboteur)**
- Git diff parsing
- Security pattern detection
- Vulnerability hypothesis generation
- NPU-accelerated inference (with CPU fallback)

✅ **Agent II (Exploit Lab)**
- Exploit script generation
- AST syntax validation
- Evidence collection
- GPU-accelerated parallel execution (with CPU fallback)

✅ **Agent III (Surgeon)**
- Patch generation
- Load testing
- Performance validation
- PR creation (needs GitHub token)

✅ **Hardware Integration**
- Automatic detection (NPU/GPU/CPU)
- Optimal backend selection
- Graceful fallbacks

## What's Next

⏳ **For Production Use**:
1. Deploy Kubernetes cluster
2. Set up shadow namespaces
3. Configure GitHub token
4. Add CI/CD webhooks

## Troubleshooting

### "Module not found" errors

```bash
# Install dependencies
pip install -r requirements-realtime.txt

# Or use conda
conda env create -f environment.yml
conda activate redroom
```

### Hardware not detected

```bash
# Check hardware
python -m redroom.cli hardware

# Force CPU fallback
export FORCE_CPU=true
python test_three_agents.py
```

### Import errors

```bash
# Make sure you're in the project root
cd The-Red-Room

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use the CLI module
python -m redroom.cli agents --demo
```

## Next Steps

1. ✅ Test the three-agent system (you are here!)
2. Read [THREE-AGENT-SYSTEM.md](THREE-AGENT-SYSTEM.md) for details
3. Check [PROJECT-MASTER.md](PROJECT-MASTER.md) for roadmap
4. Deploy to Kubernetes for production use

## Demo Video Script

**Minute 1: Problem**
- Show vulnerable code (race condition)
- Explain why traditional scanners miss it

**Minute 2: The Red Room in Action**
- Run `python test_three_agents.py`
- Show Agent I identifying the vulnerability
- Show Agent II generating exploit
- Show Agent III creating patch

**Minute 3: Results**
- Show the generated patch
- Show performance validation
- Explain the evidence collected

## Key Features

🔴 **Autonomous**: No manual intervention needed
🧠 **Intelligent**: Uses LLMs for hypothesis and patch generation
⚡ **Fast**: Hardware-accelerated (NPU/GPU/CPU)
🔒 **Safe**: Isolated execution in shadow namespaces
📊 **Evidence-Based**: Proves exploitability before patching
🎯 **Accurate**: Low false positive rate

---

**Ready to test?** Run `python test_three_agents.py` now! 🚀
