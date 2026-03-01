#!/bin/bash
set -e

echo "🔴 Setting up AMD hardware for The Red Room..."

# Check for AMD GPU
if ! command -v rocminfo &> /dev/null; then
    echo "⚠️  ROCm not found. Installing ROCm..."
    echo "Please follow: https://rocm.docs.amd.com/en/latest/deploy/linux/quick_start.html"
    exit 1
fi

# Verify GPU
echo "🔍 Checking AMD GPU..."
rocminfo | grep "Name:" || echo "⚠️  No AMD GPU detected"

# Check NPU support
echo "🔍 Checking for Ryzen AI NPU..."
if lspci | grep -i "AMD.*NPU" > /dev/null; then
    echo "✅ AMD Ryzen AI NPU detected"
else
    echo "⚠️  No AMD NPU detected. NPU features will be disabled."
fi

# Setup Docker GPU passthrough
echo "🐳 Configuring Docker for GPU access..."
sudo usermod -aG video $USER
sudo usermod -aG render $USER

# Test ROCm in Docker
echo "🧪 Testing ROCm in Docker..."
docker run --rm --device=/dev/kfd --device=/dev/dri --group-add video \
    rocm/pytorch:latest rocminfo > /dev/null 2>&1 && \
    echo "✅ ROCm Docker test passed" || \
    echo "❌ ROCm Docker test failed"

echo "✅ AMD hardware setup complete!"
echo ""
echo "⚠️  You may need to log out and back in for group changes to take effect"
