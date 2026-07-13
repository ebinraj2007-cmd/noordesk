#!/bin/bash
# Double-click to connect NoorDesk to Outlook / Hotmail / Office365.
# Make sure NoorDesk itself is already running (NoorDesk.command) first.
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Run NoorDesk.command once first to set it up."
  read -p "Press Enter to close…"; exit 1
fi

echo "Connect NoorDesk to Outlook"
echo "You need an *App Password* (Microsoft account -> Security -> Advanced security"
echo "options -> App passwords; requires two-step verification turned on)."
echo "Note: some work/school (Office 365) accounts disable app passwords — use a"
echo "personal Outlook/Hotmail account, or ask your admin."
echo ""
read -p "Your Outlook email: " EMAIL_ADDRESS
read -s -p "App Password (hidden as you type): " EMAIL_APP_PASSWORD
echo ""
export EMAIL_ADDRESS EMAIL_APP_PASSWORD
export IMAP_HOST="outlook.office365.com" SMTP_HOST="smtp.office365.com" SMTP_PORT="587" PROVIDER="Outlook"
echo ""
python3 email-connector/email_poller.py
