"""Tests for the pre-deployment hardening: auth, path traversal, validation."""
import importlib
import os
import pytest
from fastapi.testclient import TestClient


def _client():
    import webapp.main as m
    importlib.reload(m)
    return TestClient(m.app)


def test_run_rejects_path_traversal():
    client = _client()
    r = client.post("/api/run", json={"inbox": "../../../../etc"})
    assert r.status_code == 400
    assert "error" in r.json()


def test_token_required_when_configured(monkeypatch):
    monkeypatch.setenv("NOORDESK_TOKEN", "s3cret")
    client = _client()
    # no header -> 401
    assert client.post("/api/clear").status_code == 401
    # wrong token -> 403
    assert client.post("/api/clear", headers={"Authorization": "Bearer nope"}).status_code == 403
    # right token -> 200
    assert client.post("/api/clear", headers={"Authorization": "Bearer s3cret"}).status_code == 200


def test_reads_allowed_without_token(monkeypatch):
    monkeypatch.setenv("NOORDESK_TOKEN", "s3cret")
    client = _client()
    assert client.get("/api/messages").status_code == 200


def test_healthz_ok():
    client = _client()
    body = client.get("/healthz").json()
    assert body["status"] == "ok"


def test_oversized_input_rejected():
    client = _client()
    r = client.post("/api/ingest", json={"id": "x", "sender": "y", "raw_text": "A" * 9000})
    assert r.status_code == 422  # pydantic length cap


def test_rate_limit_kicks_in(monkeypatch):
    monkeypatch.setenv("NOORDESK_RATE_STRICT", "3")
    from webapp import security
    security.reset_rate_limits()
    client = _client()
    codes = [client.post("/api/clear").status_code for _ in range(6)]
    assert 429 in codes  # blocked once the strict cap is passed
