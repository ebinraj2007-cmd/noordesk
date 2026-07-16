import os
import tempfile
import pytest


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Isolate every test's database in a temp file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("NOORDESK_DB", path)
    pf = path + ".profile.json"
    monkeypatch.setenv("NOORDESK_PROFILE", pf)
    # Keep rate limits out of the way of functional tests, and start each test
    # with fresh counters. The rate limiter has its own dedicated test.
    monkeypatch.setenv("NOORDESK_RATE", "100000")
    monkeypatch.setenv("NOORDESK_RATE_STRICT", "100000")
    from webapp import security
    security.reset_rate_limits()
    yield path
    for p in (path, path + "-wal", path + "-shm", pf):
        if os.path.exists(p):
            os.remove(p)
