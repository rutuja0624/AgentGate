# AgentGate DevLog

### Day 0 (Phase 0 Foundations)
- **Built**: Monorepo scaffolding, directory layout, Docker Compose (Postgres 16 + Redis 7), root AGENTS.md, docs, Makefile, environment configs, CI workflow, Engine skeleton with FastAPI & healthz, Gateway Spring Boot skeleton, Dashboard React/Vite skeleton.
- **Broke / Blockers**: Verified local prerequisites: Python 3.12, Node 20, Git available; Java 17 detected (Java 21 upgrade recommended); Docker Desktop installed but daemon needs to be running.
- **Learned**: Enforcing contract-first design with separated DB schemas and pure-function risk scoring keeps services completely decoupled and testable in isolation.

### Day 1 (Stage A Contracts & Schemas)
- **Built**: OpenAPI 3.1 specs for Engine and Gateway; comprehensive Pydantic v2 schemas in `engine/app/models/schemas.py`; realistic review fixtures (clean, block with verified SQLi and test failure, failed with diff guard); mock engine server script `scripts/mock_engine.py`; automated contract validation test suite in `engine/tests/test_schemas.py` and `engine/tests/test_mock_engine.py`.
- **Verified**: All 10 engine unit tests passed; ruff lint clean; mypy clean (0 errors); all contract fixtures validate against models.

