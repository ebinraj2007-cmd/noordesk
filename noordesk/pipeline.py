"""Orchestrates: ingest -> detect -> classify -> respond -> translate -> escalate.

Produces one record per message, ready to store and display.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone, time as _time
from typing import List, Dict, Optional

from .detect import detect_language
from .classifier import classify
from .responder import draft_reply
from .translate import summarise
from .escalation import needs_review, DEFAULT_THRESHOLD
from .scam import detect_scam
from . import llm, local_llm, profile as profiles


def _context(profile: Optional[dict]) -> str:
    """Turn the user's profile into a short instruction the AI can use."""
    p = profile or {}
    now = "Right now it is " + datetime.now().strftime("%A %d %B %Y, %I:%M %p") + ". "
    if p.get("mode") == "business":
        noun = profiles.ROLES.get(p.get("role") or "other", {}).get("noun", "a small business")
        bits = []
        if p.get("name"):
            bits.append("name: " + str(p["name"]))
        if p.get("sells"):
            bits.append("offers: " + str(p["sells"]))
        if p.get("hours"):
            bits.append("hours: " + str(p["hours"]))
        if p.get("location"):
            bits.append("location: " + str(p["location"]))
        prods = [q for q in (p.get("products") or []) if q.get("name")]
        prodstr = "; ".join(
            (q["name"] + (" = " + q["price"] if q.get("price") else "")) for q in prods[:25]
        )
        tone = p.get("tone") or "friendly"
        ctx = "You draft customer-service replies for " + noun + ". "
        if bits:
            ctx += "; ".join(bits) + ". "
        if prodstr:
            ctx += ("Products & prices: " + prodstr
                    + ". Quote these exact prices when asked; never invent prices. ")
        faqs = [f for f in (p.get("faqs") or []) if f.get("q") and f.get("a")]
        if faqs:
            ctx += ("Known answers (use verbatim when relevant): "
                    + " | ".join("Q: " + f["q"] + " A: " + f["a"] for f in faqs[:15]) + ". ")
        ctx += "Tone: " + tone + ". Do not invent facts not given here."
        return now + ctx
    name = (p.get("name") or "").strip()
    ident = (" Your name is " + name + " — if the customer asks your name, tell them."
             if name else "")
    return (now + "You are a warm, helpful personal assistant chatting on behalf of "
            + (name or "the user") + " (an individual, not a business)." + ident
            + " Reply conversationally and actually answer their question. Do not"
            + " invent products, prices, or business hours you weren't given.")


AWAY_NOTE = {
    "en": " (We're currently closed — we'll get back to you when we reopen.)",
    "ar": " (نحن مغلقون حاليًا — سنعاود التواصل عند إعادة الفتح.)",
    "ml": " (ഞങ്ങൾ ഇപ്പോൾ അടച്ചിരിക്കുന്നു — തുറക്കുമ്പോൾ ബന്ധപ്പെടാം.)",
    "ta": " (நாங்கள் இப்போது மூடப்பட்டுள்ளோம் — திறந்ததும் தொடர்பு கொள்கிறோம்.)",
    "fr": " (Nous sommes actuellement fermés — nous vous répondrons à la réouverture.)",
}


def _tokens(s: str):
    return set(w for w in re.findall(r"\w+", (s or "").lower(), re.UNICODE) if len(w) >= 3)


def _faq_answer(text: str, profile: dict):
    """Return an exact FAQ answer if the message matches one, else None."""
    ttok = _tokens(text)
    if not ttok:
        return None
    best, best_n = None, 0
    for f in profile.get("faqs") or []:
        qtok = _tokens(f.get("q", ""))
        if not qtok:
            continue
        overlap = len(qtok & ttok)
        if qtok.issubset(ttok) or overlap >= 2:
            if overlap > best_n:
                best, best_n = f.get("a"), overlap
    return best


def _parse_hm(hhmm: str) -> _time:
    h, m = (hhmm or "09:00").split(":")[:2]
    return _time(int(h), int(m))


def _after_hours(profile: dict) -> bool:
    if not profile.get("away_enabled"):
        return False
    try:
        now = datetime.now().time()
        o = _parse_hm(profile.get("open_time", "09:00"))
        c = _parse_hm(profile.get("close_time", "18:00"))
    except Exception:
        return False
    if o <= c:
        return not (o <= now <= c)
    return not (now >= o or now <= c)   # overnight hours


def process_message(msg: Dict, profile: Optional[dict] = None,
                    threshold: float = DEFAULT_THRESHOLD,
                    use_llm: bool = True) -> Dict:
    profile = profile or {}
    raw = msg.get("raw_text", "")
    sender = msg.get("sender", "")
    lang, lang_conf = detect_language(raw)
    intent, priority, intent_conf, sentiment = classify(raw)
    is_scam, scam_score, scam_reasons = detect_scam(raw)

    # Reply: scam -> none; else an exact FAQ answer if one matches, else a draft.
    faq_used = False
    if is_scam:
        reply = ""
    else:
        fa = _faq_answer(raw, profile) if profile.get("mode") == "business" else None
        if fa:
            reply, faq_used = fa, True
        else:
            reply = draft_reply(intent, lang, profile, raw)
    engine = "faq" if faq_used else "rule"
    context = _context(profile)

    # Optional AI polish (skipped for exact FAQ answers so they stay verbatim).
    # Preference: local offline model (Ollama) first, then cloud (Claude).
    if use_llm and reply and not faq_used:
        if local_llm.is_enabled():
            refined = local_llm.refine_reply(raw, lang, reply, context)
            if refined:
                reply = refined
                engine = "local"
        if engine == "rule" and llm.is_enabled():
            refined = llm.refine_reply(raw, lang, reply, context)
            if refined:
                reply = refined
                engine = "llm"

    # Away-hours: append a localized "we're closed" note to a real reply.
    after_hours = bool(reply) and _after_hours(profile)
    if after_hours:
        reply += AWAY_NOTE.get(lang, AWAY_NOTE["en"])

    translation = summarise(lang, intent, sentiment)
    review = needs_review(lang_conf, intent_conf, sentiment, threshold) or is_scam
    vip = 1 if sender and sender in (profile.get("vip") or []) else 0

    return {
        "id": msg.get("id"),
        "sender": sender,
        "channel": msg.get("channel", "manual"),
        "raw_text": raw,
        "detected_language": lang,
        "language_confidence": round(lang_conf, 3),
        "intent": intent,
        "priority": priority,
        "sentiment": sentiment,
        "suggested_reply": reply,
        "translation": translation,
        "engine_used": engine,
        "needs_review": 1 if review else 0,
        "scam": 1 if is_scam else 0,
        "scam_score": scam_score,
        "scam_reasons": "; ".join(scam_reasons),
        "vip": vip,
        "repeat": 0,        # filled in by the app layer using message history
        "after_hours": 1 if after_hours else 0,
        "status": "new",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def process_inbox(messages: List[Dict], profile: Optional[dict] = None,
                  threshold: float = DEFAULT_THRESHOLD,
                  use_llm: bool = True) -> List[Dict]:
    return [process_message(m, profile, threshold, use_llm) for m in messages]
