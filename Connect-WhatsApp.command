#!/bin/bash
# Double-click to connect NoorDesk to WhatsApp.
# Make sure NoorDesk itself is already running (double-click NoorDesk.command first).
cd "$(dirname "$0")/whatsapp-bridge"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required for the WhatsApp connection."
  echo "Install the LTS version from https://nodejs.org , then run this again."
  read -p "Press Enter to close…"
  exit 1
fi

if [ ! -d node_modules ]; then
  echo "Setting up the WhatsApp bridge (first run, ~1 min)…"
  npm install
fi

echo ""
echo "Starting WhatsApp bridge. A QR code will appear below."
echo "On your phone: WhatsApp → Settings → Linked Devices → Link a Device → scan it."
echo ""
node index.js
