# Telegram Connector

The **reliable** social channel — official Telegram Bot API, standard library
only, no ban risk. Long-polls for messages and sends approved replies back.

## Get a bot token (2 minutes)
1. Open Telegram, search for **@BotFather**.
2. Send `/newbot`, pick a name and a username.
3. Copy the token it gives you (e.g. `123456:ABC-DEF...`).

## Run it
1. Start NoorDesk (`NoorDesk.command`).
2. Double-click **`Connect-Telegram.command`**, paste the token.
3. Message your new bot on Telegram — it appears on the dashboard. Approve a
   reply and it's sent back in the chat.

Manual: `TELEGRAM_BOT_TOKEN=xxx python3 telegram-connector/telegram_poller.py`
