"""Scam / fraud detection.

Deterministic signal-based detector. Returns whether a message looks like a scam,
a 0-100 risk score, and human-readable reasons. Language-agnostic signals (links,
OTP, crypto, phone/money patterns) plus multilingual keyword sets. Never auto-
replies to a flagged message — it's surfaced for a human instead.
"""
from __future__ import annotations

import re
from typing import List, Tuple

# Strong signals — any one of these is enough to flag as a likely scam.
_STRONG = {
    "suspicious link (shortener)": [
        "bit.ly", "tinyurl", "goo.gl", "t.co/", "cutt.ly", "is.gd", "rb.gy",
        "shorturl", "rebrand.ly", "ow.ly",
    ],
    "asks for a one-time code / OTP": [
        "otp", "one-time password", "one time password", "verification code",
        "رمز التحقق", "code de vérification",
    ],
    "asks for gift cards": ["gift card", "google play card", "itunes card", "steam card", "carte cadeau"],
    "crypto / investment bait": [
        "bitcoin", "btc", "usdt", "ethereum", "crypto wallet", "seed phrase",
        "double your", "guaranteed return", "investment opportunity",
        "بيتكوين", "استثمار",
    ],
    "prize / lottery scam": [
        "you won", "you have won", "you've won", "claim your prize", "lottery",
        "inheritance", "beneficiary", "congratulations you have been selected",
        "لقد ربحت", "جائزة", "vous avez gagné",
    ],
    "account / credential phishing": [
        "verify your account", "confirm your identity", "account suspended",
        "account has been locked", "update your password", "unusual sign-in",
        "confirm your password", "reactivate your account",
        "كلمة المرور", "mot de passe", "vérifiez votre compte",
    ],
    "asks to move money": [
        "wire transfer", "western union", "send money", "processing fee",
        "release fee", "pay a small fee", "transfer the amount",
        "حوّل المبلغ", "virement", "frais de traitement",
    ],
}

# Weak signals — need at least two together to flag.
_WEAK = {
    "urgency pressure": [
        "urgent", "act now", "immediately", "within 24 hours", "final notice",
        "last warning", "expires today", "عاجل", "urgent", "immédiatement",
    ],
    "contains a link": ["http://", "https://", "www."],
    "unsolicited payment/refund": [
        "refund", "you are eligible", "you qualify", "claim now", "free money",
        "remboursement", "استرداد",
    ],
}


def _hits(text: str, groups: dict) -> List[str]:
    found = []
    for reason, terms in groups.items():
        if any(t in text for t in terms):
            found.append(reason)
    return found


def detect_scam(text: str) -> Tuple[bool, int, List[str]]:
    """Return (is_scam, risk_score 0-100, reasons)."""
    t = re.sub(r"\s+", " ", (text or "").lower())
    strong = _hits(t, _STRONG)
    weak = _hits(t, _WEAK)

    reasons = list(strong)
    # Two weak signals together (e.g. a link + urgency) also count.
    if len(weak) >= 2:
        reasons += weak

    is_scam = bool(strong) or len(weak) >= 2
    # Score: strong signals weigh heavily, weak ones a little.
    score = min(100, len(strong) * 45 + len(weak) * 15)
    if is_scam:
        score = max(score, 60)
    return (is_scam, score, reasons)
