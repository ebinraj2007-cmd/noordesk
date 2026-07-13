# WhatsApp Bridge

A small **Node.js** process that links NoorDesk to WhatsApp locally, using
[Baileys](https://github.com/WhiskeySockets/Baileys) with QR login. It runs
separately from the Python core so a WhatsApp hiccup can never crash the app.

```
WhatsApp phone ──QR──▶ Node bridge (Baileys) ──HTTP──▶ NoorDesk core (Python)
   incoming msg ───────────────────────────────▶ /api/ingest  (triaged, shown on dashboard)
   approved reply ◀───────────────── polls /api/messages (status = "sent")
```

## Setup (macOS)

1. Make sure **Node.js** is installed (`node --version`). If not, get the LTS
   installer from <https://nodejs.org>.
2. Start NoorDesk itself first (double-click `NoorDesk.command`).
3. Double-click `Connect-WhatsApp.command` (in the main folder). On first run it
   installs dependencies, then prints a **QR code**.
4. On your phone: **WhatsApp → Settings → Linked Devices → Link a Device**, scan
   the QR. Done — incoming messages now appear in the dashboard, and replies you
   approve are sent back automatically.

Manually: `cd whatsapp-bridge && npm install && npm start`.

## How replies work
You review each message on the dashboard and click **Send / Approve & Send**.
That marks it `sent`; the bridge picks it up within a few seconds and delivers
your drafted reply to the customer on WhatsApp. Nothing is ever sent without
your approval.

## Important
- This uses WhatsApp's **unofficial** web protocol. Great for personal / local
  use; **against WhatsApp's Terms of Service** for commercial use, and a number
  can be rate-limited or banned. For a commercial product, swap this bridge for
  the **official WhatsApp Business Cloud API** — the Python core does not change,
  only this folder does.
- The `auth/` folder stores your local WhatsApp session. Keep it private; delete
  it to unlink and re-scan.
