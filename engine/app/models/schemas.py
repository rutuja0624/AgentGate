"""Pydantic v2 schemas for AgentGate Engine.

Source of truth for data models across reviewers, tools, API contracts,
and database persistence.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ReviewStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewVerdict(StrEnum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class ReviewMode(StrEnum):
    FULL = "full"
    LLM_ONLY = "llm_only"
    LLM_STATIC = "llm_static"


class ReviewerType(StrEnum):
    SECURITY = "security"
    CORRECTNESS = "correctness"
    DESIGN = "design"
    TESTS = "tests"
    STATIC = "static"


class FindingSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EvidenceType(StrEnum):
    TEST_FAILURE = "test_failure"
    STATIC_RULE = "static_rule"
    SECRET_MATCH = "secret_match"
    LLM_ONLY = "llm_only"


class ToolType(StrEnum):
    SEMGREP = "semgrep"
    RADON = "radon"
    SECRETS = "secrets"
    PYTEST = "pytest"


# ---------------------------------------------------------------------------
# Reviewer Output Schemas (Strict shape enforced on LLM output)
# ---------------------------------------------------------------------------


class ReviewerFinding(BaseModel):
    """Raw finding emitted by an LLM reviewer before deduplication and verification."""

    model_config = ConfigDict(extra="forbid")

    severity: FindingSeverity
    category: str = Field(..., description="Short slug e.g. sql_injection, prompt_injection, logic_bug")
    file: str = Field(..., description="Path of the affected file")
    line: int | None = Field(default=None, description="Line number if identifiable")
    title: str = Field(..., description="Single-line concise description")
    explanation: str = Field(..., description="Detailed explanation of the issue")
    suggested_fix: str | None = Field(default=None, description="Concrete fix or remediation advice")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="References to tool_run ids or test names confirming this issue",
    )


class ReviewerOutput(BaseModel):
    """Strict JSON schema required from every specialist LLM reviewer."""

    model_config = ConfigDict(extra="forbid")

    findings: list[ReviewerFinding] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Domain Models (Finding, ToolRun, Impact)
# ---------------------------------------------------------------------------


class Finding(BaseModel):
    """Normalized finding with verification status and evidence payload."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    review_id: UUID | None = None
    reviewer: ReviewerType
    severity: FindingSeverity
    category: str
    file: str
    line: int | None = None
    title: str
    explanation: str
    suggested_fix: str | None = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_type: EvidenceType
    evidence: dict[str, Any] = Field(default_factory=dict)
    verified: bool = False


class ToolRun(BaseModel):
    """Execution summary of an analysis or sandbox tool."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=uuid4)
    review_id: UUID | None = None
    tool: ToolType
    exit_code: int
    duration_ms: int
    summary: dict[str, Any] = Field(default_factory=dict)
    raw_output_ref: str | None = None


class Impact(BaseModel):
    """Reverse dependency relationship determined via AST code graph."""

    model_config = ConfigDict(from_attributes=True)

    changed_file: str
    impacted_file: str
    distance: int = Field(..., ge=1, le=3)


# ---------------------------------------------------------------------------
# Risk Scoring Schemas
# ---------------------------------------------------------------------------


class RiskBreakdown(BaseModel):
    has_new_test_failure: bool = False
    has_confirmed_critical: bool = False
    count_verified_high: int = 0
    count_unverified_high: int = 0
    count_medium: int = 0
    secrets_found: int = 0
    complexity_increase_total: float = 0.0
    impacted_modules_count: int = 0
    diff_lines: int = 0


class RiskResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    verdict: ReviewVerdict
    breakdown: RiskBreakdown


# ---------------------------------------------------------------------------
# Engine API Request & Response Schemas
# ---------------------------------------------------------------------------


class ReviewCreateRequest(BaseModel):
    repo: str = Field(..., examples=["octocat/Hello-World"])
    pr_number: int = Field(..., examples=[42])
    head_sha: str = Field(..., min_length=40, max_length=64, examples=["8c3d9a1f2b4e6d7c8a9b0c1d2e3f4a5b6c7d8e9f"])
    base_sha: str | None = Field(default=None, examples=["1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b"])
    mode: ReviewMode = Field(default=ReviewMode.FULL)


class ReviewQueuedResponse(BaseModel):
    review_id: UUID
    status: ReviewStatus = ReviewStatus.QUEUED


class ReviewSummary(BaseModel):
    id: UUID
    repo: str
    pr_number: int
    head_sha: str
    status: ReviewStatus
    risk_score: int | None = None
    verdict: ReviewVerdict | None = None
    mode: ReviewMode
    duration_ms: int | None = None
    created_at: datetime
    completed_at: datetime | None = None


class ReviewDetail(ReviewSummary):
    base_sha: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    error: str | None = None
    findings: list[Finding] = Field(default_factory=list)
    tool_runs: list[ToolRun] = Field(default_factory=list)
    impact: list[Impact] = Field(default_factory=list)


class ReviewStatusUpdateRequest(BaseModel):
    state: str = Field(..., pattern="^(approved|rejected)$")
    by: str
    comment: str


class AnalyzeDiffRequest(BaseModel):
    diff: str
    context_files: list[str] = Field(default_factory=list)
    mode: ReviewMode = Field(default=ReviewMode.LLM_STATIC)


class AnalyzeDiffResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    verdict: ReviewVerdict
    findings: list[Finding] = Field(default_factory=list)
