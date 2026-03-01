#!/bin/bash
set -e

echo "🔴 Deploying The Red Room demo..."

# Start Minikube if not running
if ! minikube status > /dev/null 2>&1; then
    echo "🚀 Starting Minikube..."
    minikube start --driver=docker --cpus=4 --memory=8192
fi

# Build demo application
echo "🏗️  Building demo Fintech application..."
docker build -t fintech-demo:latest src/demo/fintech_app/

# Load image into Minikube
echo "📦 Loading image into Minikube..."
minikube image load fintech-demo:latest

# Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."
kubectl apply -f deployment/kubernetes/demo-namespace.yaml
kubectl apply -f deployment/kubernetes/demo-fintech-app.yaml

# Wait for deployment
echo "⏳ Waiting for deployment..."
kubectl wait --for=condition=available --timeout=60s \
    deployment/demo-fintech -n demo

# Get service URL
echo "✅ Demo deployed successfully!"
echo ""
echo "Demo Fintech App: $(minikube service demo-fintech -n demo --url)"
echo ""
echo "To start The Red Room:"
echo "  poetry run redroom start --mode demo"
