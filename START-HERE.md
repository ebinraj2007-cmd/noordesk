# 🚀 NoorDesk — Start Here

A multilingual AI front desk that runs **entirely on your own computer**. It
reads incoming customer messages (WhatsApp, Gmail, Outlook, Telegram, Instagram,
web chat), detects the language, the tone, and the priority, and drafts a reply
in the customer's own language — which you approve and send.

> **Mac users:** the first time you open a `.command` file, macOS blocks it.
> **Right-click the file → Open → Open.** After that you can just double-click.

---

## 1. Start the app (always do this first)
Double-click **`NoorDesk.command`** (right-click → Open the first time).
It sets itself up on first run (~30–60 sec) and opens the dashboard at
**http://127.0.0.1:8000**. Leave this window open.

On first launch a **setup wizard** appears — pick your role (shop, restaurant,
personal, etc.), add products/prices, FAQ answers, opening hours, VIP contacts.
Reopen it anytime with the ⚙️ gear icon.

## 2. Turn on the smart AI (recommended — offline & free)
Out of the box, NoorDesk uses a **rule engine** (templates + greetings). For a
real chatbot that reads any message and replies naturally, add a local model:

1. Double-click **`Setup-Local-AI.command`**.
2. If Ollama isn't installed, it opens https://ollama.com — install it, then run
   the file again. It downloads a small model (`qwen2.5:3b`, ~2 GB, one time).
3. Restart `NoorDesk.command`. The header pill flips to **"Local AI"** and
   replies are now model-generated.

*(Alternatively, set an `ANTHROPIC_API_KEY` before launching to use Claude.)*

## 3. Connect your channels
With the app running, open the connector(s) you want (right-click → Open first time).
Each opens its own window — **leave them open**.

| Channel | File | What you need |
|---|---|---|
| WhatsApp | `Connect-WhatsApp.command` | Scan the QR with your phone |
| Gmail | `Connect-Gmail.command` | A Gmail **App Password** |
| Outlook | `Connect-Outlook.command` | An Outlook **App Password** |
| Telegram | `Connect-Telegram.command` | A bot token from **@BotFather** |
| Instagram | `Connect-Instagram.command` | ⚠️ experimental, test account only |
| Web chat | open `web-widget/index.html` | Drop-in bubble for any website |

See each folder's `README.md` for the exact steps.

## 4. Use it
- **Priority** tab = urgent messages from every channel in one place.
- One tab **per platform**; a **Scam** tab appears when fraud is caught.
- **📊** button = analytics (volume by channel / language / intent / hour).
- **Search** filters the queue; every card has **Approve & Send · Done · Snooze**.

## The one rule
Start **`NoorDesk.command` first**, then the connectors — they talk to it.
To stop everything: press **Ctrl+C** in each window (or just close them).

---

**Privacy:** everything runs on `127.0.0.1`. With the rule engine, no message
ever leaves your machine. The optional local AI (Ollama) also runs offline; only
the cloud AI (Claude) sends text off-device, and only if you add a key.
