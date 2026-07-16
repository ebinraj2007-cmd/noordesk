"""NoorDesk dashboard (FastAPI).

Runs on 127.0.0.1 by default. Serves a control-room dashboard and a small JSON
API. Hardened against the standard pre-deployment checklist:

  1. Authorization  - state-changing endpoints require the operator token
                      (NOORDESK_TOKEN) when one is configured.
  3. Input validation - Pydantic models with length caps; path-traversal guard
                      on the inbox folder; parameterised SQL in storage.py.
  4. CORS           - restricted to configured origins (NOORDESK_ORIGINS),
                      not a wildcard.
  5. Rate limiting  - per-IP sliding window, stricter on expensive endpoints.
  6. Error handling - custom handlers return structured JSON; no stack traces.
  8. Logging/health - structured request logging + /healthz.
"""
from __future__ import annotations

import json
import logging
import os
import time
from collections import Counter

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from noordesk.ingest import load_from_folder
from noordesk.pipeline import process_inbox
from noordesk import storage, profile as profiles, SUPPORTED_LANGUAGES
from webapp.security import require_token, rate_check, safe_inbox_path, token_configured

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLE = os.path.join(ROOT, "sample_data", "inbox")

# ---- logging (checklist #8) ------------------------------------------------
logging.basicConfig(
    level=os.environ.get("NOORDESK_LOG_LEVEL", "INFO"),
    format='{"ts":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
log = logging.getLogger("noordesk")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not token_configured():
        log.warning("NOORDESK_TOKEN not set - running in trusted local mode; "
                    "set it before exposing NoorDesk beyond 127.0.0.1")
    yield


app = FastAPI(title="NoorDesk", version="1.1.0", lifespan=lifespan)


# ---- CORS: locked to configured origins, not '*' (checklist #4) ------------
_origins = os.environ.get(
    "NOORDESK_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---- rate limiting + request logging middleware (checklist #5, #8) ---------
@app.middleware("http")
async def _guard(request: Request, call_next):
    if request.url.path.startswith("/api/") and not rate_check(request):
        log.warning("rate limit exceeded path=%s", request.url.path)
        return JSONResponse(status_code=429, content={"error": "Too many requests. Slow down."})
    start = time.monotonic()
    response = await call_next(request)
    dur = (time.monotonic() - start) * 1000
    if request.url.path.startswith("/api/"):
        log.info("request path=%s status=%s ms=%.1f", request.url.path, response.status_code, dur)
    return response


# ---- custom error handlers: no stack traces to the client (checklist #6) ---
@app.exception_handler(HTTPException)
async def _http_err(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    log.exception("unhandled error path=%s", request.url.path)  # full detail server-side only
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/healthz")
def healthz():
    """Liveness/readiness probe for monitoring (checklist #8)."""
    try:
        storage.get_all()
        return {"status": "ok", "auth": "on" if token_configured() else "local"}
    except Exception:
        raise HTTPException(status_code=503, detail="storage unavailable")


def _apply_repeat(records):
    existing = {r["sender"] for r in storage.get_all() if r.get("sender")}
    for rec in records:
        if rec.get("sender") and rec["sender"] in existing:
            rec["repeat"] = 1
    return records


# ---- request models with length caps (checklist #3) ------------------------
class RunRequest(BaseModel):
    inbox: str | None = Field(default=None, max_length=200)
    threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    use_llm: bool = True


@app.post("/api/run", dependencies=[Depends(require_token)])
def api_run(req: RunRequest):
    folder = safe_inbox_path(req.inbox, SAMPLE, ROOT)
    messages = load_from_folder(folder)
    records = process_inbox(messages, profile=profiles.load(),
                            threshold=req.threshold, use_llm=req.use_llm)
    _apply_repeat(records)
    storage.save_messages(records)
    return JSONResponse({"processed": len(records)})


@app.get("/api/messages")
def api_messages():
    return JSONResponse(storage.get_all())


@app.get("/api/stats")
def api_stats():
    rows = storage.get_all()
    langs = Counter(SUPPORTED_LANGUAGES.get(r["detected_language"], "Other") for r in rows)
    intents = Counter(r["intent"] for r in rows)
    engines = Counter(r["engine_used"] for r in rows)
    return JSONResponse({
        "total": len(rows),
        "needs_review": sum(1 for r in rows if r["needs_review"]),
        "by_language": dict(langs),
        "by_intent": dict(intents),
        "by_engine": dict(engines),
    })


class IngestMessage(BaseModel):
    id: str = Field(max_length=200)
    sender: str = Field(max_length=200)
    channel: str = Field(default="whatsapp", max_length=40)
    raw_text: str = Field(max_length=8000)


@app.post("/api/ingest", dependencies=[Depends(require_token)])
def api_ingest(msg: IngestMessage):
    records = process_inbox([msg.model_dump()], profile=profiles.load())
    _apply_repeat(records)
    storage.save_messages(records)
    return JSONResponse({"ok": True, "id": msg.id})


@app.get("/api/profile")
def api_get_profile():
    return JSONResponse(profiles.load())


class ProfileRequest(BaseModel):
    role: str = Field(default="personal", max_length=40)
    mode: str = Field(default="personal", max_length=40)
    name: str = Field(default="", max_length=120)
    sells: str = Field(default="", max_length=400)
    hours: str = Field(default="", max_length=120)
    phone: str = Field(default="", max_length=40)
    location: str = Field(default="", max_length=120)
    notes: str = Field(default="", max_length=2000)
    tone: str = Field(default="friendly", max_length=40)
    products: list = Field(default_factory=list)
    faqs: list = Field(default_factory=list)
    vip: list = Field(default_factory=list)
    away_enabled: bool = False
    open_time: str = Field(default="09:00", max_length=5)
    close_time: str = Field(default="18:00", max_length=5)


@app.get("/api/roles")
def api_roles():
    return JSONResponse([
        {"key": k, "label": v["label"], "personal": k in profiles.PERSONAL_ROLES}
        for k, v in profiles.ROLES.items()
    ])


@app.post("/api/profile", dependencies=[Depends(require_token)])
def api_save_profile(req: ProfileRequest):
    saved = profiles.save(req.model_dump())
    return JSONResponse({"ok": True, "profile": saved})


class SendRequest(BaseModel):
    id: str = Field(max_length=200)


@app.post("/api/send", dependencies=[Depends(require_token)])
def api_send(req: SendRequest):
    storage.set_status(req.id, "sent")
    return JSONResponse({"ok": True, "id": req.id})


class MarkRequest(BaseModel):
    id: str = Field(max_length=200)
    status: str = Field(default="done", max_length=20)


@app.post("/api/mark", dependencies=[Depends(require_token)])
def api_mark(req: MarkRequest):
    status = req.status if req.status in ("new", "sent", "done", "snoozed") else "done"
    storage.set_status(req.id, status)
    return JSONResponse({"ok": True, "id": req.id, "status": status})


@app.post("/api/clear", dependencies=[Depends(require_token)])
def api_clear():
    storage.clear()
    return JSONResponse({"ok": True})


# Static dashboard (mounted last so /api routes take precedence).
app.mount("/", StaticFiles(directory=os.path.join(HERE, "static"), html=True), name="static")
