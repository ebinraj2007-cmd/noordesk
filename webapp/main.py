"""NoorDesk local dashboard (FastAPI).

Runs on 127.0.0.1 only. Serves a control-room dashboard and a small JSON API.
All message text is escaped in the browser (the frontend uses textContent), so
booby-trapped message content cannot execute in the owner's browser.
"""
from __future__ import annotations

import json
import os
from collections import Counter

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from noordesk.ingest import load_from_folder
from noordesk.pipeline import process_inbox
from noordesk import storage, profile as profiles, SUPPORTED_LANGUAGES

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLE = os.path.join(ROOT, "sample_data", "inbox")

app = FastAPI(title="NoorDesk", version="1.0.0")
# Allow the embeddable web chat widget (served from another local origin) to post.
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


def _apply_repeat(records):
    """Flag messages from senders we've seen before (returning customers)."""
    existing = {r["sender"] for r in storage.get_all() if r.get("sender")}
    for rec in records:
        if rec.get("sender") and rec["sender"] in existing:
            rec["repeat"] = 1
    return records


class RunRequest(BaseModel):
    inbox: str | None = None
    threshold: float = 0.65
    use_llm: bool = True


@app.post("/api/run")
def api_run(req: RunRequest):
    folder = req.inbox or SAMPLE
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
    id: str
    sender: str
    channel: str = "whatsapp"
    raw_text: str


@app.post("/api/ingest")
def api_ingest(msg: IngestMessage):
    """Receive a single live message (e.g. from the WhatsApp bridge), triage it,
    and store it so it appears on the dashboard."""
    records = process_inbox([msg.model_dump()], profile=profiles.load())
    _apply_repeat(records)
    storage.save_messages(records)
    return JSONResponse({"ok": True, "id": msg.id})


@app.get("/api/profile")
def api_get_profile():
    return JSONResponse(profiles.load())


class ProfileRequest(BaseModel):
    role: str = "personal"
    mode: str = "personal"
    name: str = ""
    sells: str = ""
    hours: str = ""
    phone: str = ""
    location: str = ""
    notes: str = ""
    tone: str = "friendly"
    products: list = []
    faqs: list = []
    vip: list = []
    away_enabled: bool = False
    open_time: str = "09:00"
    close_time: str = "18:00"


@app.get("/api/roles")
def api_roles():
    return JSONResponse([
        {"key": k, "label": v["label"], "personal": k in profiles.PERSONAL_ROLES}
        for k, v in profiles.ROLES.items()
    ])


@app.post("/api/profile")
def api_save_profile(req: ProfileRequest):
    saved = profiles.save(req.model_dump())
    return JSONResponse({"ok": True, "profile": saved})


class SendRequest(BaseModel):
    id: str


@app.post("/api/send")
def api_send(req: SendRequest):
    # Human-approved send. (In production this hands off to the channel adapter.)
    storage.set_status(req.id, "sent")
    return JSONResponse({"ok": True, "id": req.id})


class MarkRequest(BaseModel):
    id: str
    status: str = "done"


@app.post("/api/mark")
def api_mark(req: MarkRequest):
    """Move a message through the workflow: done / snoozed / reopen (new)."""
    status = req.status if req.status in ("new", "sent", "done", "snoozed") else "done"
    storage.set_status(req.id, status)
    return JSONResponse({"ok": True, "id": req.id, "status": status})


@app.post("/api/clear")
def api_clear():
    storage.clear()
    return JSONResponse({"ok": True})


# Static dashboard (mounted last so /api routes take precedence).
app.mount("/", StaticFiles(directory=os.path.join(HERE, "static"), html=True), name="static")
