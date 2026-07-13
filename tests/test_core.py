"""Core engine tests — all run offline with no API key."""
from noordesk.detect import detect_language
from noordesk.classifier import classify, detect_sentiment
from noordesk.responder import draft_reply
from noordesk.escalation import needs_review
from noordesk.pipeline import process_message
from noordesk import storage


# ---------- language detection (all 5 languages) ----------
def test_detect_english():
    assert detect_language("Hello, I would like to book an appointment.")[0] == "en"

def test_detect_french():
    assert detect_language("Bonjour, je voudrais réserver une table ce soir.")[0] == "fr"

def test_detect_arabic():
    assert detect_language("مرحبا، أريد حجز موعد.")[0] == "ar"

def test_detect_malayalam():
    assert detect_language("എനിക്ക് ഒരു അപ്പോയിന്റ്മെന്റ് വേണം.")[0] == "ml"

def test_detect_tamil():
    assert detect_language("எனக்கு உதவி தேவை.")[0] == "ta"

def test_english_vs_french_not_confused():
    # the historically fragile case
    assert detect_language("Combien coûte une consultation ?")[0] == "fr"


# ---------- intent + negation ----------
def test_booking_intent():
    intent, priority, conf, _ = classify("I want to book an appointment")
    assert intent == "booking"

def test_negation_english_not_urgent():
    # "not an emergency" must NOT bump priority to urgent
    _, p_neg, _, _ = classify("This is not an emergency, just a question.")
    _, p_urgent, _, _ = classify("This is an emergency, help now!")
    assert p_urgent > p_neg

def test_negation_french_not_urgent():
    _, p_neg, _, _ = classify("Ce n'est pas urgent, le lien ne marche pas.")
    assert p_neg <= 4  # support base, not urgency-bumped

def test_spam_detected():
    intent, _, _, _ = classify("CONGRATULATIONS YOU WON a free prize click here lottery bitcoin")
    assert intent == "spam"


# ---------- sentiment ----------
def test_angry_sentiment_and_priority():
    intent, priority, _, sentiment = classify("This is the worst, unacceptable service, I am furious")
    assert sentiment == "angry"
    assert priority == 5


# ---------- reply language guarantee ----------
def test_reply_language_matches_detected():
    for text in [
        "I want to book an appointment",
        "Bonjour, je voudrais réserver",
        "أريد حجز موعد",
        "எனக்கு உதவி தேவை",
        "എനിക്ക് അപ്പോയിന്റ്മെന്റ് വേണം",
    ]:
        lang, _ = detect_language(text)
        intent, _, _, _ = classify(text)
        reply = draft_reply(intent, lang)
        # reply is drawn from that language's template table
        from noordesk.responder import TEMPLATES
        assert reply == "" or reply.startswith(TEMPLATES[lang][intent].split("{")[0][:10])


# ---------- escalation ----------
def test_low_confidence_escalates():
    assert needs_review(0.4, 0.9, "neutral") is True
    assert needs_review(0.9, 0.4, "neutral") is True
    assert needs_review(0.9, 0.9, "neutral") is False

def test_angry_always_escalates():
    assert needs_review(0.99, 0.99, "angry") is True


# ---------- storage: utf-8 round trip + idempotency ----------
def test_utf8_roundtrip():
    rec = process_message({"id": "x1", "sender": "a", "raw_text": "أريد حجز موعد اليوم"})
    storage.save_messages([rec])
    got = storage.get_all()[0]
    assert got["raw_text"] == "أريد حجز موعد اليوم"

def test_tamil_roundtrip():
    rec = process_message({"id": "x2", "sender": "a", "raw_text": "எனக்கு உதவி தேவை"})
    storage.save_messages([rec])
    stored = {r["id"]: r for r in storage.get_all()}
    assert stored["x2"]["raw_text"] == "எனக்கு உதவி தேவை"

def test_idempotent_rerun():
    rec = process_message({"id": "dup", "sender": "a", "raw_text": "hello"})
    storage.save_messages([rec])
    storage.save_messages([rec])  # same id again
    ids = [r["id"] for r in storage.get_all()]
    assert ids.count("dup") == 1
