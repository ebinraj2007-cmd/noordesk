"""Dashboard API tests via FastAPI TestClient."""
from fastapi.testclient import TestClient
from webapp.main import app

client = TestClient(app)


def test_run_and_messages_flow():
    assert client.post("/api/run", json={}).json()["processed"] == 15
    msgs = client.get("/api/messages").json()
    assert len(msgs) == 15
    # sorted so needs_review floats to the top
    assert msgs[0]["needs_review"] >= msgs[-1]["needs_review"]


def test_stats_shape():
    client.post("/api/run", json={})
    stats = client.get("/api/stats").json()
    assert stats["total"] == 15
    assert set(stats["by_language"]).issubset({"English", "Arabic", "Malayalam", "Tamil", "French", "Other"})


def test_send_and_clear():
    client.post("/api/run", json={})
    mid = client.get("/api/messages").json()[0]["id"]
    assert client.post("/api/send", json={"id": mid}).json()["ok"] is True
    assert client.post("/api/clear").json()["ok"] is True
    assert client.get("/api/messages").json() == []
