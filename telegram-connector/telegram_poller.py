#!/usr/bin/env python3
"""NoorDesk Telegram connector (official Bot API, standard library only).

Reliable and ToS-compliant — no ban risk. Long-polls getUpdates for new
messages, triages them on the NoorDesk dashboard, and sends approved replies
back with sendMessage.

Env: TELEGRAM_BOT_TOKEN (from @BotFather), NOORDESK_CORE (default 127.0.0.1:8000)
"""
import json
import os
import time
import urllib.parse
import urllib.request

CORE = os.environ.get("NOORDESK_CORE", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
API = "https://api.telegram.org/bot" + TOKEN
POLL_TIMEOUT = 25

pending = {}
delivered = set()
offset = None


def tg(method, params=None):
    data = urllib.parse.urlencode(params or {}).encode("utf-8")
    req = urllib.request.Request(API + "/" + method, data=data)
    with urllib.request.urlopen(req, timeout=POLL_TIMEOUT + 10) as r:
        return json.loads(r.read().decode("utf-8"))


def _post(path, data):
    req = urllib.request.Request(CORE + path, data=json.dumps(data).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(path):
    with urllib.request.urlopen(CORE + path, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def loop():
    global offset
    me = tg("getMe").get("result", {})
    print("Telegram connector running as @" + str(me.get("username", "?")) +
          " — message your bot to test.")
    while True:
        try:
            params = {"timeout": POLL_TIMEOUT}
            if offset:
                params["offset"] = offset
            for u in tg("getUpdates", params).get("result", []):
                offset = u["update_id"] + 1
                m = u.get("message") or u.get("edited_message")
                text = (m or {}).get("text")
                if not m or not text:
                    continue
                chat_id = m["chat"]["id"]
                frm = m.get("from", {})
                sender = ("@" + frm["username"]) if frm.get("username") else (frm.get("first_name") or str(chat_id))
                mid = "tg-" + str(m["message_id"]) + "-" + str(chat_id)
                pending[mid] = {"chat": chat_id}
                _post("/api/ingest", {"id": mid, "sender": sender, "channel": "telegram", "raw_text": text})
                print("→ Telegram message from", sender)

            for r in _get("/api/messages"):
                if (r.get("channel") == "telegram" and r.get("status") == "sent"
                        and r.get("suggested_reply") and r["id"] not in delivered):
                    meta = pending.get(r["id"])
                    if meta:
                        tg("sendMessage", {"chat_id": meta["chat"], "text": r["suggested_reply"]})
                        delivered.add(r["id"])
                        print("← approved reply sent on Telegram")
        except Exception as e:
            print("Telegram error:", e)
            time.sleep(3)


def main():
    if not TOKEN:
        print("Set TELEGRAM_BOT_TOKEN (get one from @BotFather), then run again.")
        return
    loop()


if __name__ == "__main__":
    main()
