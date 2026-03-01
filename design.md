# The Red Room: The Infinite Adversary - System Design Document

## 1. System Overview

### 1.1 Architecture Philosophy

The Red Room implements a **Contract-Driven Multi-Agent Swarm** architecture that transforms traditional vulnerability scanning into an active adversarial testing system. The design follows modern microservices patterns with event-driven orchestration, containerized isolation, and hardware-accelerated AI inference.

### 1.2 Core Design Principles

- **Verification over Detection:** Prove exploitability rather than report potential issues
- **Evidence-Based Remediation:** Generate patches backed by reproducible exploit proof
- **Zero Trust Execution:** Isolate all exploit attempts in ephemeral shadow environments
- **Hardware-Software Co-Design:** Leverage AMD hardware for optimal performance at each pipeline stage
- **Developer-Centric UX:** Minimize friction and false positives in CI/CD workflows

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Developer Workflow                       │
│                    (Git Push / PR Creation)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline Hook                         │
│                   (GitHub Webhook / GitLab CI)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                        │
│              (Stateful Multi-Agent Coordination)                 │
└─────┬───────────────────┬───────────────────┬───────────────────┘
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

## 3. Component Architecture

### 3.1 Orchestration Layer: LangGraph State Machine

**Technology:** LangGraph (Python)

**Responsibilities:**
- Manage cyclic, stateful handoffs between agents
- Handle error recovery and retry logic
- Maintain execution context and audit trail
- Coordinate resource allocation (NPU/GPU/CPU)

**State Machine Flow:**
```python
States:
  - IDLE: Waiting for Git webhook trigger
  - ANALYZING: Agent I processing diff
  - HYPOTHESIS_GENERATED: Attack vector identified
  - EXPLOITING: Agent II executing in shadow namespace
  - EXPLOIT_VERIFIED: Vulnerability confirmed
  - PATCHING: Agent III generating fix
  - VALIDATING: Performance testing patch
  - PR_CREATED: Pull request submitted
  - FAILED: Abort and log failure
```

**Key Design Decisions:**
- Use LangGraph over LangChain for better cyclic workflow support
- Implement checkpointing for long-running operations
- Store state in Redis for distributed orchestration

### 3.2 Agent I: The Saboteur (Hypothesis Generation)

**Deployment Target:** AMD Ryzen AI NPU (Edge Device)

**Technology Stack:**
- Model: Llama-3-8B-Instruct (Quantized to INT4 via ONNX)
- Runtime: onnxruntime-genai with Vitis AI Execution Provider
- Input Processing: Git diff parser + OpenAPI spec parser

**Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent I: Saboteur                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌─────────────────┐                 │
│  │ Git Diff     │─────▶│ Context Builder │                 │
│  │ Listener     │      │ (Diff + Spec)   │                 │
│  └──────────────┘      └────────┬────────┘                 │
│                                  │                          │
│                                  ▼                          │
│                        ┌──────────────────┐                │
│                        │ NPU Inference    │                │
│                        │ (Llama-3-8B-INT4)│                │
│                        └────────┬─────────┘                │
│                                 │                           │
│                                 ▼                           │
│                        ┌──────────────────┐                │
│                        │ JSON Schema      │                │
│                        │ Validator        │                │
│                        └────────┬─────────┘                │
│                                 │                           │
│                                 ▼                           │
│                        ┌──────────────────┐                │
│                        │ Hypothesis       │                │
│                        │ Output           │                │
│                        └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

**Input Schema:**
```json
{
  "git_diff": "string",
  "openapi_spec": "object",
  "security_contracts": "array",
  "previous_vulnerabilities": "array"
}
```

**Output Schema:**
```json
{
  "vulnerability_type": "race_condition | auth_bypass | injection | logic_flaw",
  "confidence_score": "float (0-1)",
  "affected_endpoints": ["array of API paths"],
  "invariant_break": {
    "expected_behavior": "string",
    "actual_behavior": "string",
    "contract_violation": "string"
  },
  "attack_hypothesis": {
    "method": "string",
    "payload": "object",
    "timing_requirements": "object",
    "expected_outcome": "string"
  }
}
```

**Hardware Optimization:**
- Quantization reduces model from 16GB to 2GB for NPU compatibility
- Inference latency: <500ms for typical Git diff
- Zero cloud latency for privacy-sensitive codebases
- Power efficiency: <15W during inference

**Key Design Decisions:**
- Process only Git diffs (not entire codebase) to fit NPU memory constraints
- Use structured output forcing via JSON schema constraints
- Implement local caching of OpenAPI specs to reduce context size
- Fallback to cloud LLM (Gemini 1.5 Pro) for complex multi-file analysis

### 3.3 Agent II: The Exploit Laboratory (Verification Engine)

**Deployment Target:** AMD ROCm GPU (Radeon/Instinct)

**Technology Stack:**
- Container: rocm/pytorch:latest
- Exploit Framework: Python requests + Playwright
- Parallel Execution: ROCm-accelerated batch processing
- Isolation: Kubernetes Namespaces + Docker

**Architecture:**

```
┌──────────────────────────────────────────────────────────────┐
│                Agent II: Exploit Laboratory                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌────────────────────┐           │
│  │ Hypothesis       │─────▶│ Exploit Script     │           │
│  │ Parser           │      │ Generator (LLM)    │           │
│  └──────────────────┘      └─────────┬──────────┘           │
│                                       │                      │
│                                       ▼                      │
│                            ┌────────────────────┐           │
│                            │ AST Syntax         │           │
│                            │ Validator          │           │
│                            └─────────┬──────────┘           │
│                                      │                      │
│                                      ▼                      │
│                            ┌────────────────────┐           │
│                            │ Shadow Namespace   │           │
│                            │ Orchestrator       │           │
│                            └─────────┬──────────┘           │
│                                      │                      │
│                    ┌─────────────────┼─────────────────┐   │
│                    ▼                 ▼                 ▼   │
│            ┌──────────────┐  ┌──────────────┐  ┌─────────┐│
│            │ GPU Worker 1 │  │ GPU Worker 2 │  │ Worker N││
│            │ (Parallel    │  │ (Parallel    │  │ ...     ││
│            │  Exploit)    │  │  Exploit)    │  │         ││
│            └──────┬───────┘  └──────┬───────┘  └────┬────┘│
│                   │                 │                │     │
│                   └─────────────────┼────────────────┘     │
│                                     ▼                      │
│                          ┌────────────────────┐           │
│                          │ Result Aggregator  │           │
│                          │ (Success/Failure)  │           │
│                          └────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

**Shadow Namespace Architecture:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: shadow-{uuid}
  labels:
    purpose: exploit-testing
    auto-cleanup: "true"
    ttl: "300s"
---
apiVersion: v1
kind: Pod
metadata:
  name: target-app
  namespace: shadow-{uuid}
spec:
  containers:
  - name: app
    image: fintech-demo:latest
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
  - name: db
    image: postgres:15-alpine
    volumeMounts:
    - name: sanitized-data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: sanitized-data
    persistentVolumeClaim:
      claimName: sanitized-snapshot
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: exploit-isolation
  namespace: shadow-{uuid}
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: exploit-executor
  egress:
  - to:
    - podSelector: {}
```

**Exploit Execution Flow:**

1. **Script Generation:**
   - LLM converts hypothesis to Python/Playwright code
   - AST validation ensures syntactic correctness
   - Inject instrumentation for result capture

2. **Parallel Execution (GPU-Accelerated):**
   - For race conditions: Launch 1000+ concurrent requests via GPU-parallelized workers
   - For crypto attacks: Use ROCm for hash brute-forcing
   - For timing attacks: Leverage GPU for microsecond-precision coordination

3. **Result Capture:**
   ```python
   {
     "exploit_successful": bool,
     "evidence": {
       "http_responses": [],
       "db_state_before": {},
       "db_state_after": {},
       "timing_data": {},
       "screenshots": []  # For UI-based exploits
     },
     "reproducibility_score": float,
     "execution_time_ms": int
   }
   ```

4. **Cleanup:**
   - Automatic namespace deletion after 5 minutes
   - Persistent logging to audit database
   - Evidence archival for compliance

**Hardware Optimization:**
- GPU passthrough: `--device=/dev/kfd --device=/dev/dri --group-add=video`
- ROCm batch processing for 10,000+ parallel HTTP requests
- Memory pooling to reduce allocation overhead
- Async I/O for network-bound operations

**Security Hardening:**
- Non-root container execution
- Capability dropping: `--cap-drop=ALL`
- Read-only root filesystem
- Network segmentation via Kubernetes NetworkPolicies
- Resource quotas to prevent DoS

**Key Design Decisions:**
- Use GPU for parallelization, not for LLM inference (network I/O is bottleneck)
- Implement 3-retry limit with error feedback to LLM
- Store exploit scripts in version control for audit trail
- Use ephemeral namespaces to prevent state pollution

### 3.4 Agent III: The Surgeon (Intelligent Remediation)

**Deployment Target:** CPU with Load Testing Infrastructure

**Technology Stack:**
- Model: Gemini 1.5 Pro API (or Mixtral 8x7B via ROCm for air-gapped)
- Load Testing: K6 or Locust
- Git Integration: PyGithub
- Code Analysis: Tree-sitter for AST manipulation

**Architecture:**

```
┌──────────────────────────────────────────────────────────────┐
│                  Agent III: The Surgeon                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌────────────────────┐           │
│  │ Exploit Evidence │─────▶│ Patch Generator    │           │
│  │ + Vulnerable Code│      │ (LLM)              │           │
│  └──────────────────┘      └─────────┬──────────┘           │
│                                       │                      │
│                                       ▼                      │
│                            ┌────────────────────┐           │
│                            │ Syntax Validator   │           │
│                            │ (Tree-sitter)      │           │
│                            └─────────┬──────────┘           │
│                                      │                      │
│                                      ▼                      │
│                            ┌────────────────────┐           │
│                            │ Shadow Deployment  │           │
│                            │ (Patched Version)  │           │
│                            └─────────┬──────────┘           │
│                                      │                      │
│                    ┌─────────────────┼─────────────────┐   │
│                    ▼                 ▼                 ▼   │
│            ┌──────────────┐  ┌──────────────┐  ┌─────────┐│
│            │ Load Test    │  │ Regression   │  │ Exploit ││
│            │ (K6/Locust)  │  │ Test Suite   │  │ Re-test ││
│            └──────┬───────┘  └──────┬───────┘  └────┬────┘│
│                   │                 │                │     │
│                   └─────────────────┼────────────────┘     │
│                                     ▼                      │
│                          ┌────────────────────┐           │
│                          │ Performance Delta  │           │
│                          │ Analysis           │           │
│                          └────────┬───────────┘           │
│                                   │                       │
│                                   ▼                       │
│                          ┌────────────────────┐           │
│                          │ PR Generator       │           │
│                          │ (PyGithub)         │           │
│                          └────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

**Patch Generation Prompt Template:**

```python
SYSTEM_PROMPT = """
You are a senior security engineer. Given:
1. Vulnerable code snippet
2. Successful exploit proof-of-concept
3. Business logic contracts

Generate a minimal, surgical patch that:
- Fixes the vulnerability completely
- Preserves existing functionality
- Maintains or improves algorithmic complexity
- Follows the codebase's existing style
- Includes inline comments explaining the fix

Output format:
{
  "patch": "unified diff format",
  "explanation": "string",
  "complexity_analysis": {
    "before": "O(n)",
    "after": "O(n)",
    "justification": "string"
  },
  "regression_tests": "pytest code"
}
"""
```

**Performance Validation Pipeline:**

```python
# 1. Deploy patched version to shadow namespace
kubectl apply -f shadow-patched-{uuid}.yaml

# 2. Run baseline load test (original code)
k6 run --vus 100 --duration 30s baseline-test.js > baseline.json

# 3. Run patched load test
k6 run --vus 100 --duration 30s patched-test.js > patched.json

# 4. Compare metrics
metrics_comparison = {
  "p95_latency_delta_ms": patched.p95 - baseline.p95,
  "throughput_delta_rps": patched.rps - baseline.rps,
  "error_rate_delta": patched.errors - baseline.errors,
  "cpu_usage_delta": patched.cpu - baseline.cpu,
  "memory_delta_mb": patched.memory - baseline.memory
}

# 5. Acceptance criteria
assert metrics_comparison["p95_latency_delta_ms"] < 50  # Max 50ms regression
assert metrics_comparison["error_rate_delta"] == 0
```

**Pull Request Template:**

```markdown
## 🔴 Security Vulnerability Fix - [VULNERABILITY_TYPE]

### Vulnerability Summary
[AI-generated description of the flaw]

### Exploit Proof-of-Concept
```python
[The actual exploit script that succeeded]
```

### Evidence
- **Exploitability:** Confirmed via automated testing
- **Severity:** [CVSS Score]
- **Affected Endpoints:** [List]

### Proposed Fix
[Explanation of the patch]

### Performance Impact
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| P95 Latency | 45ms | 47ms | +2ms |
| Throughput | 1000 rps | 1000 rps | 0 |
| CPU Usage | 60% | 61% | +1% |

### Regression Tests
[New test cases added]

### Complexity Analysis
- **Before:** O(n)
- **After:** O(n)
- **Justification:** [Explanation]

---
🤖 Generated by The Red Room - Infinite Adversary
⚠️ Requires human review before merge
```

**Key Design Decisions:**
- Replace uProf with application-level load testing (more relevant for web apps)
- Use comparative performance testing instead of absolute IPC measurements
- Generate regression tests alongside patches
- Require human approval for all merges (no auto-merge)
- Include complexity analysis to prevent algorithmic degradation

## 4. Data Flow Architecture

### 4.1 End-to-End Pipeline

```
1. Developer pushes code
   ↓
2. Git webhook triggers orchestrator
   ↓
3. Orchestrator extracts diff + OpenAPI spec
   ↓
4. Agent I (NPU) analyzes diff locally
   ↓
5. If vulnerability hypothesis generated:
   ↓
6. Orchestrator provisions shadow namespace
   ↓
7. Agent II (GPU) generates exploit script
   ↓
8. AST validation of exploit code
   ↓
9. Parallel exploit execution in shadow namespace
   ↓
10. If exploit succeeds:
    ↓
11. Evidence captured and archived
    ↓
12. Agent III generates patch
    ↓
13. Patch deployed to new shadow namespace
    ↓
14. Load testing + regression testing
    ↓
15. Performance delta analysis
    ↓
16. PR created with evidence + patch + tests
    ↓
17. Human review and merge
```

### 4.2 State Persistence

**Redis State Store:**
```json
{
  "execution_id": "uuid",
  "status": "EXPLOITING",
  "git_commit": "sha",
  "agent_states": {
    "saboteur": {
      "hypothesis": {},
      "confidence": 0.95,
      "timestamp": "iso8601"
    },
    "exploit_lab": {
      "attempts": 2,
      "shadow_namespace": "shadow-abc123",
      "exploit_successful": true,
      "evidence_path": "s3://evidence/abc123"
    },
    "surgeon": {
      "patch_generated": false
    }
  },
  "created_at": "iso8601",
  "updated_at": "iso8601"
}
```

## 5. Technology Stack Summary

### 5.1 Core Technologies

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Orchestration | LangGraph | Cyclic workflow support, checkpointing |
| Agent I Model | Llama-3-8B-INT4 | Fits NPU constraints, good reasoning |
| Agent II/III Model | Gemini 1.5 Pro API | Large context window, code generation |
| NPU Runtime | onnxruntime-genai + Vitis AI | AMD NPU support |
| GPU Runtime | ROCm/PyTorch | AMD GPU acceleration |
| Container Platform | Docker + Kubernetes | Industry standard, isolation |
| Load Testing | K6 | Modern, scriptable, accurate |
| Git Integration | PyGithub | Mature, well-documented |
| State Store | Redis | Fast, distributed, persistent |
| Logging | ELK Stack | Scalable, searchable, compliant |

### 5.2 Development Stack

| Purpose | Technology |
|---------|-----------|
| Language | Python 3.10+ |
| Dependency Management | Poetry |
| Code Quality | Ruff (linting), Black (formatting) |
| Testing | Pytest, Hypothesis (property testing) |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |
| Documentation | MkDocs |

## 6. Deployment Architecture

### 6.1 Development Environment (Hackathon)

```
Developer Laptop (AMD Ryzen AI)
├── Agent I (NPU) - Local inference
├── Minikube - Local Kubernetes
│   ├── Shadow Namespaces
│   └── Demo Fintech App
├── Docker with ROCm
│   └── Agent II (GPU) - Exploit execution
└── Agent III (CPU) - Patch generation
```

### 6.2 Production Environment (Enterprise)

```
┌─────────────────────────────────────────────────────────┐
│                    Edge Layer                            │
│  Developer Workstations (AMD Ryzen AI NPUs)             │
│  - Agent I running locally                              │
│  - Zero-latency diff analysis                           │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Orchestration Layer                     │
│  Kubernetes Cluster (Control Plane)                     │
│  - LangGraph Orchestrator (Replicated)                  │
│  - Redis Cluster (State)                                │
│  - RabbitMQ (Event Bus)                                 │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ GPU Cluster │  │ Shadow      │  │ Monitoring  │
│ (ROCm)      │  │ Namespace   │  │ & Logging   │
│             │  │ Pool        │  │             │
│ Agent II    │  │ (Ephemeral) │  │ ELK Stack   │
│ Workers     │  │             │  │ Prometheus  │
└─────────────┘  └─────────────┘  └─────────────┘
```

## 7. Security Architecture

### 7.1 Threat Model

**Threats:**
1. AI-generated exploit escaping sandbox
2. Malicious code injection via prompt manipulation
3. Resource exhaustion attacks
4. Data exfiltration from shadow namespaces
5. Privilege escalation in Kubernetes

**Mitigations:**

| Threat | Mitigation |
|--------|-----------|
| Sandbox escape | Non-root containers, capability dropping, NetworkPolicies |
| Prompt injection | Input sanitization, AST validation, output filtering |
| Resource exhaustion | Kubernetes resource quotas, pod limits, auto-cleanup |
| Data exfiltration | Network segmentation, egress filtering, sanitized snapshots |
| Privilege escalation | RBAC, Pod Security Standards, admission controllers |

### 7.2 Defense in Depth

```
Layer 1: Input Validation
  - AST parsing of AI-generated code
  - JSON schema validation
  - Git diff sanitization

Layer 2: Execution Isolation
  - Kubernetes namespaces
  - Docker containers
  - Network policies

Layer 3: Resource Limits
  - CPU/Memory quotas
  - Timeout enforcement
  - Concurrent execution limits

Layer 4: Monitoring & Alerting
  - Anomaly detection
  - Audit logging
  - Real-time alerts

Layer 5: Human Oversight
  - No auto-merge
  - PR review required
  - Manual approval gates
```

## 8. Scalability & Performance

### 8.1 Horizontal Scaling

**Agent I (NPU):**
- Scales with number of developer workstations
- No central bottleneck
- Linear scaling with team size

**Agent II (GPU):**
- Kubernetes HPA based on queue depth
- GPU node pool auto-scaling
- Target: 100 concurrent exploit executions

**Agent III (CPU):**
- Stateless, easily replicated
- Load balancer distribution
- Target: 50 concurrent patch generations

### 8.2 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Diff analysis latency | <5s | P95 |
| Shadow namespace creation | <10s | P95 |
| Exploit execution | <60s | P95 |
| Patch generation | <30s | P95 |
| End-to-end pipeline | <15min | P95 |
| False positive rate | <5% | Accuracy |

## 9. Observability & Monitoring

### 9.1 Metrics

**System Metrics:**
- Agent execution times
- Shadow namespace lifecycle
- GPU utilization
- NPU inference latency
- Queue depths

**Business Metrics:**
- Vulnerabilities detected
- Exploits verified
- Patches generated
- False positive rate
- Time to remediation

### 9.2 Logging Strategy

```python
{
  "timestamp": "iso8601",
  "execution_id": "uuid",
  "agent": "saboteur|exploit_lab|surgeon",
  "event": "hypothesis_generated|exploit_success|patch_created",
  "severity": "info|warning|error",
  "metadata": {
    "git_commit": "sha",
    "vulnerability_type": "string",
    "confidence": float,
    "evidence_path": "string"
  },
  "trace_id": "uuid"  # Distributed tracing
}
```

## 10. Risk Mitigation

### 10.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| AI hallucination | High | Medium | AST validation, retry logic, human review |
| Hardware failure | Medium | High | Cloud fallback, redundant infrastructure |
| Namespace escape | Low | Critical | Security hardening, monitoring, isolation |
| Performance degradation | Medium | Medium | Load testing, rollback capability |
| False negatives | Medium | High | Continuous model improvement, feedback loop |

### 10.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Pipeline slowdown | High | High | Async execution, caching, optimization |
| Cost overrun | Medium | Medium | Resource quotas, auto-scaling limits |
| Developer friction | Medium | High | UX optimization, clear documentation |
| Compliance issues | Low | Critical | Audit logging, data sanitization |

## 11. Future Architecture Evolution

### Phase 2: Multi-Language Support
- Extend to Java, Go, Rust
- Language-specific exploit frameworks
- Polyglot codebase analysis

### Phase 3: Distributed Deployment
- Multi-cloud support
- Edge computing integration
- Federated learning for model improvement

### Phase 4: Advanced Capabilities
- Supply chain security analysis
- ML model poisoning detection
- Zero-day vulnerability prediction

## 12. Hackathon Demo Architecture

### 12.1 Demo Application: Fintech Transfer Service

```python
# Deliberately vulnerable code
@app.post("/transfer")
async def transfer_funds(from_account: str, to_account: str, amount: float):
    # VULNERABILITY: Race condition - balance check not atomic
    balance = await db.get_balance(from_account)
    if balance >= amount:
        await asyncio.sleep(0.1)  # Simulated processing delay
        await db.deduct(from_account, amount)
        await db.credit(to_account, amount)
        return {"status": "success"}
    return {"status": "insufficient_funds"}
```

### 12.2 Demo Flow (3 Minutes)

**Minute 1: Problem Introduction**
- Show the vulnerable Fintech code
- Explain the race condition risk
- Traditional scanners miss this

**Minute 2: The Red Room in Action**
- Agent I identifies the race condition hypothesis
- Agent II generates exploit script
- Live GPU-accelerated parallel attack
- Show balance going negative in real-time

**Minute 3: Intelligent Remediation**
- Agent III generates patch with database transaction
- Performance validation shows no degradation
- PR created with full evidence

### 12.3 Demo Technical Setup

```bash
# Terminal 1: Orchestrator UI
python -m redroom.ui --mode demo

# Terminal 2: Shadow namespace monitor
watch kubectl get pods -n shadow-*

# Terminal 3: GPU utilization
watch rocm-smi

# Terminal 4: Demo app logs
kubectl logs -f fintech-demo -n demo
```

## 13. Conclusion

The Red Room architecture represents a paradigm shift from passive vulnerability scanning to active adversarial testing. By leveraging AMD's hardware ecosystem for optimal performance at each pipeline stage, the system delivers enterprise-grade security validation with minimal developer friction.

The multi-agent design ensures separation of concerns, fault isolation, and independent scalability. The contract-driven approach eliminates false positives while the evidence-backed remediation builds developer trust.

This architecture is production-ready for the hackathon demo and provides a clear path to enterprise deployment.
