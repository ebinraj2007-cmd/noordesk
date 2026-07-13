"""Owner Translation View.

The rule engine cannot do full free-text translation offline, so it produces an
honest English *summary* of the message (language + intent + tone). When the LLM
engine is enabled, this is replaced by a real translation. Either way the owner
gets an English understanding of every message.
"""
from __future__ import annotations

from . import SUPPORTED_LANGUAGES

INTENT_GLOSS = {
    "booking": "wants to make a booking / appointment",
    "complaint": "is making a complaint",
    "price_enquiry": "is asking about pricing",
    "support": "needs help / support",
    "spam": "looks like spam / promotional",
    "general": "sent a general message",
}


def summarise(lang: str, intent: str, sentiment: str) -> str:
    """Offline English gloss of a message."""
    language = SUPPORTED_LANGUAGES.get(lang, "Unknown")
    tone = " (customer sounds upset)" if sentiment == "angry" else ""
    return f"[{language}] Customer {INTENT_GLOSS.get(intent, 'sent a message')}{tone}."
