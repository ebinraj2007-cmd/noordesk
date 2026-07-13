"""Confidence-based human escalation.

If the app is not confident enough, flag the message for a human instead of
presenting an auto-reply as send-ready.
"""
from __future__ import annotations

DEFAULT_THRESHOLD = 0.65


def needs_review(language_confidence: float, intent_confidence: float,
                 sentiment: str, threshold: float = DEFAULT_THRESHOLD) -> bool:
    if language_confidence < threshold:
        return True
    if intent_confidence < threshold:
        return True
    # Angry customers always get a human eye before sending.
    if sentiment == "angry":
        return True
    return False
