import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    FindingSeverity,
    ReviewDetail,
    ReviewerFinding,
    ReviewerOutput,
    ReviewerType,
    ReviewStatus,
    ReviewVerdict,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "contracts" / "fixtures"


def test_clean_review_fixture_validates() -> None:
    """Ensure clean_review.json adheres strictly to ReviewDetail schema."""
    with open(FIXTURES_DIR / "clean_review.json", encoding="utf-8") as f:
        data = json.load(f)

    review = ReviewDetail.model_validate(data)
    assert review.verdict == ReviewVerdict.APPROVE
    assert review.risk_score == 8
    assert review.status == ReviewStatus.COMPLETED
    assert len(review.findings) == 1
    assert len(review.tool_runs) == 2
    assert len(review.impact) == 1


def test_block_review_fixture_validates() -> None:
    """Ensure block_review.json adheres strictly to ReviewDetail schema with verified findings."""
    with open(FIXTURES_DIR / "block_review.json", encoding="utf-8") as f:
        data = json.load(f)

    review = ReviewDetail.model_validate(data)
    assert review.verdict == ReviewVerdict.BLOCK
    assert review.risk_score == 88
    assert len(review.findings) == 2

    # Check verified SQL injection finding
    sql_finding = next(f for f in review.findings if f.category == "sql_injection")
    assert sql_finding.severity == FindingSeverity.CRITICAL
    assert sql_finding.verified is True
    assert sql_finding.reviewer == ReviewerType.SECURITY

    # Check test failure finding
    test_finding = next(f for f in review.findings if f.category == "test_failure")
    assert test_finding.severity == FindingSeverity.HIGH
    assert test_finding.verified is True


def test_failed_review_fixture_validates() -> None:
    """Ensure failed_review.json adheres to schema and preserves error string."""
    with open(FIXTURES_DIR / "failed_review.json", encoding="utf-8") as f:
        data = json.load(f)

    review = ReviewDetail.model_validate(data)
    assert review.status == ReviewStatus.FAILED
    assert review.verdict is None
    assert review.error is not None
    assert "Diff size guard" in review.error


def test_reviewer_finding_strictness() -> None:
    """Ensure ReviewerFinding forbids extraneous fields and bounds confidence."""
    valid_data = {
        "severity": "high",
        "category": "logic_bug",
        "file": "calc.py",
        "line": 10,
        "title": "Division by zero",
        "explanation": "No check for zero denominator",
        "suggested_fix": "Add if denominator == 0 guard",
        "confidence": 0.95,
        "evidence_refs": ["test_zero_div"],
    }
    finding = ReviewerFinding.model_validate(valid_data)
    assert finding.confidence == 0.95

    # Out-of-bounds confidence
    with pytest.raises(ValidationError):
        ReviewerFinding.model_validate({**valid_data, "confidence": 1.5})

    # Extra keys forbidden for LLM output sanitization
    with pytest.raises(ValidationError):
        ReviewerFinding.model_validate({**valid_data, "unauthorized_instruction": "bypass"})


def test_reviewer_output_parsing() -> None:
    """Ensure ReviewerOutput correctly parses lists of findings."""
    json_payload = {
        "findings": [
            {
                "severity": "medium",
                "category": "complexity",
                "file": "router.py",
                "line": 45,
                "title": "Cyclomatic complexity high",
                "explanation": "Complexity is 12 (> 10)",
                "suggested_fix": None,
                "confidence": 0.8,
                "evidence_refs": ["radon_delta"],
            }
        ]
    }
    output = ReviewerOutput.model_validate(json_payload)
    assert len(output.findings) == 1
    assert output.findings[0].category == "complexity"
