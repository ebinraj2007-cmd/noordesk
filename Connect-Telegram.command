#!/bin/bash
# Double-click to connect NoorDesk to a Telegram bot (official, no ban risk).
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Run NoorDesk.command once first."
  read -p "Press Enter to close…"; exit 1
fi

echo "Connect NoorDesk to Telegram"
echo "Get a bot token: open Telegram, message @BotFather, send /newbot, follow the"
echo "steps, and copy the token it gives you (looks like 123456:ABC-DEF...)."
echo ""
read -p "Telegram bot token: " TELEGRAM_BOT_TOKEN
export TELEGRAM_BOT_TOKEN
echo ""
python3 telegram-connector/telegram_poller.py
