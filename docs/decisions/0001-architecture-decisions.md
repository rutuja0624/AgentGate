# ADR 0001: Core Architecture Decisions

## Status
Accepted

## Context
AgentGate is a portfolio verification gate for pull requests that combines code analysis, sandboxed execution, specialist LLM reviewers, human-in-the-loop approvals, and a benchmark. We need an architecture that balances robust security, clean separation of concerns, rapid development, and enterprise quality signals.

## Decisions

### 1. Two-Service Split (Spring Boot Gateway + FastAPI Engine)
- **Gateway (Java 21 / Spring Boot 3)**: Manages webhook ingress, user authentication, role-based access control, approvals, and an immutable audit log. Java/Spring provides mature enterprise security, strong typing, and enterprise patterns.
- **Engine (Python 3.12 / FastAPI)**: Manages code parsing (AST), dependency graph construction (NetworkX), static analysis (Semgrep, radon), sandboxed container execution (Docker SDK), and LLM reviewer orchestration. Python is the premier ecosystem for AI, AST tooling, and data manipulation.

### 2. Redis + RQ for Asynchronous Review Execution
- Instead of heavyweight message brokers like Kafka or RabbitMQ, we use Redis + RQ (Redis Queue).
- **Tradeoff**: Redis is lightweight, fast to run locally via Docker, trivial to maintain, and provides native atomic counters for token budget rate limiting. RQ provides Python job queue semantics with retry backoff.

### 3. Shared Database Instance with Strict Schema Separation
- A single PostgreSQL 16 instance hosts two independent schemas: `gateway` and `engine`.
- Services have zero cross-table queries. Communication between Gateway and Engine occurs strictly over HTTP REST using an internal token (`X-Internal-Token`).

### 4. Human-in-the-Loop Governance
- The AgentGate bot is strictly non-destructive: it comments findings and sets GitHub commit statuses (`pending`, `success`, `failure`). It never pushes commits, modifies branches, or auto-merges pull requests. Human approval is mandatory.
