"""HTTP API. Run: uvicorn app.main:app"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import audit, documents, providers
from app.auth import KeyStore, User
from app.config import Settings
from app.pipeline import Pipeline
from app.ratelimit import RateLimiter
from app.retrieval import Index

settings = Settings()
index = Index(documents.load(settings.docs_dir, scan_threshold=settings.injection_threshold))
pipeline = Pipeline(settings, index, providers.get(settings.provider, settings.model))
keys = KeyStore(settings.users_file)
limiter = RateLimiter(settings.rate_per_minute)

app = FastAPI(title="Secure LLM Gateway", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.update(
        {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
            "Cache-Control": "no-store",
        }
    )
    return response


class AskRequest(BaseModel):
    # Hard ceiling at the HTTP layer; the pipeline applies the configurable, lower limit.
    question: str = Field(min_length=1, max_length=20_000)


def current_user(x_api_key: str | None = Header(default=None)) -> User:
    user = keys.authenticate(x_api_key)
    if not user:
        raise HTTPException(status_code=401, detail="invalid or missing API key")
    if not limiter.allow(user.user_id):
        raise HTTPException(status_code=429, detail="rate limit exceeded")
    return user


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "provider": pipeline.provider.name, "chunks": len(index.chunks)}


@app.post("/v1/ask")
def ask(body: AskRequest, user: User = Depends(current_user)) -> dict:
    if settings.disabled or os.environ.get("GATEWAY_DISABLED") == "true":
        raise HTTPException(status_code=503, detail="the assistant is temporarily disabled")
    return pipeline.ask(user, body.question).public()


@app.get("/v1/audit/verify")
def verify_audit(user: User = Depends(current_user)) -> dict:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    ok, n, msg = audit.verify(settings.audit_path)
    return {"intact": ok, "records": n, "message": msg}


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception) -> JSONResponse:
    # Never return stack traces or provider errors (which can echo prompts) to the client.
    return JSONResponse(status_code=500, content={"detail": "internal error"})
