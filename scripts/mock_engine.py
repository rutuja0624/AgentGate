#!/usr/bin/env python3
"""Mock AgentGate Engine server.

Serves contract fixtures for local development of Gateway (Lane B), Dashboard (Lane C),
and integration testing without requiring the full worker/sandbox stack.

Usage:
    python scripts/mock_engine.py [--port 8001]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

# Ensure engine package is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "engine"))

from app.models.schemas import (
    AnalyzeDiffRequest,
    AnalyzeDiffResponse,
    ReviewCreateRequest,
    ReviewDetail,
    ReviewQueuedResponse,
    ReviewStatus,
    ReviewStatusUpdateRequest,
    ReviewSummary,
    ReviewVerdict,
)

FIXTURES_DIR = REPO_ROOT / "docs" / "contracts" / "fixtures"

app = FastAPI(
    title="AgentGate Mock Engine",
    description="Mock engine server serving validated contract fixtures.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INTERNAL_TOKEN = os.getenv("ENGINE_INTERNAL_TOKEN", "agentgate_internal_secret_change_in_prod")


def _load_fixture(name: str) -> dict[str, Any]:
    fixture_path = FIXTURES_DIR / name
    if not fixture_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fixture {name} not found",
        )
    with open(fixture_path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


# In-memory store of mock reviews
REVIEWS_STORE: dict[str, dict[str, Any]] = {}


def _verify_token(x_internal_token: str | None) -> None:
    expected = os.getenv("ENGINE_INTERNAL_TOKEN", INTERNAL_TOKEN)
    if not x_internal_token or x_internal_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Internal-Token header",
        )


@app.get("/healthz", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "agentgate-mock-engine", "version": "0.1.0"}


@app.post(
    "/internal/reviews",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ReviewQueuedResponse,
    tags=["Reviews"],
)
async def create_review(
    req: ReviewCreateRequest,
    x_internal_token: str | None = Header(default=None),
) -> ReviewQueuedResponse:
    _verify_token(x_internal_token)

    review_id = str(uuid4())

    # Pick fixture based on PR number convention
    if req.pr_number == 13:
        fixture = _load_fixture("block_review.json")
    elif req.pr_number == 14:
        fixture = _load_fixture("failed_review.json")
    else:
        fixture = _load_fixture("clean_review.json")

    mock_review = dict(fixture)
    mock_review["id"] = review_id
    mock_review["repo"] = req.repo
    mock_review["pr_number"] = req.pr_number
    mock_review["head_sha"] = req.head_sha
    mock_review["base_sha"] = req.base_sha

    REVIEWS_STORE[review_id] = mock_review

    return ReviewQueuedResponse(review_id=UUID(review_id), status=ReviewStatus.QUEUED)


@app.get("/internal/reviews/{review_id}", response_model=ReviewDetail, tags=["Reviews"])
async def get_review(
    review_id: UUID,
    x_internal_token: str | None = Header(default=None),
) -> ReviewDetail:
    _verify_token(x_internal_token)

    sid = str(review_id)
    if sid in REVIEWS_STORE:
        return ReviewDetail.model_validate(REVIEWS_STORE[sid])

    # Fallback to block_review if id matches fixture id
    block_data = _load_fixture("block_review.json")
    if sid == block_data["id"]:
        return ReviewDetail.model_validate(block_data)

    clean_data = _load_fixture("clean_review.json")
    if sid == clean_data["id"]:
        return ReviewDetail.model_validate(clean_data)

    # Return clean fixture modified with requested ID
    clean_copy = dict(clean_data)
    clean_copy["id"] = sid
    return ReviewDetail.model_validate(clean_copy)


@app.get("/internal/reviews", tags=["Reviews"])
async def list_reviews(
    repo: str | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    x_internal_token: str | None = Header(default=None),
) -> dict[str, Any]:
    _verify_token(x_internal_token)

    items = []
    # Seed default fixtures if store empty
    if not REVIEWS_STORE:
        for f in ["clean_review.json", "block_review.json", "failed_review.json"]:
            data = _load_fixture(f)
            items.append(ReviewSummary.model_validate(data))
    else:
        for r in REVIEWS_STORE.values():
            if not repo or r.get("repo") == repo:
                items.append(ReviewSummary.model_validate(r))

    return {"items": items[:limit], "next_cursor": None}


@app.post("/internal/reviews/{review_id}/status", tags=["Reviews"])
async def update_status(
    review_id: UUID,
    payload: ReviewStatusUpdateRequest,
    x_internal_token: str | None = Header(default=None),
) -> dict[str, str]:
    _verify_token(x_internal_token)
    sid = str(review_id)
    if sid in REVIEWS_STORE:
        REVIEWS_STORE[sid]["status"] = "completed"

    github_status = "success" if payload.state == "approved" else "failure"
    return {"status": "updated", "github_status_set": github_status}


@app.post("/internal/analyze-diff", response_model=AnalyzeDiffResponse, tags=["Analysis"])
async def analyze_diff(
    payload: AnalyzeDiffRequest,
    x_internal_token: str | None = Header(default=None),
) -> AnalyzeDiffResponse:
    _verify_token(x_internal_token)

    # If diff contains sql injection keywords, simulate block
    if "SELECT" in payload.diff or "INSERT" in payload.diff or "%s" in payload.diff:
        fixture = _load_fixture("block_review.json")
        return AnalyzeDiffResponse(
            risk_score=fixture["risk_score"],
            verdict=ReviewVerdict.BLOCK,
            findings=fixture["findings"],
        )

    clean = _load_fixture("clean_review.json")
    return AnalyzeDiffResponse(
        risk_score=clean["risk_score"],
        verdict=ReviewVerdict.APPROVE,
        findings=clean["findings"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="AgentGate Mock Engine")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on (default: 8001)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface")
    args = parser.parse_args()

    uvicorn.run("scripts.mock_engine:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
