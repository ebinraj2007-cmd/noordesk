// NoorDesk WhatsApp bridge (local, Baileys, QR login).
//
// Inbound : incoming WhatsApp messages are POSTed to the NoorDesk core, which
//           triages them and shows them on the dashboard.
// Outbound: replies you APPROVE on the dashboard (status = "sent") are polled
//           here and delivered back to the customer on WhatsApp.
//
// NOTE: this uses WhatsApp's unofficial web protocol (fine for personal/local
// use; against WhatsApp's ToS for commercial use — swap for the official
// Business Cloud API when you go commercial). Nothing in the Python core changes.

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
  Browsers,
} = require("@whiskeysockets/baileys");
const qrcode = require("qrcode-terminal");
const pino = require("pino");

const CORE = process.env.NOORDESK_CORE || "http://127.0.0.1:8000";
const delivered = new Set();

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState("auth");
  // Pin the current WhatsApp-Web version — without this, WhatsApp rejects the
  // handshake and the connection drops in a loop before the QR can appear.
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    browser: Browsers.macOS("Desktop"),
    printQRInTerminal: false,
    logger: pino({ level: "silent" }),
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (u) => {
    const { connection, lastDisconnect, qr } = u;
    if (qr) {
      console.log("\nScan this QR in WhatsApp → Settings → Linked Devices:\n");
      qrcode.generate(qr, { small: true });
    }
    if (connection === "close") {
      const code = lastDisconnect?.error?.output?.statusCode;
      if (code === DisconnectReason.loggedOut || code === 401) {
        console.log("Logged out. Delete the 'auth' folder and run again to re-link.");
        return;
      }
      console.log("Connection dropped, reconnecting in 3s…");
      setTimeout(start, 3000);
    } else if (connection === "open") {
      console.log("✓ WhatsApp connected. NoorDesk is now handling your messages.");
      pollOutbox(sock);
    }
  });

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;
    for (const m of messages) {
      if (m.key.fromMe) continue;
      const text =
        m.message?.conversation || m.message?.extendedTextMessage?.text;
      if (!text) continue;
      const sender = m.key.remoteJid;
      try {
        await fetch(CORE + "/api/ingest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id: m.key.id,
            sender,
            channel: "whatsapp",
            raw_text: text,
          }),
        });
        console.log("→ received & triaged a message from", sender);
      } catch (e) {
        console.log("Could not reach NoorDesk core — is it running?", e.message);
      }
    }
  });
}

// Deliver replies you approved on the dashboard.
function pollOutbox(sock) {
  setInterval(async () => {
    try {
      const rows = await (await fetch(CORE + "/api/messages")).json();
      for (const r of rows) {
        if (
          r.channel === "whatsapp" &&
          r.status === "sent" &&
          r.suggested_reply &&
          !delivered.has(r.id)
        ) {
          await sock.sendMessage(r.sender, { text: r.suggested_reply });
          delivered.add(r.id);
          console.log("← sent approved reply to", r.sender);
        }
      }
    } catch (e) {
      // core not up yet; try again next tick
    }
  }, 4000);
}

start();
