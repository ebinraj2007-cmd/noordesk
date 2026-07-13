"""Conversational small-talk: greet back, thank, sign off — in the right language."""
from noordesk.responder import draft_reply


def test_greeting_replies_conversationally():
    for msg in ["hello", "hii", "hey", "wassup", "good morning"]:
        r = draft_reply("general", "en", {"mode": "personal"}, msg)
        assert "👋" in r and "get back to you" not in r


def test_thanks_and_bye():
    assert "welcome" in draft_reply("general", "en", {"mode": "personal"}, "thanks a lot").lower()
    assert draft_reply("general", "en", {"mode": "personal"}, "bye") != ""


def test_greeting_language_from_word_not_detector():
    # short English greeting must reply in English even if detector is unsure
    assert "Hey!" in draft_reply("general", "fr", {"mode": "personal"}, "hii")
    # Arabic greeting replies in Arabic
    assert "مرحب" in draft_reply("general", "ar", {"mode": "personal"}, "مرحبا")


def test_real_question_not_treated_as_greeting():
    r = draft_reply("general", "en", {"mode": "personal"}, "hi, do you deliver to Dubai today?")
    assert "👋" not in r     # long message → not small-talk
