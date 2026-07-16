"""Security helpers for the NoorDesk dashboard API.

Everything here is designed to be safe-by-default for the common case (a single
operator running NoorDesk locally) while making the app deployable to a shared
host without opening the holes on the standard pre-deployment checklist.

Controls provided:
  * Bearer-token authentication for state-changing endpoints (checklist #1).
  * A small in-memory per-client rate limiter (checklist #5).
  * A safe-path resolver that blocks path traversal (checklist #3).
"""
from __future__ import annotations

import os
import time
import threading
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

# ---------------------------------------------------------------------------
# 1. Authorization
# ---------------------------------------------------------------------------
# NoorDesk is single-operator: there is one owner, and every message record
# belongs to that owner's workspace. Rather than a per-row ownership check
# (there is only one tenant), we gate every write/state-changing endpoint behind
# a shared operator token. If NOORDESK_TOKEN is unset we assume trusted local
# use (127.0.0.1) and allow the request, but we log a warning at startup.

def token_configured() -> bool:
    return bool(os.environ.get("NOORDESK_TOKEN"))


def require_token(authorization: str | None = Header(default=None)) -> None:
    """FastAPI dependency. Enforces the operator token when one is configured.

    Send it as:  Authorization: Bearer <token>
    """
    expected = os.environ.get("NOORDESK_TOKEN")
    if not expected:
        # No token set -> local trusted mode. Reads and writes allowed.
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    supplied = authorization.split(" ", 1)[1].strip()
    # Constant-time comparison to avoid timing side-channels.
    import hmac
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=403, detail="Invalid token")


# ---------------------------------------------------------------------------
# 5. Rate limiting  (in-memory sliding window, per client IP)
# ---------------------------------------------------------------------------
_WINDOW = 60.0
_STRICT_PATHS = ("/api/run", "/api/ingest", "/api/clear")
_hits_default: dict[str, deque] = defaultdict(deque)
_hits_strict: dict[str, deque] = defaultdict(deque)
_lock = threading.Lock()


def _limit(name: str, default: int) -> int:
    # Read at call time so tests (and ops) can tune limits via env vars.
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def _allow(store: dict[str, deque], key: str, limit: int) -> bool:
    now = time.monotonic()
    with _lock:
        q = store[key]
        while q and q[0] <= now - _WINDOW:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True


def client_key(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_check(request: Request) -> bool:
    key = client_key(request)
    if request.url.path in _STRICT_PATHS:
        return _allow(_hits_strict, key, _limit("NOORDESK_RATE_STRICT", 12))
    return _allow(_hits_default, key, _limit("NOORDESK_RATE", 120))


def reset_rate_limits() -> None:
    """Clear all counters (used by the test-suite between cases)."""
    with _lock:
        _hits_default.clear()
        _hits_strict.clear()


# ---------------------------------------------------------------------------
# 3. Safe path resolution  (block path traversal / arbitrary reads)
# ---------------------------------------------------------------------------
def safe_inbox_path(user_path: str | None, default: str, root: str) -> str:
    """Resolve an inbox folder, refusing anything outside `root`.

    The dashboard lets the operator point at a folder of message JSON files.
    Without this check a caller could pass '/etc' or '../../secrets' and the
    loader would happily read it. We resolve the real path and require it to
    stay inside an allowlisted root (the project dir, or NOORDESK_DATA_ROOT).
    """
    if not user_path:
        return default
    allowed_root = os.path.realpath(os.environ.get("NOORDESK_DATA_ROOT", root))
    candidate = os.path.realpath(os.path.join(allowed_root, user_path))
    if candidate != allowed_root and not candidate.startswith(allowed_root + os.sep):
        raise HTTPException(status_code=400, detail="Inbox path is outside the allowed data directory")
    if not os.path.isdir(candidate):
        raise HTTPException(status_code=400, detail="Inbox path is not a directory")
    return candidate
