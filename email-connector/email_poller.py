#!/usr/bin/env python3
"""NoorDesk email connector (local, IMAP + SMTP, standard library only).

Works with Gmail, Outlook/Office365, Zoho, iCloud, etc. — just point it at the
right servers. Inbound: watches your inbox and triages new mail on the NoorDesk
dashboard. Outbound: emails your APPROVED replies back to the sender.

Environment (credentials are read from env, never written to disk):
  EMAIL_ADDRESS        your full email address
  EMAIL_APP_PASSWORD   an app password for the mailbox
  IMAP_HOST            default imap.gmail.com
  SMTP_HOST            default smtp.gmail.com
  SMTP_PORT            default 465 (SSL). Use 587 for STARTTLS (Outlook).
  PROVIDER             label shown in the console (e.g. Gmail / Outlook)
  NOORDESK_CORE        default http://127.0.0.1:8000
  EMAIL_POLL_SECONDS   default 20
"""
import email
import imaplib
import json
import os
import smtplib
import time
import urllib.request
from email.header import decode_header
from email.mime.text import MIMEText
from email.utils import parseaddr

CORE = os.environ.get("NOORDESK_CORE", "http://127.0.0.1:8000").rstrip("/")
ADDR = (os.environ.get("EMAIL_ADDRESS") or os.environ.get("GMAIL_ADDRESS", "")).strip()
PW = (os.environ.get("EMAIL_APP_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD", "")).replace(" ", "")
IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
PROVIDER = os.environ.get("PROVIDER", "email")
POLL = int(os.environ.get("EMAIL_POLL_SECONDS", "20"))

seen_ids = set()
pending = {}
delivered = set()


def _decode(value):
    if not value:
        return ""
    out = ""
    for text, enc in decode_header(value):
        out += text.decode(enc or "utf-8", errors="replace") if isinstance(text, bytes) else text
    return out


def _body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                try:
                    return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")
                except Exception:
                    continue
        return ""
    try:
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")
    except Exception:
        return msg.get_payload() or ""


def _post(path, data):
    req = urllib.request.Request(CORE + path, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(path):
    with urllib.request.urlopen(CORE + path, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_new():
    M = imaplib.IMAP4_SSL(IMAP_HOST)
    M.login(ADDR, PW)
    M.select("INBOX")
    _typ, data = M.search(None, "UNSEEN")
    for num in data[0].split()[-20:]:
        _typ, md = M.fetch(num, "(BODY.PEEK[])")   # PEEK keeps the email unread
        raw = email.message_from_bytes(md[0][1])
        mid = raw.get("Message-ID") or ("em-" + num.decode())
        if mid in seen_ids:
            continue
        seen_ids.add(mid)
        frm = parseaddr(raw.get("From", ""))[1]
        subject = _decode(raw.get("Subject", ""))
        body = _body(raw).strip()
        text = ((subject + "\n" + body).strip()) if subject else body
        if not frm or not text:
            continue
        pending[mid] = {"to": frm, "subject": subject}
        try:
            _post("/api/ingest", {"id": mid, "sender": frm, "channel": "email", "raw_text": text})
            print("→ new email triaged from", frm)
        except Exception as e:
            print("  (core not reachable — is NoorDesk running?)", e)
    M.logout()


def _smtp():
    if SMTP_PORT == 465:
        return smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
    s = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    s.ehlo()
    s.starttls()
    s.ehlo()
    return s


def send_replies():
    rows = _get("/api/messages")
    todo = [r for r in rows if r.get("channel") == "email" and r.get("status") == "sent"
            and r.get("suggested_reply") and r["id"] not in delivered]
    if not todo:
        return
    s = _smtp()
    s.login(ADDR, PW)
    for r in todo:
        meta = pending.get(r["id"], {})
        to = meta.get("to") or r.get("sender")
        if not to or "@" not in to:
            delivered.add(r["id"])
            continue
        subject = meta.get("subject") or "your message"
        if not subject.lower().startswith("re:"):
            subject = "Re: " + subject
        msg = MIMEText(r["suggested_reply"], "plain", "utf-8")
        msg["From"] = ADDR
        msg["To"] = to
        msg["Subject"] = subject
        s.sendmail(ADDR, [to], msg.as_string())
        delivered.add(r["id"])
        print("← approved reply emailed to", to)
    s.quit()


def main():
    if not ADDR or not PW:
        print("Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD, then run again.")
        return
    print(PROVIDER + " connector running for " + ADDR + " — checking every " + str(POLL) + "s.")
    print("Leave this window open. New emails appear on your NoorDesk dashboard.")
    while True:
        try:
            fetch_new()
        except Exception as e:
            print("IMAP error:", e)
        try:
            send_replies()
        except Exception as e:
            print("SMTP error:", e)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
