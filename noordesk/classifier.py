"""Intent classification, priority scoring, and sentiment/tone detection.

Deterministic rule engine. Multilingual keyword sets. Negation handling for
English and French so "not urgent" / "pas urgent" is not treated as urgent.
"""
from __future__ import annotations

import re
from typing import Tuple

INTENTS = ["booking", "complaint", "price_enquiry", "support", "spam", "general"]

BASE_PRIORITY = {
    "complaint": 5,
    "support": 4,
    "booking": 3,
    "price_enquiry": 2,
    "general": 2,
    "spam": 1,
}

# Multilingual keyword hints per intent (lowercased match on normalised text).
KEYWORDS = {
    "booking": [
        "book", "booking", "appointment", "reserve", "reservation", "schedule", "slot",
        "rendez-vous", "réserver", "reservation",           # fr
        "موعد", "حجز", "احجز",                                # ar
        "ബുക്ക്", "അപ്പോയിന്റ്മെന്റ്",                          # ml
        "பதிவு", "முன்பதிவு", "அப்பாய்ண்ட்மென்ட்",              # ta
    ],
    "complaint": [
        "complaint", "complain", "refund", "terrible", "worst", "angry", "unacceptable",
        "disappointed", "broken", "wrong", "late",
        "plainte", "remboursement", "inacceptable", "déçu",  # fr
        "شكوى", "استرجاع", "سيء", "غاضب", "خطأ",              # ar
        "പരാതി", "മോശം", "മോശമായ", "ദേഷ്യ",                    # ml
        "புகார்", "மோசம", "மோசமான", "தவறு", "கோப",              # ta
    ],
    "price_enquiry": [
        "price", "cost", "how much", "quote", "rate", "fees", "charge",
        "prix", "coût", "combien", "tarif",                  # fr
        "سعر", "كم", "تكلفة", "الأسعار",                       # ar
        "വില", "എത്ര",                                        # ml
        "விலை", "எவ்வளவு",                                     # ta
    ],
    "support": [
        "help", "support", "issue", "problem", "not working", "error", "stuck", "fix",
        "aide", "problème", "ne marche pas", "erreur",       # fr
        "مساعدة", "مشكلة", "لا يعمل", "خطأ",                   # ar
        "സഹായം", "പ്രശ്നം",                                   # ml
        "உதவி", "பிரச்சனை",                                    # ta
    ],
    "spam": [
        "congratulations you won", "click here", "free prize", "lottery", "bitcoin",
        "investment opportunity", "act now", "limited offer", "earn money fast",
        "gagné", "cliquez ici", "loterie",                   # fr
        "مبروك لقد ربحت", "اضغط هنا", "جائزة مجانية",          # ar
    ],
}

URGENCY_TERMS = [
    "urgent", "emergency", "asap", "immediately", "right now", "critical",
    "urgent", "urgence", "immédiatement",                    # fr
    "عاجل", "طارئ", "حالا",                                   # ar
    "അടിയന്തരം",                                              # ml
    "அவசரம்",                                                 # ta
]

NEGATIONS = ["not", "no", "never", "isn't", "wasn't", "don't",
             "pas", "non", "ne", "aucun"]  # en + fr

ANGER_TERMS = [
    "angry", "furious", "terrible", "worst", "unacceptable", "disgusting",
    "ridiculous", "never again", "scam", "cheated",
    "furieux", "inacceptable", "arnaque",                    # fr
    "غاضب", "سيء جدا", "احتيال",                              # ar
    "മോശം", "ദേഷ്യ",                                          # ml
    "மோசமான", "கோப",                                          # ta
]


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _has_unnegated_urgency(text: str) -> bool:
    """True if an urgency term appears without a nearby negation before it."""
    words = text.split()
    for i, w in enumerate(words):
        if any(term in w for term in URGENCY_TERMS):
            window = words[max(0, i - 3):i]
            if not any(neg == token for token in window for neg in NEGATIONS):
                return True
    return False


def detect_sentiment(text: str) -> str:
    """Return 'angry', 'neutral'."""
    t = _normalise(text)
    if any(term in t for term in ANGER_TERMS):
        return "angry"
    return "neutral"


def classify(text: str) -> Tuple[str, int, float, str]:
    """Return (intent, priority, confidence 0..1, sentiment)."""
    t = _normalise(text)
    sentiment = detect_sentiment(text)

    # Score each intent by keyword hits.
    scores = {intent: 0 for intent in INTENTS if intent != "general"}
    for intent, words in KEYWORDS.items():
        for kw in words:
            if kw in t:
                scores[intent] += 1

    best_intent = "general"
    best_score = 0
    for intent, score in scores.items():
        if score > best_score:
            best_intent = intent
            best_score = score

    priority = BASE_PRIORITY[best_intent]

    # Urgency (with negation handling) bumps priority.
    if _has_unnegated_urgency(t):
        priority = min(5, priority + 2)

    # Angry customers are always high priority.
    if sentiment == "angry":
        priority = max(priority, 5)
        if best_intent == "general":
            best_intent = "complaint"

    # Confidence: based on how decisively keywords matched.
    if best_intent == "general" and sentiment == "neutral":
        confidence = 0.45  # nothing matched -> uncertain, likely needs review
    elif best_score >= 2:
        confidence = 0.9
    elif best_score == 1:
        confidence = 0.75
    else:
        confidence = 0.6

    return (best_intent, priority, confidence, sentiment)
