#!/bin/bash
set -e

echo "🧹 Cleaning up shadow namespaces..."

# Find all shadow namespaces
namespaces=$(kubectl get namespaces -o json | jq -r '.items[] | select(.metadata.name | startswith("shadow-")) | .metadata.name')

if [ -z "$namespaces" ]; then
    echo "✅ No shadow namespaces to clean up"
    exit 0
fi

# Delete each namespace
for ns in $namespaces; do
    echo "Deleting namespace: $ns"
    kubectl delete namespace "$ns" --grace-period=0 --force || true
done

echo "✅ Cleanup complete!"
