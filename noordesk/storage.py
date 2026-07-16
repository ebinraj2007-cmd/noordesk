"""SQLite persistence. Idempotent by message id (no duplicate rows).

Stores full Unicode text. Uses parameterised queries only (no SQL injection).
"""
from __future__ import annotations

import os
import sqlite3
from typing import List, Dict, Optional

DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".noordesk", "noordesk.db")


def current_db() -> str:
    """Resolve the DB path at call time (NOORDESK_DB env var overrides default)."""
    return os.environ.get("NOORDESK_DB", DEFAULT_DB)

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    sender TEXT,
    channel TEXT,
    raw_text TEXT,
    detected_language TEXT,
    language_confidence REAL,
    intent TEXT,
    priority INTEGER,
    sentiment TEXT,
    suggested_reply TEXT,
    translation TEXT,
    engine_used TEXT,
    needs_review INTEGER,
    scam INTEGER,
    scam_score INTEGER,
    scam_reasons TEXT,
    vip INTEGER,
    repeat INTEGER,
    after_hours INTEGER,
    status TEXT,
    created_at TEXT
);
"""

# Indexes on the columns the dashboard actually filters/sorts by (checklist #7).
# get_all() orders by (needs_review, priority, created_at); set_status filters by
# id (already the PRIMARY KEY). status is filtered in the UI. Targeted only -
# over-indexing would slow every insert for no read benefit.
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_messages_sort ON messages(needs_review DESC, priority DESC, created_at DESC);",
    "CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);",
    "CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender);",
]

COLUMNS = [
    "id", "sender", "channel", "raw_text", "detected_language", "language_confidence",
    "intent", "priority", "sentiment", "suggested_reply", "translation",
    "engine_used", "needs_review", "scam", "scam_score", "scam_reasons",
    "vip", "repeat", "after_hours", "status", "created_at",
]

# column -> SQL type, used to auto-add any missing columns on existing DBs.
_COL_TYPES = {
    "scam": "INTEGER", "scam_score": "INTEGER", "scam_reasons": "TEXT",
    "vip": "INTEGER", "repeat": "INTEGER", "after_hours": "INTEGER",
}


def _connect(db_path: str) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    db_path = db_path or current_db()
    with _connect(db_path) as conn:
        conn.executescript(SCHEMA)
        # Migrate older databases: add any columns they're missing.
        existing = {row[1] for row in conn.execute("PRAGMA table_info(messages)")}
        for col, coltype in _COL_TYPES.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE messages ADD COLUMN {col} {coltype}")
        for ddl in INDEXES:
            conn.execute(ddl)


def save_messages(records: List[Dict], db_path: Optional[str] = None) -> int:
    db_path = db_path or current_db()
    init_db(db_path)
    placeholders = ", ".join(["?"] * len(COLUMNS))
    sql = f"INSERT OR REPLACE INTO messages ({', '.join(COLUMNS)}) VALUES ({placeholders})"
    rows = [[r.get(c) for c in COLUMNS] for r in records]
    with _connect(db_path) as conn:
        conn.executemany(sql, rows)
    return len(rows)


def get_all(db_path: Optional[str] = None) -> List[Dict]:
    db_path = db_path or current_db()
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            "SELECT * FROM messages ORDER BY needs_review DESC, priority DESC, created_at DESC"
        )
        return [dict(row) for row in cur.fetchall()]


def set_status(msg_id: str, status: str, db_path: Optional[str] = None) -> None:
    db_path = db_path or current_db()
    with _connect(db_path) as conn:
        conn.execute("UPDATE messages SET status = ? WHERE id = ?", (status, msg_id))


def clear(db_path: Optional[str] = None) -> None:
    db_path = db_path or current_db()
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM messages")
