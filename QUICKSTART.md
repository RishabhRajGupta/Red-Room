# 🚀 Quick Start - 2 Minutes

## Install & Run

### Step 1: Install (One Command)
```bash
pip install -r requirements-realtime.txt
```

### Step 2: Run (One Command)
```bash
# Scan your project
python -m redroom.cli fullscan ./your-project

# Or scan a demo
python -m redroom.cli fullscan ./demo-app
```

That's it! 🎉

## What You'll See

```
Hardware Detection:
  NPU: CPU Inference ✓
  GPU: NVIDIA CUDA ✓
  CPU: 24 cores ✓

Deploying in Docker...
✓ Flask detected
✓ Running on http://localhost:8080

Running 70 tests...
✓ Found 3 vulnerabilities

Analyzing...
✓ SQL Injection (92%)
✓ Race Condition (95%)
✓ XSS (88%)

Generating fixes...
✓ 3 patches ready

Done! Check report above.
```

## Requirements

- Python 3.10+
- Docker Desktop (for deployment)
- That's it!

## Install Docker

**Windows/Mac:**
Download from: https://www.docker.com/products/docker-desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
```

## Commands

```bash
# Method 1: Using run script (always works)
run.bat hardware              # Windows
./run.sh hardware             # Linux/Mac

run.bat fullscan ./my-project
./run.sh fullscan ./my-project

# Method 2: Using module (if installed)
python -m redroom.cli hardware
python -m redroom.cli fullscan ./my-project
```

## Troubleshooting

**"Docker not found"**
→ Install Docker Desktop

**"Module not found"**
→ Run: `pip install -r requirements-realtime.txt`

**"Port already in use"**
→ Use: `--port 8081`

## Next Steps

1. Read: `HOW-IT-WORKS.md`
2. Details: `HARDWARE-ACCELERATION-GUIDE.md`
3. Architecture: `THREE-AGENT-SYSTEM.md`

---

**That's it! Two commands and you're scanning.** 🚀
