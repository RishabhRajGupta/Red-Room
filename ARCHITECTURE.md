# The Red Room - Architecture Overview

This document provides a high-level overview of The Red Room architecture. For detailed design, see [design.md](design.md).

## System Components

### 1. Orchestrator (LangGraph)
- Manages agent lifecycle
- Handles state transitions
- Coordinates resource allocation
- Implements retry logic

### 2. Agent I: The Saboteur (NPU)
- Runs on AMD Ryzen AI NPU
- Analyzes Git diffs locally
- Maps business logic contracts
- Generates attack hypotheses

### 3. Agent II: The Exploit Laboratory (GPU)
- Leverages AMD ROCm GPUs
- Generates exploit scripts
- Executes in shadow namespaces
- Collects evidence

### 4. Agent III: The Surgeon (CPU)
- Generates security patches
- Validates performance impact
- Creates pull requests
- Runs regression tests

## Data Flow

```
Git Push → Webhook → Orchestrator → Agent I (NPU)
                                        ↓
                                    Hypothesis
                                        ↓
                            Shadow Namespace ← Agent II (GPU)
                                        ↓
                                    Evidence
                                        ↓
                                    Agent III (CPU)
                                        ↓
                                    Pull Request
```

## Technology Stack

- **Language**: Python 3.10+
- **Orchestration**: LangGraph
- **AI Models**: Llama-3-8B (NPU), Gemini 1.5 Pro (Cloud)
- **Container**: Docker + Kubernetes
- **Hardware**: AMD Ryzen AI NPU, AMD ROCm GPUs
- **State**: Redis
- **Database**: PostgreSQL

## Security Model

- Non-root containers
- Kubernetes NetworkPolicies
- AST validation
- Resource quotas
- Audit logging

## Scalability

- Horizontal agent scaling
- GPU node pools
- Distributed state management
- Async execution

For implementation details, see [design.md](design.md).
