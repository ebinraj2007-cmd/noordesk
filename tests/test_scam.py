"""Scam shield: detection + reply suppression."""
from noordesk.scam import detect_scam
from noordesk.pipeline import process_message


def test_flags_phishing_link():
    s, score, reasons = detect_scam("Your account is suspended, verify at bit.ly/x now urgently")
    assert s is True and score >= 60 and reasons


def test_flags_otp_request():
    s, _, _ = detect_scam("Please send me the OTP you just received")
    assert s is True


def test_flags_lottery():
    s, _, _ = detect_scam("Congratulations, you won a prize! Claim your lottery bitcoin")
    assert s is True


def test_legit_message_not_flagged():
    for good in ["Hi, can I book a table for 8pm?", "How much is the power bank?",
                 "أريد حجز موعد غدا"]:
        s, _, _ = detect_scam(good)
        assert s is False


def test_pipeline_suppresses_reply_for_scam():
    rec = process_message({"id": "z", "sender": "x@evil.co",
                           "raw_text": "verify your account at bit.ly/x and send your OTP"})
    assert rec["scam"] == 1
    assert rec["suggested_reply"] == ""     # never auto-reply to a scam
    assert rec["needs_review"] == 1
    assert rec["scam_reasons"]
