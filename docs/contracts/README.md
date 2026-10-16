# AgentGate API Contracts & Fixtures

This directory defines the cross-service API contracts and test fixtures that enable parallel development across the Python Review Engine, Java/Spring Boot Gateway, and React Dashboard.

---

## 1. OpenAPI Specifications

- **[engine.openapi.yaml](file:///c:/Big_Project/AgentGate/docs/contracts/engine.openapi.yaml)**: Internal contract exposed by the FastAPI Engine (`http://localhost:8001`) requiring the `X-Internal-Token` header.
- **[gateway.openapi.yaml](file:///c:/Big_Project/AgentGate/docs/contracts/gateway.openapi.yaml)**: Public and webhook API exposed by the Spring Boot Gateway (`http://localhost:8080`).

---

## 2. Shared Data Models

All Engine models are defined in [engine/app/models/schemas.py](file:///c:/Big_Project/AgentGate/engine/app/models/schemas.py) with Pydantic v2 validation:
- **`ReviewDetail`**: Top-level PR review containing risk score, verdict (`APPROVE`, `REVIEW`, `BLOCK`), findings, tool runs, and reverse impact list.
- **`Finding`**: Evidence-backed security or correctness finding with verification flag (`verified: true/false`).
- **`ReviewerOutput`**: Strict schema enforced on raw LLM responses. Extraneous keys are forbidden to prevent prompt injection leakage.
- **`ToolRun`**: Summaries of Semgrep, Radon, Secrets scanner, and Pytest sandbox runs.
- **`Impact`**: Reverse dependency chain mapped up to 3 hops via AST code graph.

---

## 3. Fixtures Catalog (`docs/contracts/fixtures/`)

| Fixture | Risk Score | Verdict | Scenario |
|---|---|---|---|
| [clean_review.json](file:///c:/Big_Project/AgentGate/docs/contracts/fixtures/clean_review.json) | 8 | `APPROVE` | Passing tests, zero critical findings, small blast radius. |
| [block_review.json](file:///c:/Big_Project/AgentGate/docs/contracts/fixtures/block_review.json) | 88 | `BLOCK` | Verified SQL injection (`agentgate.rules.sql-injection-format`) and sandboxed test failure (`sqlite3.OperationalError`). |
| [failed_review.json](file:///c:/Big_Project/AgentGate/docs/contracts/fixtures/failed_review.json) | null | null | Job rejected by diff size guard (> 2,000 lines changed). |

---

## 4. Running the Mock Engine

To run the mock engine during Gateway or Dashboard development:
```bash
python scripts/mock_engine.py --port 8001
```
The mock server checks the `X-Internal-Token` header and returns dynamic responses matching the fixtures based on PR numbers (PR #13 returns `BLOCK`, PR #14 returns `failed`, all others return `APPROVE`).
