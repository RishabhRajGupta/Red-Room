# Installation Guide

## Prerequisites

- Python 3.10 or higher
- Windows 10/11 (or Linux/macOS with modifications)
- pip package manager

## Quick Installation

### 1. Install Required Packages

```cmd
pip install fastapi uvicorn pydantic structlog rich typer httpx pyyaml
```

### 2. Set Python Path

**Windows (CMD)**:
```cmd
set PYTHONPATH=%CD%\src
```

**Windows (PowerShell)**:
```powershell
$env:PYTHONPATH="$PWD/src"
```

**Linux/macOS**:
```bash
export PYTHONPATH=$PWD/src
```

### 3. Run the Demo

```cmd
python src\redroom\ui\terminal_ui.py
```

Or use the batch file:
```cmd
run-demo.bat
```

## Full Installation (Optional)

For development with all dependencies:

### Using pip (Recommended for Windows)

```cmd
pip install -e . --no-deps
pip install fastapi uvicorn pydantic structlog rich typer httpx pyyaml
```

### Using Poetry (If available)

```cmd
poetry install
```

## Verify Installation

Run the demo to verify everything works:

```cmd
run-demo.bat
```

You should see:
- The Red Room banner
- Animated agent execution
- Success messages

## Common Issues

### Issue: ModuleNotFoundError: No module named 'redroom'

**Solution**: Set PYTHONPATH
```cmd
set PYTHONPATH=%CD%\src
```

### Issue: ModuleNotFoundError: No module named 'langgraph'

**Solution**: The full dependencies aren't needed for the demo. Just install the core packages:
```cmd
pip install fastapi uvicorn pydantic structlog rich typer httpx pyyaml
```

### Issue: Import errors for specific modules

**Solution**: Most optional dependencies (langgraph, kubernetes, etc.) are only needed for full functionality. The demo works with just the core packages.

## What's Installed

### Core Packages (Required)
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `structlog` - Structured logging
- `rich` - Terminal UI
- `typer` - CLI framework
- `httpx` - HTTP client
- `pyyaml` - YAML parser

### Optional Packages (For Full Functionality)
- `langgraph` - Agent orchestration
- `kubernetes` - K8s integration
- `torch` - GPU acceleration
- `onnxruntime-genai` - NPU inference

## Running Without Installation

You can run The Red Room without installing it as a package:

```cmd
set PYTHONPATH=%CD%\src
python src\redroom\ui\terminal_ui.py
```

This is the simplest way to get started!

## Next Steps

After installation:
1. Run the demo: `run-demo.bat`
2. Try CLI commands: `run-cli.bat demo`
3. Read the documentation
4. Explore the source code

## Support

If you encounter issues:
1. Check PYTHONPATH is set correctly
2. Verify Python version (3.10+)
3. Ensure core packages are installed
4. See QUICK-START.md for more help
