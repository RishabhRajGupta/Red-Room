#!/bin/bash

echo "========================================"
echo "The Red Room - Quick Install"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not found!"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

echo "[1/3] Installing Python dependencies..."
pip3 install -r requirements-realtime.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo ""
echo "Installing The Red Room package..."
pip3 install -e .

if [ $? -ne 0 ]; then
    echo "[WARNING] Package install failed, using run.sh instead"
fi

echo ""
echo "[2/3] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "[WARNING] Docker not found!"
    echo "Docker is required for fullscan command."
    echo "Install: curl -fsSL https://get.docker.com | sh"
    echo ""
    echo "You can still use other commands without Docker."
else
    echo "Docker found!"
fi

echo ""
echo "[3/3] Testing installation..."
python3 -m redroom.cli hardware

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Quick Start:"
echo "  1. Test three-agent system:"
echo "     python3 test_three_agents.py"
echo ""
echo "  2. Scan demo app:"
echo "     ./run.sh fullscan ./demo-app"
echo "     (or: python3 -m redroom.cli fullscan ./demo-app)"
echo ""
echo "  3. Check hardware:"
echo "     ./run.sh hardware"
echo "     (or: python3 -m redroom.cli hardware)"
echo ""
echo "Read QUICKSTART.md for more info."
echo ""
