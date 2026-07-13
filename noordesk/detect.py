"""Language detection.

Arabic, Malayalam, and Tamil are detected instantly and reliably by their
distinct Unicode scripts. The only genuinely ambiguous case is English vs
French (both Latin script), which the `lingua` library resolves accurately.
Returns a (language_code, confidence) tuple.
"""
from __future__ import annotations

from typing import Optional, Tuple

try:
    from lingua import Language, LanguageDetectorBuilder
    # lingua handles the Latin-script pair only; scripts below cover ar/ml/ta.
    _LINGUA_MAP = {
        Language.ENGLISH: "en",
        Language.FRENCH: "fr",
    }
    _DETECTOR = (
        LanguageDetectorBuilder.from_languages(*_LINGUA_MAP.keys())
        .with_preloaded_language_models()
        .build()
    )
except Exception:  # pragma: no cover - lingua should be installed
    Language = None
    _LINGUA_MAP = {}
    _DETECTOR = None


def _script_hint(text: str) -> Optional[str]:
    """Fast, reliable detection for distinct-script languages."""
    for ch in text:
        code = ord(ch)
        if 0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F:
            return "ar"
        if 0x0D00 <= code <= 0x0D7F:
            return "ml"
        if 0x0B80 <= code <= 0x0BFF:
            return "ta"
    return None


def detect_language(text: str) -> Tuple[str, float]:
    """Return (language_code, confidence 0..1)."""
    text = (text or "").strip()
    if not text:
        return ("en", 0.0)

    # Distinct scripts are unambiguous - trust them with high confidence.
    hint = _script_hint(text)
    if hint is not None:
        return (hint, 0.99)

    if _DETECTOR is None:
        # Minimal fallback if lingua is unavailable.
        return ("en", 0.5)

    values = _DETECTOR.compute_language_confidence_values(text)
    if not values:
        return ("en", 0.3)
    top = values[0]
    code = _LINGUA_MAP.get(top.language, "en")
    return (code, float(top.value))
