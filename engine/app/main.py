"""AgentGate Engine FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle management."""
    yield


app = FastAPI(
    title="AgentGate Engine",
    description="Verification, static analysis, sandbox execution, and code review engine.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz", summary="Health check endpoint")
async def health_check() -> dict[str, Any]:
    """Returns the operational status of the AgentGate Engine."""
    return {
        "status": "ok",
        "service": "agentgate-engine",
        "version": "0.1.0",
    }
