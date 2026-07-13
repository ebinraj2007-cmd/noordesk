#!/usr/bin/env python3
"""EXPERIMENTAL Instagram DM connector (UNOFFICIAL — high ban risk).

Uses instagrapi to read and reply to Instagram DMs locally. Instagram actively
detects automation and MAY LOCK OR BAN the account. Use a THROWAWAY / TEST
account only, and don't run it aggressively.

Requires: pip install instagrapi   (the launcher does this in a local venv)
Env: IG_USERNAME, IG_PASSWORD, NOORDESK_CORE (default http://127.0.0.1:8000)
"""
import json
import os
import time
import urllib.request

CORE = os.environ.get("NOORDESK_CORE", "http://127.0.0.1:8000").rstrip("/")
USER = os.environ.get("IG_USERNAME", "").strip()
PW = os.environ.get("IG_PASSWORD", "")
POLL = int(os.environ.get("IG_POLL_SECONDS", "30"))
SESSION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json")

seen = set()
pending = {}
delivered = set()


def _post(path, data):
    req = urllib.request.Request(CORE + path, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(path):
    with urllib.request.urlopen(CORE + path, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def get_client():
    from instagrapi import Client
    cl = Client()
    if os.path.exists(SESSION):
        try:
            cl.load_settings(SESSION)
        except Exception:
            pass
    cl.login(USER, PW)          # may raise a challenge on new devices
    try:
        cl.dump_settings(SESSION)
    except Exception:
        pass
    return cl


def run():
    cl = get_client()
    me = str(cl.user_id)
    uname = {}
    print("Connected. Watching Instagram DMs — leave this window open.")
    while True:
        try:
            for t in cl.direct_threads(amount=10):
                for m in cl.direct_messages(t.id, amount=5):
                    if str(m.user_id) == me:
                        continue
                    mid = str(m.id)
                    if mid in seen:
                        continue
                    seen.add(mid)
                    text = getattr(m, "text", None)
                    if not text:
                        continue
                    uid = str(m.user_id)
                    if uid not in uname:
                        try:
                            uname[uid] = "@" + cl.username_from_user_id(m.user_id)
                        except Exception:
                            uname[uid] = "ig:" + uid
                    pending[mid] = {"thread": t.id}
                    _post("/api/ingest", {"id": mid, "sender": uname[uid],
                                          "channel": "instagram", "raw_text": text})
                    print("→ new IG DM from", uname[uid])

            for r in _get("/api/messages"):
                if (r.get("channel") == "instagram" and r.get("status") == "sent"
                        and r.get("suggested_reply") and r["id"] not in delivered):
                    meta = pending.get(r["id"])
                    if meta:
                        cl.direct_send(r["suggested_reply"], thread_ids=[meta["thread"]])
                        delivered.add(r["id"])
                        print("← approved reply sent on Instagram")
        except Exception as e:
            print("Instagram error (login challenge or rate limit?):", e)
        time.sleep(POLL)


def main():
    if not USER or not PW:
        print("Set IG_USERNAME and IG_PASSWORD, then run again.")
        return
    print("EXPERIMENTAL Instagram connector for @" + USER)
    print("Unofficial automation — HIGH BAN RISK. Use a test account only.")
    run()


if __name__ == "__main__":
    main()
