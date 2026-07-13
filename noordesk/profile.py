"""User profile / role configuration.

Lets each user pick a role (shop, restaurant, clinic, freelancer, student, …) and
optionally feed in products & prices, so replies — and the AI — are tailored.
Stored as JSON in the user's home dir (not in the repo).
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

_DIR = os.path.join(os.path.expanduser("~"), ".noordesk")


def _path() -> str:
    """Resolve the profile path at call time (NOORDESK_PROFILE overrides)."""
    return os.environ.get("NOORDESK_PROFILE", os.path.join(_DIR, "profile.json"))


# role key -> (label, description-for-AI). Personal roles get no product/pricing.
ROLES: Dict[str, Dict[str, str]] = {
    "shop":        {"label": "Retail shop",        "noun": "a retail shop"},
    "restaurant":  {"label": "Restaurant / café",  "noun": "a restaurant or café"},
    "ecommerce":   {"label": "Online store",       "noun": "an online store"},
    "clinic":      {"label": "Clinic / dental",    "noun": "a clinic or dental practice"},
    "salon":       {"label": "Salon / spa",        "noun": "a salon or spa"},
    "realestate":  {"label": "Real estate",        "noun": "a real estate agency"},
    "services":    {"label": "Services / repairs", "noun": "a service business (repairs, cleaning, etc.)"},
    "hospitality": {"label": "Hotel / stays",      "noun": "a hotel or guesthouse"},
    "education":   {"label": "Tutor / classes",    "noun": "a tutoring or education service"},
    "freelancer":  {"label": "Freelancer",         "noun": "a freelancer or creator"},
    "events":      {"label": "Events / bookings",  "noun": "an events or bookings business"},
    "other":       {"label": "Other business",     "noun": "a small business"},
    "student":     {"label": "Student",            "noun": "a student (personal use)"},
    "personal":    {"label": "Just me / personal", "noun": "an individual (personal use)"},
}

PERSONAL_ROLES = {"student", "personal"}


def mode_for(role: str) -> str:
    return "personal" if role in PERSONAL_ROLES else "business"


DEFAULT: Dict = {
    "mode": "personal",
    "role": "personal",
    "name": "",
    "sells": "",
    "hours": "",
    "phone": "",
    "location": "",
    "notes": "",
    "tone": "friendly",     # "friendly" | "formal" | "brief"
    "products": [],          # [{name, price, note}]
    "faqs": [],              # [{q, a}]
    "vip": [],               # [sender strings to prioritise]
    "away_enabled": False,   # append an "we're closed" note outside hours
    "open_time": "09:00",
    "close_time": "18:00",
    "configured": False,
}


def _clean_products(raw) -> List[Dict]:
    out: List[Dict] = []
    for p in (raw or [])[:100]:
        if not isinstance(p, dict):
            continue
        name = str(p.get("name", "")).strip()[:80]
        if not name:
            continue
        out.append({
            "name": name,
            "price": str(p.get("price", "")).strip()[:40],
            "note": str(p.get("note", "")).strip()[:160],
        })
    return out


def _clean_faqs(raw) -> List[Dict]:
    out: List[Dict] = []
    for f in (raw or [])[:100]:
        if not isinstance(f, dict):
            continue
        q = str(f.get("q", "")).strip()[:160]
        a = str(f.get("a", "")).strip()[:600]
        if q and a:
            out.append({"q": q, "a": a})
    return out


def _clean_vip(raw) -> List[str]:
    out = []
    for v in (raw or [])[:200]:
        s = str(v).strip()[:120]
        if s:
            out.append(s)
    return out


def load() -> Dict:
    try:
        with open(_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = {**DEFAULT, **data}
        merged["products"] = _clean_products(merged.get("products"))
        merged["faqs"] = _clean_faqs(merged.get("faqs"))
        merged["vip"] = _clean_vip(merged.get("vip"))
        return merged
    except Exception:
        return dict(DEFAULT)


def save(profile: Dict) -> Dict:
    clean = {k: profile.get(k, DEFAULT[k]) for k in DEFAULT}
    role = clean.get("role") or "personal"
    if role not in ROLES:
        role = "personal"
    clean["role"] = role
    clean["mode"] = mode_for(role)
    clean["products"] = _clean_products(profile.get("products"))
    clean["faqs"] = _clean_faqs(profile.get("faqs"))
    clean["vip"] = _clean_vip(profile.get("vip"))
    clean["away_enabled"] = bool(profile.get("away_enabled"))
    clean["open_time"] = str(profile.get("open_time") or "09:00")[:5]
    clean["close_time"] = str(profile.get("close_time") or "18:00")[:5]
    clean["configured"] = True
    path = _path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)
    return clean
