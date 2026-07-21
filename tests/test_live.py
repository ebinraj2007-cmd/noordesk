"""Tests for the live-update layer.

Two things are being checked here, and they matter for different reasons.

The *hub* tests are about not hurting anything: a broadcast must never raise,
never block, and never grow memory without bound, because it runs inside request
handlers that have real work to do. A dashboard missing a nudge is a cosmetic
problem; an API call failing because a browser tab closed is a real one.

The *endpoint* tests are about the security boundary. The socket is a second
door into the application, and it needs the same lock as the front one.
"""
import asyncio
import json
import os

import pytest
from fastapi.testclient import TestClient

from webapp.live import Hub, check_auth, QUEUE_LIMIT
from webapp.main import app
from webapp.security import reset_rate_limits


@pytest.fixture(autouse=True)
def _clean():
    reset_rate_limits()
    yield
    os.environ.pop("NOORDESK_TOKEN", None)


# --------------------------------------------------------------- the hub ---

def test_publish_without_a_loop_is_silent():
    """Publishing before startup must not raise.

    A synchronous endpoint could run before (or after) the loop is bound. That
    is not a reason to fail somebody's API call.
    """
    hub = Hub()
    hub.publish("messages", reason="test")     # no loop bound
    assert hub.stats["published"] == 1


def test_publish_never_raises_on_a_closed_loop():
    hub = Hub()
    loop = asyncio.new_event_loop()
    hub.bind_loop(loop)
    loop.close()
    hub.publish("messages", reason="after-shutdown")   # must not raise


@pytest.mark.asyncio
async def test_registered_client_receives_the_event():
    hub = Hub()
    hub.bind_loop(asyncio.get_running_loop())
    q = hub.register()

    hub.publish("messages", reason="run", count=3)
    await asyncio.sleep(0)                     # let call_soon run

    event = q.get_nowait()
    assert event["type"] == "messages"
    assert event["reason"] == "run"
    assert event["count"] == 3
    assert "at" in event


@pytest.mark.asyncio
async def test_a_slow_client_cannot_grow_memory():
    """The whole point of a bounded queue.

    A laptop that slept mid-session must not be able to make the server hold an
    unbounded backlog on its behalf.
    """
    hub = Hub()
    hub.bind_loop(asyncio.get_running_loop())
    q = hub.register()

    for i in range(QUEUE_LIMIT * 5):
        hub.publish("messages", reason="flood", i=i)
        await asyncio.sleep(0)

    assert q.qsize() <= QUEUE_LIMIT

    # And what survives is recent, because we drop the oldest hint.
    newest = None
    while not q.empty():
        newest = q.get_nowait()
    assert newest["i"] >= QUEUE_LIMIT


@pytest.mark.asyncio
async def test_unregister_stops_delivery():
    hub = Hub()
    hub.bind_loop(asyncio.get_running_loop())
    q = hub.register()
    hub.unregister(q)

    hub.publish("messages", reason="gone")
    await asyncio.sleep(0)

    assert q.empty()
    assert hub.clients == 0


@pytest.mark.asyncio
async def test_every_client_gets_every_event():
    hub = Hub()
    hub.bind_loop(asyncio.get_running_loop())
    a, b, c = hub.register(), hub.register(), hub.register()

    hub.publish("messages", reason="broadcast")
    await asyncio.sleep(0)

    assert hub.clients == 3
    for q in (a, b, c):
        assert q.get_nowait()["reason"] == "broadcast"


# ------------------------------------------------------------- handshake ---

def test_local_mode_accepts_any_opening_frame():
    os.environ.pop("NOORDESK_TOKEN", None)
    assert check_auth('{"token": ""}') is True
    assert check_auth("") is True
    assert check_auth(None) is True


def test_a_configured_token_is_enforced():
    os.environ["NOORDESK_TOKEN"] = "s3cret"
    assert check_auth(json.dumps({"token": "s3cret"})) is True
    assert check_auth(json.dumps({"token": "wrong"})) is False
    assert check_auth(json.dumps({})) is False
    assert check_auth("not json") is False
    assert check_auth(None) is False


def test_a_non_string_token_is_refused():
    """Guards the constant-time compare, which raises on non-str input."""
    os.environ["NOORDESK_TOKEN"] = "s3cret"
    assert check_auth(json.dumps({"token": 12345})) is False
    assert check_auth(json.dumps({"token": None})) is False
    assert check_auth(json.dumps({"token": ["s3cret"]})) is False


# -------------------------------------------------------------- endpoint ---

def test_socket_opens_and_announces_itself():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"token": ""}))
            hello = ws.receive_json()
            assert hello["type"] == "ready"
            assert hello["clients"] >= 1


def test_a_mutation_pushes_a_hint_to_the_socket():
    """The end-to-end contract: change something, every dashboard hears about it."""
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"token": ""}))
            assert ws.receive_json()["type"] == "ready"

            client.post("/api/clear")

            event = ws.receive_json()
            assert event["type"] == "messages"
            assert event["reason"] == "clear"


def test_the_hint_carries_no_message_content():
    """The socket is a notification channel, not a data channel.

    Customer messages stay on the authenticated REST path. If this test starts
    failing, someone has begun pushing data down the socket and the security
    story needs revisiting.
    """
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"token": ""}))
            ws.receive_json()

            # Touch storage first so the schema exists, then drain that hint.
            client.post("/api/clear")
            ws.receive_json()

            client.post("/api/mark", json={"id": "abc", "status": "done"})
            event = ws.receive_json()

            assert set(event) <= {"type", "at", "reason", "id", "count"}
            assert "raw_text" not in event
            assert "reply" not in event


def test_a_bad_token_is_shown_the_door():
    os.environ["NOORDESK_TOKEN"] = "s3cret"
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect("/ws") as ws:
                ws.send_text(json.dumps({"token": "wrong"}))
                ws.receive_json()


def test_live_stats_endpoint_reports_the_hub():
    with TestClient(app) as client:
        body = client.get("/api/live/stats").json()
        assert set(body) == {"clients", "published", "dropped"}
        assert isinstance(body["clients"], int)
