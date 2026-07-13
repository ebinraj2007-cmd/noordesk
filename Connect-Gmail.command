#!/bin/bash
# Double-click to connect NoorDesk to Gmail.
# Make sure NoorDesk itself is already running (NoorDesk.command) first.
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Run NoorDesk.command once first to set it up."
  read -p "Press Enter to close…"; exit 1
fi

echo "Connect NoorDesk to Gmail"
echo "You need a Gmail *App Password* (not your normal password)."
echo "Get one: Google Account -> Security -> 2-Step Verification -> App passwords."
echo "See email-connector/README.md for step-by-step help."
echo ""
read -p "Your Gmail address: " EMAIL_ADDRESS
read -s -p "Gmail App Password (hidden as you type): " EMAIL_APP_PASSWORD
echo ""
export EMAIL_ADDRESS EMAIL_APP_PASSWORD
export IMAP_HOST="imap.gmail.com" SMTP_HOST="smtp.gmail.com" SMTP_PORT="465" PROVIDER="Gmail"
echo ""
python3 email-connector/email_poller.py
