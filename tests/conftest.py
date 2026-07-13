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
    yield path
    for p in (path, path + "-wal", path + "-shm", pf):
        if os.path.exists(p):
            os.remove(p)
