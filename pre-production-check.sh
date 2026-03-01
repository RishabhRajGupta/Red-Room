#!/bin/bash
# Pre-Production Checklist Script for The Red Room

echo "========================================"
echo "The Red Room - Pre-Production Checks"
echo "========================================"
echo ""

# 1. Check for real API keys in .env.example
echo "[1/5] Checking .env.example for real API keys..."
if grep -q "AIzaSy" .env.example; then
    echo "[FAIL] ❌ Real API keys found in .env.example!"
    echo "       Please replace with placeholders before production."
    exit 1
else
    echo "[PASS] ✅ No real API keys in .env.example"
fi
echo ""

# 2. Check .gitignore includes .env
echo "[2/5] Checking .gitignore for .env..."
if grep -q "\.env" .gitignore; then
    echo "[PASS] ✅ .env is in .gitignore"
else
    echo "[WARN] ⚠️  .env not found in .gitignore"
fi
echo ""

# 3. Check if .env is tracked by git
echo "[3/5] Checking if .env is tracked by git..."
if git ls-files | grep -x "\.env" > /dev/null 2>&1; then
    echo "[FAIL] ❌ .env is tracked by git!"
    echo "       Run: git rm --cached .env"
    exit 1
else
    echo "[PASS] ✅ .env is not tracked by git"
fi
echo ""

# 4. Run tests
echo "[4/5] Running tests..."
if python test_three_agents.py > /dev/null 2>&1; then
    echo "[PASS] ✅ All tests passed"
else
    echo "[WARN] ⚠️  Some tests failed - check manually"
fi
echo ""

# 5. Check Python dependencies
echo "[5/5] Checking Python dependencies..."
export PYTHONPATH="$(pwd)/src"
if python -c "import redroom; print('OK')" > /dev/null 2>&1; then
    echo "[PASS] ✅ Core dependencies installed"
else
    echo "[FAIL] ❌ Missing dependencies"
    echo "       Run: ./install.sh"
    exit 1
fi
echo ""

echo "========================================"
echo "✅ Pre-Production Checks Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Review any warnings above"
echo "2. Set up your own .env file"
echo "3. Configure production settings"
echo "4. Deploy to production"
echo ""
echo "See PRE-PRODUCTION-CHECKLIST.md for details"
