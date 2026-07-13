"""FAQ answers, away-hours, VIP, repeat, and the done/snooze workflow."""
from noordesk.pipeline import process_message, _after_hours
from noordesk import storage
from webapp.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_faq_exact_answer_verbatim():
    prof = {"mode": "business", "role": "shop",
            "faqs": [{"q": "do you deliver", "a": "Yes, free over AED 100."}]}
    r = process_message({"id": "x", "sender": "a", "raw_text": "hi, do you deliver to Dubai?"}, profile=prof)
    assert r["suggested_reply"].startswith("Yes, free over AED 100.")
    assert r["engine_used"] == "faq"


def test_vip_flag():
    prof = {"mode": "business", "role": "shop", "vip": ["vip@x.com"]}
    assert process_message({"id": "a", "sender": "vip@x.com", "raw_text": "hi"}, profile=prof)["vip"] == 1
    assert process_message({"id": "b", "sender": "other@x.com", "raw_text": "hi"}, profile=prof)["vip"] == 0


def test_after_hours_logic():
    assert _after_hours({"away_enabled": False}) is False
    assert _after_hours({"away_enabled": True, "open_time": "00:00", "close_time": "23:59"}) is False


def test_repeat_customer_detected():
    client.post("/api/clear")
    client.post("/api/ingest", json={"id": "r1", "sender": "z@x.com", "channel": "email", "raw_text": "first"})
    client.post("/api/ingest", json={"id": "r2", "sender": "z@x.com", "channel": "email", "raw_text": "again"})
    rows = {r["id"]: r for r in client.get("/api/messages").json()}
    assert rows["r1"]["repeat"] == 0 and rows["r2"]["repeat"] == 1


def test_mark_done_and_reopen():
    client.post("/api/clear")
    client.post("/api/ingest", json={"id": "d1", "sender": "a@x.com", "channel": "email", "raw_text": "hello"})
    assert client.post("/api/mark", json={"id": "d1", "status": "done"}).json()["status"] == "done"
    assert {r["id"]: r["status"] for r in client.get("/api/messages").json()}["d1"] == "done"
    client.post("/api/mark", json={"id": "d1", "status": "new"})
    assert {r["id"]: r["status"] for r in client.get("/api/messages").json()}["d1"] == "new"
