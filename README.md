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

<div align="center">
<sub>Built by Ebin Raj · runs on your machine · your data stays yours</sub>
</div>
