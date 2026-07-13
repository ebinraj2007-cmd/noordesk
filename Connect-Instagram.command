#!/bin/bash
# EXPERIMENTAL: connect NoorDesk to Instagram DMs (unofficial, high ban risk).
cd "$(dirname "$0")/instagram-connector"

echo "⚠️  EXPERIMENTAL — Instagram DM automation is unofficial, against Instagram's"
echo "   terms, and CAN GET THE ACCOUNT BANNED OR LOCKED. Use a TEST account only."
echo ""
read -p "Type 'yes' to continue: " ok
[ "$ok" = "yes" ] || { echo "Cancelled."; exit 0; }

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required."; read -p "Press Enter to close…"; exit 1
fi
if [ ! -d .venv ]; then
  echo "Setting up (first run, ~1 min)…"
  python3 -m venv .venv
  ./.venv/bin/pip install --quiet --upgrade pip
  ./.venv/bin/pip install --quiet instagrapi
fi

read -p "Instagram username: " IG_USERNAME
read -s -p "Instagram password (hidden as you type): " IG_PASSWORD
echo ""
export IG_USERNAME IG_PASSWORD
./.venv/bin/python instagram_poller.py
