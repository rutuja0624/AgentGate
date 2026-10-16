# AgentGate Architecture Specification

## 1. System Overview
AgentGate operates as an automated code intelligence and verification gate intercepting pull requests submitted to GitHub repositories. It evaluates change risk by orchestrating:
1. Static code graph generation (AST parsing and reverse dependency tracing).
2. Security, complexity, and secret detection tools.
3. Sandboxed test execution inside isolated ephemeral Docker containers (`--network none`).
4. Multi-agent LLM analysis with strict output validation and prompt-injection defense.
5. Deterministic risk scoring leading to human-governed approvals.

```mermaid
flowchart TD
    subgraph GitHub
        PR[Pull Request Event]
        Status[Commit Status API]
        Comment[PR Comment API]
    end

    subgraph Gateway ["Gateway (Spring Boot 3 / Java 21)"]
        WebhookHandler["Webhook Controller (HMAC-SHA256)"]
        AuthController["Auth & JWT"]
        DecisionController["PR & Decision API"]
        AuditService["Append-Only Audit Log"]
        EngineProxy["Engine RestClient"]
    end

    subgraph Engine ["Engine (FastAPI / Python 3.12)"]
        InternalAPI["Internal Review API"]
        RQ["Redis Queue (RQ)"]
        Worker["Review Worker"]
        CodeGraph["AST Code Graph (NetworkX)"]
        StaticTools["Semgrep / Radon / Secrets"]
        SandboxMgr["Docker Sandbox Runner"]
        ReviewerAgents["LLM Specialist Reviewers"]
        RiskEngine["Risk Score & Verdict"]
    end

    subgraph Storage
        PostgresDB[("PostgreSQL 16 (engine + gateway schemas)")]
        RedisDB[("Redis 7 (Jobs + Rate limits)")]
    end

    subgraph Dashboard ["Dashboard (React 18 / Vite / TS)"]
        UI["PR List, Review Details, Audit & Benchmark UI"]
    end

    PR -->|HMAC Webhook| WebhookHandler
    WebhookHandler -->|Idempotent Delivery| PostgresDB
    WebhookHandler -->|POST /internal/reviews| EngineProxy
    EngineProxy -->|X-Internal-Token| InternalAPI
    InternalAPI -->|Enqueue Review| RQ
    RQ --> Worker
    Worker -->|Build Graph| CodeGraph
    Worker -->|Scan| StaticTools
    Worker -->|Run Pytest (No Network)| SandboxMgr
    Worker -->|Prompt Reviewers| ReviewerAgents
    Worker -->|Compute Score| RiskEngine
    Worker -->|Persist Results| PostgresDB
    Worker -->|Post Comments & Status| Comment
    Worker -->|Set Status| Status
    UI -->|REST + JWT| AuthController
    UI -->|Approve / Reject| DecisionController
    DecisionController -->|Record Audit| AuditService
    AuditService --> PostgresDB
    DecisionController -->|Forward Status| EngineProxy
```

## 2. Security Boundaries
1. **GitHub Ingress**: All incoming webhooks must pass cryptographic HMAC-SHA256 verification using `MessageDigest.isEqual` before request body parsing.
2. **Untrusted Code Sandboxing**: Pull request code is never executed directly on the host or inside the engine container. All test runs happen in a locked container with no network access, read-only root filesystem, tmpfs limits, CPU limits, memory limits, and pids limits.
3. **Data Redaction**: Sensitive tokens (AWS keys, GitHub tokens, JWTs, emails) are stripped before sending code excerpts to external LLM providers.
4. **Prompt Injection Containment**: Diffs are encased in `<UNTRUSTED_CODE>` delimiters, interior closing tags are escaped, and reviewers are explicitly directed to treat code as passive data.
