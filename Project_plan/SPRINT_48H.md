# AgentGate: 48-Hour Sprint Plan (full scope)

Put this at `docs/SPRINT_48H.md`. It overrides the 21-day schedule in `BUILD_PLAN.md` Section 14. Everything else in BUILD_PLAN.md (scope, schemas, APIs, sandbox rules, benchmark design) still applies. Nothing is removed from the project; the schedule is compressed by running agents in parallel and by sequencing the riskiest items first.

## 0. Read this first (honest expectations)

- The whole project in 48 hours is only possible because several agents work in parallel. **Your bottlenecks are not typing speed. They are: reviewing agent output, verifying benchmark labels, AWS setup, and LLM rate limits.** The plan is built around those.
- Plan for roughly 32 hours of focused work plus sleep. Do not skip sleep: tired review of agent code is how bugs and security holes get merged. Two 16-hour work blocks, one 7-hour sleep, and a 9-hour buffer at the end (which includes a nap and your interview study session).
- Agent-generated code you did not read is a liability in an interview. The final block includes a mandatory 90-minute "explain it back" session. Do not trade it away.
- Every time box below is a **hard stop**. When it expires, merge what works, note the gap in `docs/DEVLOG.md`, and move on. A working 80% lane beats a half-finished 100% lane that blocks everyone else.
- At every checkpoint the project is in a shippable state. If something slips, it is always the **last** item in the order, never a foundation.
- Do not fabricate benchmark numbers, screenshots, or upstream PRs to make up time. Report what is real.

---

## 1. Before the clock starts (do this today, 60-90 minutes)

1. Install everything in BUILD_PLAN Section 2.1 (Git, GitHub CLI, Python 3.12, uv, Node LTS, JDK 21, Docker Desktop, make, Antigravity, smee client). Verify each with its version command. Run `docker run hello-world`.
2. Pre-pull images so the sprint does not wait on downloads: `docker pull postgres:16`, `docker pull redis:7`, `docker pull python:3.12-slim`.
3. Create accounts and keys: GitHub test repo (you own it), fine-grained PAT scoped to that repo (BUILD_PLAN Section 3), webhook secret (32+ random characters), LLM API key, AWS account with a **billing alarm** and an IAM user (not root keys). AWS account verification can take time, so do this now.
4. Create the **test repo content**: a small Python project (50-150 lines, with pytest tests that pass). You will open PRs against it for end-to-end tests and the demo.
5. Check your LLM provider's current rate limits and quotas. With several agents plus benchmark runs, the free tier may throttle you. If it is too tight, plan to use a paid tier or a second provider for the benchmark only.
6. In Antigravity, set terminal autonomy so lint/test commands can auto-run, but keep manual review for `docker`, install, network, and AWS/cloud commands.
7. Create the empty repo, add `AGENTS.md` (root) and this file and BUILD_PLAN.md under `docs/`. Do **not** enable strict branch protection yet (it comes after CI exists, Hour 12).

---

## 2. Operating rules for the sprint

**Contract-first.** Parallel lanes only work if everyone builds against the same interfaces. Stage A (Hours 1.5-3) produces schemas, API specs, and fixtures before any lane starts.

**Lanes own folders.** No two agents ever edit the same folder.

| Lane | Folder(s) it owns | Depends on |
|---|---|---|
| A1 Engine core | `engine/app/api`, `engine/app/core`, `engine/app/models`, `engine/alembic`, `engine/app/github` | Stage A |
| A2 Analysis tools | `engine/app/graph`, `engine/app/tools`, `engine/rules` | Stage A |
| A3 Sandbox | `engine/app/sandbox`, `engine/sandbox` | Stage A |
| A4 Pipeline and reviewers | `engine/app/llm`, `engine/app/reviewers`, `engine/app/security`, `engine/app/pipeline` | A1, A2, A3 merged |
| B Gateway | `gateway/` | Stage A |
| C Dashboard | `dashboard/` | Stage A (mock data), later gateway |
| D Benchmark | `bench/` | Stage A, later engine |
| E Infra and CI/CD | `.github/`, `deploy/`, `Makefile`, `docs/DEPLOY.md` | Stage A |
| F MCP | `mcp/` | engine API |
| G Hardening | `engine/tests/security`, `gateway/src/test/.../security` | A4, B |
| H Observability and Terraform | `deploy/terraform`, `deploy/grafana`, engine `/metrics` module | E, A1 |

**Merge discipline.** Each lane works on `lane/<name>`. When its acceptance passes, you review the diff (30 minutes max), run `make test`, merge to `main`, and tell the next lane to rebase.

**Concurrency limit.** Run at most 4 agents at once. More than that and you cannot review fast enough, and you hit LLM rate limits.

**Dependencies pre-declared.** In Stage A the agent writes the complete `pyproject.toml`, `pom.xml`, and `package.json` with every dependency from BUILD_PLAN. Lanes do not edit them.

**Contract changes.** Lanes write requests in `docs/CONTRACT_REQUESTS.md`. You resolve them at the next checkpoint.

---

## 3. Hour-by-hour schedule

H0 = the moment you start the clock.

### DAY 1 (H0-H16)

| Hours | What | Who |
|---|---|---|
| H0-1.5 | **Phase 0**: skeleton, compose, health endpoints, Makefile, `.env`, CI stub | 1 agent (prompt P0) |
| H1.5-3 | **Stage A**: contracts, schemas, fixtures (prompt PA). Meanwhile YOU: push test repo, launch the EC2 instance and security group, install Docker on it | 1 agent + you |
| H3-9 | **Wave 1**: lanes A1, A2, A3, B in parallel. You review in rotation: ~H5, H7, H9 | 4 agents |
| H9-15 | **Wave 2**: lanes A4, C, D, E in parallel. Enable branch protection once E's CI is green (~H12) | 4 agents |
| H15-16 | **Checkpoint 1**: engine runs end-to-end on a real PR from your test repo with `FakeLLMClient`; gateway and dashboard run against fixtures; CI green. Update DEVLOG. Push. | you |
| H16-23 | **Sleep.** Optionally leave a benchmark dataset-generation agent running only if it cannot block anything | you |

### DAY 2 (H23-H39)

| Hours | What | Who |
|---|---|---|
| H23-26 | **Integration block**: real LLM key, engine + gateway + dashboard wired together, `scripts/e2e.sh` passes with a signed fake webhook, then with a real PR. Start dataset label verification (Section 5). Deploy first version to EC2 (E lane + you following `docs/DEPLOY.md`) | 2 agents + you |
| H26-32 | **Wave 3**: lanes F (MCP), G (hardening and prompt-injection tests), H (metrics, Grafana, Terraform) in parallel. Meanwhile start the **benchmark run** in the background (`make bench`, all three modes, 3 repeats, with LLM caching) | 3 agents + bench |
| H32-35 | **Tuning**: tune score weights on the train split only; run the held-out test split once; write the ADR. Dashboard Benchmark page reads `latest.json`. Redeploy final version. Short k6 load test | you + 1 agent |
| H35-39 | **Validation and showcase**: run AgentGate on 3-5 open-source Python repos (forks or your own PRs), submit 1-2 genuine upstream PRs, record screenshots, README, demo video, resume bullets | you |

### BUFFER (H39-H48)
- H39-43: fix whatever broke in validation; sleep or nap 4 hours if you can.
- H43-45: **Explain-it-back session** (90 minutes): for each component, explain aloud what it does, why it was designed that way, and what the tradeoffs are. Use the interview questions in BUILD_PLAN 16.5. Fix any code you cannot explain by simplifying it.
- H45-48: final README pass, tag `v1.0`, confirm the live link works from a different network (phone data), and submit.

---

## 4. Prompts (paste into Antigravity; each begins with the common header)

**Common header (put at the start of every prompt):**
> Read `AGENTS.md` and `docs/BUILD_PLAN.md` first, and `docs/SPRINT_48H.md` for the sprint rules. You are working in lane `<LANE>`. Only edit the folders that lane owns. Write a short plan first, then implement, run tests and linters, and report exactly what passes and what does not. Do not claim success without running the commands.

### P0: Foundations (H0)
> Execute BUILD_PLAN Section 5 (Phase 0). Create the monorepo skeleton, `docker-compose` for Postgres and Redis with the two schemas, health endpoints for engine and gateway, the Vite dashboard stub, the Makefile targets listed in AGENTS.md section 8, `.env.example`, and a CI workflow stub. Declare the COMPLETE dependency set now so later lanes never edit dependency files: Python deps listed in BUILD_PLAN 2.2 plus `respx`, `pytest-timeout`, `pytest-asyncio`, `detect-secrets` optional; Java deps for Web, Security, JPA, Validation, Actuator, PostgreSQL, Flyway, Testcontainers, JJWT, and Micrometer Prometheus; npm deps listed in BUILD_PLAN 2.3 plus `vitest`, `@testing-library/react`, `msw`. Acceptance: `make up && make test && make lint` pass on a clean clone.

### PA: Contracts (H1.5)
> Produce the contracts that all lanes will build against, and commit them: (1) `docs/contracts/engine.openapi.yaml` for BUILD_PLAN 8.1; (2) `docs/contracts/gateway.openapi.yaml` for 8.2; (3) Pydantic schemas in `engine/app/models/schemas.py` for Review, Finding, ToolRun, Impact, RiskResult, and the reviewer JSON output; (4) SQL DDL as Alembic and Flyway migration drafts matching BUILD_PLAN 6; (5) realistic JSON fixtures in `docs/contracts/fixtures/` (a clean review, a BLOCK review with a verified SQL injection and a failing test, a failed review); (6) a mock engine server script (`scripts/mock_engine.py`, FastAPI serving the fixtures) and a README of the contracts. Acceptance: schemas import cleanly, fixtures validate against the schemas in a test, OpenAPI files lint.

### A1: Engine core
> Lane A1. Implement BUILD_PLAN Phase 1: SQLAlchemy models and Alembic migration, GitHub client (get_pr, get_diff, get_file_at_sha, post_comment, set_status) with httpx, FastAPI endpoints per the engine contract with internal-token auth, RQ queue and a worker whose `run_review` calls pipeline stage functions through an interface (stubbed for now). Diff size guard (7.1 step 1). Unit and integration tests with mocked GitHub (`respx`). Acceptance: POST creates a review row, the worker processes it, status transitions work, tests pass.

### A2: Analysis tools
> Lane A2. Implement BUILD_PLAN 7.2 and 7.3: code graph builder (ast + networkx, impact distance up to 3, syntax-error tolerance), Semgrep wrapper with 5 custom local rules, radon complexity delta, secrets scanner. Each wrapper returns Pydantic models and never raises on tool failure. Tests with fixture packages and recorded tool outputs. Acceptance: all tools run on a sample project and tests pass.

### A3: Sandbox
> Lane A3. Implement BUILD_PLAN 7.4: sandbox Dockerfile, runner using the Docker SDK with EVERY listed constraint, baseline-vs-head comparison returning only new failures, log truncation, guaranteed cleanup. Write the five malicious fixture tests (network access, fork bomb, memory bomb, writing outside tmpfs, infinite sleep). Acceptance: all five are contained and reported; no leftover containers (`docker ps -a`).

### B: Gateway
> Lane B. Implement BUILD_PLAN 6.2, 8.2, 9 (gateway part): Flyway migrations, JWT login with BCrypt and login rate limiting, HMAC-verified webhook with delivery-id idempotency, EngineClient (RestClient with timeouts and internal token, errors mapped to 502), pull-request and decision endpoints with role checks, append-only audit log, metrics summary endpoint, benchmark endpoint. Develop against `scripts/mock_engine.py`. Tests: controller slices, Testcontainers repositories, signature valid/invalid/missing, role matrix. Acceptance: `./mvnw verify` passes; a signed webhook creates a PR row and calls the (mock) engine.

### A4: Pipeline and reviewers (after A1-A3 are merged)
> Lane A4. Implement BUILD_PLAN 7.5-7.8 and wire the full pipeline from 7.1: LLM client interface with Gemini, OpenAI-compatible, and Fake implementations (timeouts, jittered retries, token caps, daily budget, caching keyed by hash of redacted prompt + model); redaction; security and correctness reviewers, plus design and test-quality reviewers, with strict Pydantic validation and one retry; delimiter escaping for `</UNTRUSTED_CODE>`; finding dedup/verification; the risk score as a pure function with unit tests; PR comment and commit status formatting; `analyze-diff` endpoint. Use `FakeLLMClient` in CI tests. Acceptance: end-to-end on a real PR from the test repo posts a comment and status (use the live LLM once, manually).

### C: Dashboard
> Lane C. Implement BUILD_PLAN section 9 dashboard: typed API client from the gateway contract, React Query, routing, Login, PR list, PR detail (score gauge, severity groups, evidence badges, expandable evidence, impacted modules, tool runs, cost, approve/reject with required comment), Metrics, Benchmark (reads `/api/benchmark/latest`), Audit log. Develop against MSW fixtures from `docs/contracts/fixtures/`. Loading, empty, and error states everywhere; responsive. Vitest tests for the PR table and finding card. Acceptance: `npm run build` and tests pass; all pages work against fixtures.

### D: Benchmark
> Lane D. Implement BUILD_PLAN section 11: `run.py`, `report.py`, label schema, train/test split (fixed seed, stored in `bench/split.json`), three modes, repeat runs, results JSON and markdown. Then generate 6-8 small Python projects with passing tests and 8 patches each (clean, logic bug caught by tests, security issue, subtle bug NOT caught by tests), labelled per 11.2, with a mix of hand-style, AI-generated, and seeded patches. Also write `bench/verify_labels.py` (Section 5 of the sprint plan). Acceptance: framework runs with a fake engine; dataset has at least 60 cases; `verify_labels.py` runs.

### E: Infra and CI/CD
> Lane E. Implement BUILD_PLAN 13.1-13.3: finalize CI (parallel jobs, caching, coverage summary), `deploy.yml` (build and push to GHCR, SSH deploy, smoke test, rollback to the previous tag), production compose, Caddyfile, Dockerfiles for engine, worker, gateway, dashboard, and `docs/DEPLOY.md` as a step-by-step runbook for me (EC2 host prep, Docker install, env file, GitHub secrets). Acceptance: CI is green; a dry-run of the deploy workflow's build steps passes.

### F: MCP server (H26)
> Lane F. Implement BUILD_PLAN section 10 with FastMCP over stdio: `review_diff`, `run_tests` (allowlisted paths only), `get_impact`, `explain_finding`. Tests call the tool functions directly. README instructions to register it in Antigravity. Acceptance: tests pass and the server starts.

### G: Hardening (H26)
> Lane G. Implement BUILD_PLAN 12.1 and 12.2: prompt-injection fixtures and tests (5 cases), the grep-style test that the GitHub client has no merge/push/approve methods, audit completeness test (one decision = one audit row), token budget guard test. Fix gaps you find in the owning lane's code by writing the request in `docs/CONTRACT_REQUESTS.md`; I will route it.

### H: Observability and Terraform (H26)
> Lane H. Add Prometheus metrics to the engine (`reviews_total` by verdict, `review_duration_seconds`, `llm_tokens_total`, `sandbox_timeouts_total`, queue depth) and the gateway actuator Prometheus endpoint; Grafana and Prometheus in a separate compose file with a provisioned dashboard; Terraform for the EC2 host, security group, Elastic IP, and key pair in `deploy/terraform` with a README (no state committed). Acceptance: `terraform validate` passes; Grafana shows live metrics locally.

---

## 5. Benchmark label verification (the human bottleneck, made fast)

Wrong labels destroy your credibility, and manually verifying 60 cases is slow. Automate the checks, then spot-check.

`bench/verify_labels.py` must, for each case:
1. Run the base project's tests in the sandbox: they must pass.
2. Apply `patch.diff` and run tests again.
3. Check consistency with the label:
   - `type = clean` -> tests pass and Semgrep reports no new findings.
   - `type = logic_bug` (tests catch it) -> tests fail after the patch.
   - `type = subtle_bug` (not caught by tests) -> tests pass after the patch; you must confirm the bug by reading the diff.
   - `type = sql_injection | command_injection | unsafe_deserialization | secret` -> tests pass, and a manual-confirmation flag is set.
4. Output a table of cases that FAIL the consistency check, and a list of cases that need human confirmation.

You then: fix or delete inconsistent cases, and read about 15-20 cases yourself (all subtle bugs plus a random sample of the rest). Budget 2 hours. Record the process and limits in `bench/DATASET.md`.

If you end up with fewer than 60 verified cases, use what is verified (minimum 40) and state the actual number. Never keep unverified labels to hit a number.

**Running it:** the full run is 3 modes x N cases x 3 repeats. Use the LLM cache, run it in the background during Wave 3, and watch your rate limits. Split: tune weights on the train split only, run the test split once at the end.

---

## 6. Checkpoints (go/no-go)

| Checkpoint | Must be true |
|---|---|
| **C1 (H16)** | `make test` passes; a real PR on the test repo gets an engine review with a comment and status (Fake LLM is OK); gateway and dashboard run against fixtures; CI green |
| **C2 (H26)** | Real LLM produces reviews; webhook -> engine -> gateway -> dashboard works end to end; approve/reject writes an audit row; first deployment is live |
| **C3 (H32)** | Benchmark finished for all three modes; sandbox containment tests pass; prompt-injection tests pass; MCP server starts |
| **C4 (H39)** | Final deployment live; README has real numbers; demo video recorded; resume bullets filled with real results |

If a checkpoint is missed by more than 2 hours, do not start new lanes. Stabilize what exists and continue with the remaining items in this order: benchmark honesty and README first, then deployment, then hardening tests, then MCP, then Terraform and Grafana.

---

## 7. Integration commands (use these to verify, not agent claims)

```
make up && make test && make lint          # whole repo
make engine & make worker                   # engine API + worker
make gateway                                # Spring Boot
make dash                                   # dashboard
scripts/e2e.sh                              # signed webhook -> review -> decision
make bench                                  # all modes
docker ps -a                                # must show no leftover sandbox containers
curl -s localhost:8001/healthz ; curl -s localhost:8080/actuator/health
```

Local webhook tunnel: `smee --url <your smee channel> --target http://localhost:8080/webhooks/github`, and set that smee URL and your webhook secret in the test repo's GitHub webhook settings (event: Pull requests).

---

## 8. Real-world validation and showcase (H35-39)

1. Pick 3-5 small open-source Python repos with working test suites. Fork them. Make realistic changes on branches (one clean refactor, one with a seeded bug) and open PRs **on your forks** so AgentGate reviews them. Do not point the bot at repositories you do not control.
2. Submit 1-2 genuine upstream PRs (documentation fixes, small bug fixes, tests). These must be real, useful changes that follow each project's contribution guidelines. Acceptance by maintainers is not in your control, so the claim on your resume is "submitted" until merged.
3. Record in the README an honest "what it got wrong" section with 2-3 false positives and what you learned.
4. Screenshots: PR comment, PR detail with evidence badges, benchmark page, Grafana, CI run, MCP tool call.
5. Demo video per BUILD_PLAN 16.2. Resume bullets per 16.4, using only measured numbers.

---

## 9. What is most likely to go wrong, and the answer

| Risk | Early warning | Response |
|---|---|---|
| Agents produce conflicting code | merge conflicts, repeated contract requests | smaller lanes, rebase before each wave, keep folders disjoint |
| Docker sandbox misbehaves on Windows | tests pass locally in WSL but fail on host | develop inside WSL2; run sandbox tests in CI on Linux |
| LLM rate limits throttle the benchmark | 429s, slow runs | caching, batches, lower concurrency, secondary provider for benchmark only |
| AWS setup eats hours | no instance by H10 | launch the instance during Stage A while agents work; follow `docs/DEPLOY.md` exactly |
| Java gateway lags | Lane B not green by H9 | give B a second agent session to fix tests, keep scope to the contract, do not redesign |
| Benchmark labels contested | `verify_labels.py` shows many mismatches | delete bad cases, report the true count |
| You cannot explain the code | explain-it-back session stalls | ask the agent to simplify or add comments; remove anything you cannot defend |

---

## 10. Final submission checklist
- [ ] `main` is green in CI; tag `v1.0`
- [ ] Live link works from another network; demo credentials documented
- [ ] README has architecture diagram, benchmark table with dataset size and split, limitations, security notes, quick start
- [ ] Every number in the README and resume exists in `bench/results/` or a CI/test report
- [ ] No secrets in the repo (`git log -p` grep for tokens; rotate any that leaked)
- [ ] AWS billing alarm set; instance stopped or sized down after the demo window if cost matters
- [ ] DEVLOG, ADRs, and `docs/DEPLOY.md` committed
- [ ] You can explain every component and every design tradeoff aloud
