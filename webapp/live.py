"""Live updates over WebSocket.

NoorDesk's dashboard originally polled `/api/messages` and `/api/stats` every
five seconds. That works, and it is genuinely the right default for a tool that
might be running over a flaky hotel wifi — a dropped poll costs you five seconds
and nothing else. But it means the browser asks "anything new?" seventeen
thousand times a day, and almost every answer is "no".

This module replaces that with a push. The trade-offs are set out in the README;
what follows are the decisions that shaped the code.

**The socket carries hints, not data.** A broadcast says only "messages
changed". The client then re-fetches through the existing REST endpoints, which
already have authentication, rate limiting and validation on them. Pushing full
message payloads down the socket would mean duplicating all of that on a second
path, and customer messages are exactly the data NoorDesk exists to keep on the
operator's own machine. One authenticated read path is easier to secure than two.

**Publishing is safe from synchronous code.** Every endpoint in main.py is a
plain `def`, so FastAPI runs it in a worker thread. Touching an asyncio object
from there is a data race. `publish()` therefore hands the work to the event
loop with `run_coroutine_threadsafe`, and does nothing at all if no loop has
been registered yet — a broadcast is a nicety, never a reason for a request to
fail.

**Slow clients get dropped, not queued.** Each connection has a bounded queue.
A laptop that went to sleep mid-session must not be able to grow the server's
memory. When its queue fills we discard the oldest hint, because hints are
idempotent: "something changed" twice is the same instruction as once.

**Authentication happens in the first message, not the URL.** Putting a token in
a query string writes it into every access log and proxy trace along the way.
The client sends it as the first frame instead, and a connection that fails to
authenticate inside a few seconds is closed.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any

log = logging.getLogger("noordesk.live")

# How long a new connection has to send its auth frame before we hang up.
AUTH_TIMEOUT = 5.0

# Server->client keepalive. Proxies and phone radios drop idle sockets; a
# periodic ping keeps them open and lets us notice a peer that has gone away.
PING_INTERVAL = 25.0

# Per-connection backlog. Small on purpose: these are hints, and a client that
# is this far behind will get the current state from its next fetch anyway.
QUEUE_LIMIT = 8


class Hub:
    """Registry of connected dashboards, and a way to nudge all of them."""

    def __init__(self) -> None:
        self._queues: set[asyncio.Queue] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._published = 0
        self._dropped = 0

    # -- lifecycle ---------------------------------------------------------

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Remember the loop so synchronous endpoints can publish into it."""
        self._loop = loop

    def register(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=QUEUE_LIMIT)
        self._queues.add(q)
        return q

    def unregister(self, q: asyncio.Queue) -> None:
        self._queues.discard(q)

    # -- publishing --------------------------------------------------------

    @property
    def clients(self) -> int:
        return len(self._queues)

    @property
    def stats(self) -> dict[str, int]:
        return {"clients": self.clients, "published": self._published, "dropped": self._dropped}

    def _emit(self, event: dict[str, Any]) -> None:
        """Runs on the event loop. Never blocks on a slow consumer."""
        for q in list(self._queues):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # Discard this client's oldest hint and try once more. Hints are
                # idempotent, so losing one costs nothing.
                try:
                    q.get_nowait()
                    q.put_nowait(event)
                except Exception:
                    self._dropped += 1

    def publish(self, kind: str, **fields: Any) -> None:
        """Broadcast a change hint. Safe to call from any thread.

        Deliberately swallows every error: a dashboard that misses a nudge
        refreshes a few seconds later anyway, and no API call should ever fail
        because a browser tab went away.
        """
        event = {"type": kind, "at": time.time(), **fields}
        self._published += 1

        loop = self._loop
        if loop is None or loop.is_closed():
            return
        try:
            if loop is _running_loop():
                self._emit(event)
            else:
                loop.call_soon_threadsafe(self._emit, event)
        except RuntimeError:
            # Loop shutting down mid-request. Nothing to do and nothing to say.
            pass


def _running_loop() -> asyncio.AbstractEventLoop | None:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return None


# One hub per process. NoorDesk is single-operator and single-process by design;
# a multi-worker deployment would need Redis pub/sub here instead, which is
# noted in the README rather than pretended away.
hub = Hub()


# ---------------------------------------------------------------------------
# Handshake
# ---------------------------------------------------------------------------

def check_auth(frame: str | None) -> bool:
    """Validate the client's opening frame against NOORDESK_TOKEN.

    Mirrors `security.require_token`: when no token is configured we are in
    trusted local mode and accept the connection. Comparison is constant-time so
    the socket can't be used as an oracle to guess the token a byte at a time.
    """
    expected = os.environ.get("NOORDESK_TOKEN")
    if not expected:
        return True
    if not frame:
        return False
    try:
        payload = json.loads(frame)
    except (ValueError, TypeError):
        return False
    supplied = payload.get("token")
    if not isinstance(supplied, str):
        return False
    import hmac
    return hmac.compare_digest(supplied, expected)
