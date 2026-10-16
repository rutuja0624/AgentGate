# AgentGate: Verification Gate for Pull Requests

AgentGate is a rigorous verification gate for pull requests (including AI-generated ones). For each PR, it:
1. **Builds a code graph** of changed files to compute impacted modules and reverse dependencies.
2. **Executes specialist reviewers** (security, correctness, design, tests) equipped with deterministic tools, not just raw prompts.
3. **Verifies hypotheses** by executing tests and static analysis in a strictly isolated, network-less Docker sandbox.
4. **Calculates a 0–100 merge-risk score** with verified evidence and posts an annotated PR comment and commit status.
5. **Provides human-in-the-loop governance** via a Spring Boot gateway and React dashboard with an append-only audit log.
6. **Exposes tools via the Model Context Protocol (MCP)** for direct integration with AI coding agents.
7. **Maintains a measured benchmark** evaluating precision, recall, and false-positive rates comparing LLM-only vs static-augmented vs full sandboxed review.

---

## Architecture Overview

```
GitHub PR event
      |
      v   (HMAC-verified webhook)
+-------------+     POST /internal/reviews      +---------------------------+
|  gateway    | ------------------------------> |  engine API (FastAPI)     |
| Spring Boot |                                 |  enqueue job in Redis     |
| auth, audit |                                 +-------------+-------------+
| approvals   |                                               |
|             | <---- GET /internal/reviews/{id} ----+        v
+------+------+                                      |   RQ worker
       ^                                              |   1. fetch diff + files (GitHub API)
       | REST (JWT)                                   |   2. code graph (ast + networkx)
       |                                              |   3. static tools (semgrep, radon, secrets)
+------+------+                                       |   4. sandbox: run tests (Docker)
|  dashboard  |                                       |   5. reviewers (LLM + tools, redacted input)
|  React/Vite |                                       |   6. score + persist (Postgres)
+-------------+                                       |   7. post PR comment + commit status
                                                      v
                                       +--------------+----------+
                                       | Postgres | Redis | Docker sandbox (no network)
                                       +-------------------------+
MCP server (stdio) --HTTP--> engine API  (Antigravity / Claude Code / Cursor)
```

---

## Monorepo Layout

```
agentgate/
  AGENTS.md                         # Standing operating rules for all agent tasks
  docs/
    BUILD_PLAN.md                   # Source of truth master plan
    SPRINT_48H.md                   # 48-hour sprint acceleration schedule
    architecture.md                 # Detailed architecture specification
    decisions/                      # Architecture Decision Records (ADRs)
  engine/                           # Python 3.12 + FastAPI + RQ + Docker SDK
    app/
      api/                          # Internal REST endpoints
      core/                         # Config, logging, DB session
      graph/                        # Code graph & impact analysis
      tools/                        # Semgrep, radon, secret scanners
      reviewers/                    # Specialist LLM reviewer agents
      sandbox/                      # Sandboxed Docker test execution
      llm/                          # Provider-agnostic LLM client (Gemini/OpenAI/Fake)
      security/                     # Input redaction & prompt-injection defense
      models/                       # SQLAlchemy models & Pydantic schemas
    tests/                          # Unit & integration test suites
  gateway/                          # Java 21 + Spring Boot 3.x
    src/main/java/                  # Controllers, Services, Entities, Flyway migrations
    src/test/java/                  # Unit and slice tests
  dashboard/                        # React 18 + Vite + TypeScript + Tailwind
    src/                            # Pages, components, typed API client
  mcp/                              # FastMCP Python server
  bench/                            # Benchmark cases, runner, and reporting
  deploy/                           # Docker Compose (local & prod), Caddyfile, Terraform
  .github/workflows/ci.yml          # GitHub Actions CI workflow
  .env.example                      # Environment variables template
  Makefile                          # Task runner
```

---

## Quickstart

### Prerequisites
- Python 3.12+
- Node.js 20+ (LTS) & npm
- JDK 21 (Temurin)
- Docker Desktop (with WSL2 backend enabled)
- Git & GitHub CLI

### Development Commands
```bash
# 1. Start Postgres (port 5432) and Redis (port 6379)
make up

# 2. Run Engine API (port 8001)
make engine

# 3. Run Engine RQ Background Worker
make worker

# 4. Run Spring Boot Gateway (port 8080)
make gateway

# 5. Run Vite Dashboard (port 5173)
make dash

# 6. Run test suites
make test

# 7. Run linters
make lint
```

---

## Security Model
- **Untrusted Code Execution**: All code submitted via PRs runs exclusively inside isolated Docker containers with `--network none`, `read_only` root FS, strict CPU/memory limits, dropped Linux capabilities, and timeout enforcement.
- **Prompt Injection Defense**: Diffs are treated as untrusted data enclosed in explicit delimiters (`<UNTRUSTED_CODE>`), with tag escape sanitization and schema-enforced output.
- **Redaction**: All code sent to LLM endpoints is scrubbed for credentials, private keys, API tokens, and emails via regex scanners before transmission.
- **Auditability**: Decisions (approvals/rejections) are written to an append-only audit log in PostgreSQL.
