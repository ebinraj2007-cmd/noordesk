<div align="center">

# ◈ NoorDesk

### Multilingual AI front desk — runs entirely on your own computer

Turn a messy multilingual inbox (WhatsApp · Gmail · Outlook · Telegram · Instagram · Web)
into one tidy, prioritized queue of ready-to-send replies — and let a one-language
owner serve customers in **five**.

**English · العربية · മലയാളം · தமிழ் · Français**

`local-first` · `offline AI (Ollama)` · `no cloud · no account · your data never leaves the machine`

</div>

---

## Why NoorDesk?

Small businesses get customer messages in many languages, across many apps, and
can't reply fast — or at all — in every one. Hiring multilingual staff is
expensive; machine-translating by hand is slow. NoorDesk does the first pass
automatically: it reads each message, works out the **language**, **tone** and
**priority**, drafts a reply **in the customer's own language**, and shows the
owner an English summary — so nothing sits untouched and no customer is lost to a
language barrier. Everything runs on your machine.

## Features

- **6 channels, one inbox** — WhatsApp, Gmail, Outlook (any IMAP), Telegram, Instagram, and an embeddable web chat widget, all feeding the same dashboard.
- **Understands language, tone & importance** — 5-language detection, angry-customer detection, priority scoring — all offline.
- **Three reply engines, graceful fallback** — a deterministic rule engine (always on), an **offline local AI** (Ollama, free), or cloud AI, in that order.
- **Real chatbot replies** — with the local AI on, it actually answers questions ("what's your name?", "what time is it?") in the customer's language.
- **Scam shield** — flags phishing/fraud (bad links, OTP/gift-card/crypto bait), blocks any auto-reply, and gathers them in a dedicated Scam page.
- **Roles & knowledge** — pick your role (shop, clinic, restaurant, freelancer, personal…), add **products + prices**, **FAQ answers**, opening hours, and VIP contacts — the AI uses them.
- **Portals** — a cross-channel **Priority** page for urgent messages, plus one page per platform.
- **Workflow** — approve-before-send, **Done / Snooze**, search, returning-customer detection, and an **analytics** tab.
- **Private by design** — runs on `127.0.0.1`; with the rule or local-AI engine, no message ever leaves your computer.

## Quick start (macOS)

> First time you open a `.command` file, macOS blocks it — **right-click → Open → Open**. After that, just double-click.

1. **Start the app** — double-click **`NoorDesk.command`**. It sets itself up and opens the dashboard at `http://127.0.0.1:8000`. A setup wizard appears on first launch.
2. **Turn on the smart AI (optional, offline & free)** — double-click **`Setup-Local-AI.command`**. It installs [Ollama](https://ollama.com) if needed and downloads a small model (`qwen2.5:3b`). Restart the app → the pill reads **"Local AI"**.
3. **Connect a channel** — double-click `Connect-WhatsApp.command` (scan the QR), `Connect-Gmail.command`, `Connect-Telegram.command`, etc.

See **[`START-HERE.md`](START-HERE.md)** for the complete guide.

## How it works

```
messages (WhatsApp / Gmail / Outlook / Telegram / Instagram / Web)
        │
        ▼
   detect language ─▶ classify intent + priority ─▶ tone ─▶ scam check
        │                                                      │
        ▼                                                      ▼
   draft reply (rules → local AI → cloud)  ──▶  needs-review? ──▶  dashboard
        │                                                      │
        └──────────── you approve ──▶ reply sent on the same channel
```

Language, tone, intent, priority and scam detection are **deterministic** and run
offline. The AI engine only words the reply — and if it's unavailable, the rule
engine covers it.

## AI engines

| Engine | Setup | Notes |
|---|---|---|
| **Rule engine** | none | Always on. Templates + greetings, fully offline. |
| **Local AI** | install Ollama, `ollama pull qwen2.5:3b` | **Recommended.** Real chatbot replies, offline & free. Auto-detected. |
| **Cloud AI** | set `ANTHROPIC_API_KEY` | Optional, sharpest wording. |

## Channels

| Channel | Connector | Needs |
|---|---|---|
| WhatsApp | `Connect-WhatsApp.command` | Scan QR (unofficial web — personal use) |
| Gmail | `Connect-Gmail.command` | Gmail **App Password** |
| Outlook / any IMAP | `Connect-Outlook.command` | App Password |
| Telegram | `Connect-Telegram.command` | Bot token from @BotFather (official, no ban risk) |
| Instagram | `Connect-Instagram.command` | ⚠️ experimental, test account only |
| Web chat | `web-widget/` | Drop-in bubble for any website |

## Tech stack

Python · FastAPI · SQLite · [lingua](https://github.com/pemistahl/lingua-py) · Ollama (optional) · Anthropic Claude API (optional) · Node + Baileys (WhatsApp) · vanilla JS/CSS · pytest · GitHub Actions.

## Tests

```bash
pytest tests/ -v
```
45+ tests cover language detection (all 5), negation, sentiment, scam, FAQ, VIP,
the reply-language guarantee, escalation, UTF-8 storage, idempotency, and the AI
fallback path — all offline, no key needed.

## Roadmap

- [x] 6 channels · three-tier AI · scam shield · portals · analytics · roles/products/FAQ
- [ ] Official WhatsApp Business API option
- [ ] Voice-note transcription
- [ ] Windows installer

## License

MIT — see [LICENSE](LICENSE).

## Live updates: polling, then WebSockets

The dashboard originally polled `/api/messages` and `/api/stats` every five
seconds. It now holds a WebSocket and refreshes the moment something changes,
with the poll kept as a fallback. Both paths are in the codebase on purpose.

### The numbers

| | Short polling | WebSocket |
|---|---|---|
| Requests per idle hour, one dashboard | 720 | 0 |
| Time to see a new message | 0–5s, average 2.5s | ~50ms |
| Server work when nothing happens | 720 queries, 720 responses | one idle socket |
| Recovery from a dropped connection | automatic, next tick | reconnect with backoff |
| Behind a proxy that strips `Upgrade` | works | fails |
| Load balancer with round-robin | works | needs sticky sessions |

### Why keep both

Polling is not the naive option. It is stateless, it survives anything, and a
dropped request costs five seconds and nothing else. For a tool that might be
running on a shop's wifi or over a hotel connection, that matters.

WebSockets remove the 2.5-second average latency and the 720 pointless requests
an hour, at the cost of a connection that has to be maintained, authenticated,
and given up on gracefully.

So the socket is the fast path and the poll is the safety net. The poll only
runs while the socket is down — never both at once — and the indicator in the
header shows which is active.

### Design decisions worth naming

**The socket carries hints, not data.** A broadcast says `{"type":"messages",
"reason":"ingest"}` and nothing more. The dashboard then re-fetches through the
existing REST endpoints, which already have authentication, rate limiting and
validation. Pushing message content down the socket would mean duplicating all
of that on a second path — and customer messages are exactly the data NoorDesk
exists to keep on the operator's own machine. One authenticated read path is
easier to secure than two. A test asserts the payload never grows message
fields, so this can't erode by accident.

**Publishing is safe from synchronous code.** Every endpoint is a plain `def`,
so FastAPI runs it in a worker thread, where touching an asyncio object is a
data race. `hub.publish()` hands the work to the event loop via
`call_soon_threadsafe`, and does nothing at all if no loop is bound. It also
swallows every exception: a dashboard missing a nudge is cosmetic, an API call
failing because a browser tab closed is not.

**Slow clients get dropped, not queued.** Each connection has a bounded queue of
8. A laptop that slept mid-session must not be able to grow the server's memory.
When a queue fills, the oldest hint is discarded — hints are idempotent, so
"something changed" twice means the same as once.

**Auth is in the first frame, not the URL.** A token in a query string ends up
in every access log and proxy trace on the way. The client sends it as the
opening message instead, and a connection that fails to authenticate within five
seconds is closed. The comparison is constant-time, so the socket can't be used
to guess the token a byte at a time.

**Reconnection backs off exponentially**, capped at 30 seconds, so a server
restart doesn't get hammered by every open dashboard simultaneously.

### Known limits

- **One process only.** The hub lives in memory. Running NoorDesk under multiple
  workers would need Redis pub/sub or similar; NoorDesk is single-operator by
  design, so that isn't built.
- **Needs `uvicorn[standard]`** for WebSocket support. Plain `uvicorn` will
  serve the app but the socket will never open — and the dashboard will quietly
  fall back to polling, which is the intended behaviour.

### Trying it

```bash
pip install 'uvicorn[standard]'
python -m pytest tests/test_live.py -q     # 14 tests
uvicorn webapp.main:app --reload
```

Open two browser tabs. Act in one; the other updates immediately. Then stop the
server — the header switches back to `auto-refresh · 5s` and the dashboard keeps
working.

`GET /api/live/stats` reports connected clients, events published, and events
dropped to slow consumers.

---

<div align="center">
<sub>Built by Ebin Raj · runs on your machine · your data stays yours</sub>
</div>
