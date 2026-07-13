"""Load incoming messages.

Local-friendly by design: reads JSON files from a folder. Each .json file may be
a single message object or a list of message objects.

A documented IMAP hook is included for connecting a real mailbox (email is
naturally local: the app polls the user's own inbox from their machine).
"""
from __future__ import annotations

import glob
import json
import os
from typing import List, Dict


def load_from_folder(folder: str) -> List[Dict]:
    messages: List[Dict] = []
    for path in sorted(glob.glob(os.path.join(folder, "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            messages.extend(data)
        elif isinstance(data, dict):
            messages.append(data)
    return messages


def fetch_from_imap(host: str, username: str, password: str,
                    folder: str = "INBOX", limit: int = 50) -> List[Dict]:  # pragma: no cover
    """Example hook for a real mailbox. Runs entirely on the user's machine.

    Not exercised in tests (needs live credentials). Kept documented so the
    email channel plugs into the same pipeline as JSON/manual input.
    """
    import imaplib
    import email
    from email.header import decode_header

    out: List[Dict] = []
    conn = imaplib.IMAP4_SSL(host)
    conn.login(username, password)
    conn.select(folder)
    _typ, data = conn.search(None, "ALL")
    ids = data[0].split()[-limit:]
    for num in ids:
        _typ, msg_data = conn.fetch(num, "(RFC822)")
        raw = email.message_from_bytes(msg_data[0][1])
        subject, enc = decode_header(raw.get("Subject", ""))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(enc or "utf-8", errors="replace")
        body = ""
        if raw.is_multipart():
            for part in raw.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="replace")
                    break
        else:
            body = raw.get_payload(decode=True).decode(errors="replace")
        out.append({
            "id": f"email-{num.decode()}",
            "sender": raw.get("From", ""),
            "channel": "email",
            "raw_text": f"{subject}\n{body}".strip(),
        })
    conn.logout()
    return out
