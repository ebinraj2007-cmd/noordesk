// NoorDesk dashboard.
// Security invariant: ALL customer-supplied text (sender, message body,
// translation, suggested reply) is inserted with textContent / createElement —
// never innerHTML — so a booby-trapped message cannot execute in the browser.
// The only innerHTML use is icon(), which renders hardcoded SVG strings below.

const LANG_NAME = { en: "English", ar: "Arabic", ml: "Malayalam", ta: "Tamil", fr: "French" };
const LANG_CODE = { English: "EN", Arabic: "AR", Malayalam: "ML", Tamil: "TA", French: "FR" };
const FONT_CLASS = { ar: "font-ar", ml: "font-ml", ta: "font-ta" };
const PRIORITY_LABEL = { 5: "Urgent", 4: "High", 3: "Medium", 2: "Low", 1: "Minimal" };
const CHANNEL_ICON = { email: "mail", whatsapp: "whatsapp", instagram: "instagram", telegram: "send", web: "globe", manual: "user" };
const CHANNEL_LABEL = { whatsapp: "WhatsApp", email: "Email", instagram: "Instagram", telegram: "Telegram", web: "Web chat", manual: "Manual" };
const CHANNEL_ORDER = ["whatsapp", "email", "instagram", "telegram", "web", "manual"];
const INTENT_META = {
  booking:       { icon: "calendar", color: "var(--blue)" },
  complaint:     { icon: "alert",    color: "var(--red)" },
  price_enquiry: { icon: "tag",      color: "var(--teal)" },
  support:       { icon: "lifebuoy", color: "var(--violet)" },
  spam:          { icon: "ban",      color: "var(--slate)" },
  general:       { icon: "chat",     color: "var(--slate)" },
};

// Static icon markup (Lucide/Tabler outline paths). Never holds user data.
const ICONS = {
  mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
  whatsapp: '<path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"/>',
  instagram: '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
  user: '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
  calendar: '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>',
  alert: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  tag: '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>',
  lifebuoy: '<circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/>',
  ban: '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
  languages: '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
  pie: '<path d="M21 12c.552 0 1.005-.449.95-.998a10 10 0 0 0-8.953-8.951c-.55-.055-.998.398-.998.95v8a1 1 0 0 0 1 1z"/><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>',
  inbox: '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
  sparkles: '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  send: '<path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/><path d="m21.854 2.147-10.94 10.939"/>',
  flame: '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
  shieldalert: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1 1 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
  clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  star: '<path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.12 2.12 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.12 2.12 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.12 2.12 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.12 2.12 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.12 2.12 0 0 0 1.597-1.16z"/>',
  repeat: '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/>',
  chart: '<path d="M3 3v16a2 2 0 0 0 2 2h16"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  eye: '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
  play: '<polygon points="6 3 20 12 6 21 6 3"/>',
  spark: '<path fill="currentColor" stroke="none" d="M12 2c.72 5.4 4.6 9.28 10 10-5.4.72-9.28 4.6-10 10-.72-5.4-4.6-9.28-10-10 5.4-.72 9.28-4.6 10-10z"/>',
};

// ---------- tiny safe-DOM helpers ----------

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text; // safe: no HTML injection
  return e;
}

function icon(name, cls) {
  const s = el("span", "ico" + (cls ? " " + cls : ""));
  // Static, hardcoded markup only (see ICONS above) — never user data.
  s.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (ICONS[name] || "") + "</svg>";
  return s;
}

function chip(cls, iconName, text) {
  const c = el("span", "chip" + (cls ? " " + cls : ""));
  if (iconName) c.appendChild(icon(iconName));
  if (text !== undefined) c.appendChild(el("span", null, text));
  return c;
}

function langify(node, lang) {
  if (FONT_CLASS[lang]) node.classList.add(FONT_CLASS[lang]);
  if (lang) node.lang = lang;
  if (lang === "ar") { node.dir = "rtl"; node.classList.add("rtl"); }
}

function fmtAgo(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return "";
  const s = (Date.now() - d.getTime()) / 1000;
  if (s < 45) return "just now";
  if (s < 3600) return Math.max(1, Math.floor(s / 60)) + "m ago";
  if (s < 86400) return Math.floor(s / 3600) + "h ago";
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

// ---------- server API (contract unchanged) ----------

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(path + " -> HTTP " + res.status);
  return res.json();
}

// ---------- connection + toasts ----------

let online = null;

function setConn(ok) {
  if (ok === online) return;
  online = ok;
  const box = document.getElementById("conn");
  box.classList.remove("wait");
  box.classList.toggle("off", !ok);
  document.getElementById("conn-label").textContent = ok ? "Live" : "Offline";
  if (!ok) toast("Connection lost — retrying every 5 s", "err");
}

function toast(msg, kind) {
  const t = el("div", "toast" + (kind ? " " + kind : ""), msg);
  document.getElementById("toasts").appendChild(t);
  setTimeout(() => { t.classList.add("out"); setTimeout(() => t.remove(), 320); }, 3600);
}

// ---------- stats ----------

function statHead(cardEl, iconName, label) {
  const h = el("div", "stat-head");
  h.appendChild(icon(iconName));
  h.appendChild(el("span", null, label));
  cardEl.appendChild(h);
}

function renderStats(s) {
  const box = document.getElementById("stats");
  box.replaceChildren();

  const total = el("div", "stat");
  statHead(total, "inbox", "Total messages");
  total.appendChild(el("div", "n", String(s.total || 0)));

  const review = el("div", "stat" + (s.needs_review > 0 ? " hot" : ""));
  statHead(review, "alert", "Needs review");
  review.appendChild(el("div", "n", String(s.needs_review || 0)));

  const langs = el("div", "stat wide");
  statHead(langs, "languages", "Languages");
  const lentries = Object.entries(s.by_language || {}).sort((a, b) => b[1] - a[1]);
  if (!lentries.length) {
    langs.appendChild(el("span", "none", "No messages yet"));
  } else {
    const cloud = el("div", "chips");
    lentries.forEach(([name, n]) => {
      const c = el("span", "chip");
      c.appendChild(el("b", "code", LANG_CODE[name] || name.slice(0, 2).toUpperCase()));
      c.appendChild(el("span", null, name));
      c.appendChild(el("b", "count", String(n)));
      cloud.appendChild(c);
    });
    langs.appendChild(cloud);
  }

  const intents = el("div", "stat wide");
  statHead(intents, "pie", "Intent mix");
  const ientries = Object.entries(s.by_intent || {}).sort((a, b) => b[1] - a[1]);
  if (!ientries.length) {
    intents.appendChild(el("span", "none", "No messages yet"));
  } else {
    const sum = ientries.reduce((acc, [, n]) => acc + n, 0);
    const bar = el("div", "mixbar");
    ientries.forEach(([k, n]) => {
      const seg = el("span");
      seg.style.width = (100 * n / sum) + "%";
      seg.style.background = (INTENT_META[k] || INTENT_META.general).color;
      seg.title = k.replace(/_/g, " ") + ": " + n;
      bar.appendChild(seg);
    });
    intents.appendChild(bar);
    const legend = el("div", "chips");
    ientries.forEach(([k, n]) => {
      const c = el("span", "chip legend");
      const dot = el("i", "dot2");
      dot.style.background = (INTENT_META[k] || INTENT_META.general).color;
      c.appendChild(dot);
      c.appendChild(el("span", null, k.replace(/_/g, " ")));
      c.appendChild(el("b", "count", String(n)));
      legend.appendChild(c);
    });
    intents.appendChild(legend);
  }

  box.append(total, review, langs, intents);
}

function setEngine(s) {
  const be = s.by_engine || {};
  const local = (be.local || 0) > 0;
  const cloud = (be.llm || 0) > 0;
  document.getElementById("engine").classList.toggle("ai", local || cloud);
  document.getElementById("engine-label").textContent = local ? "Local AI" : cloud ? "AI engine" : "Rule engine";
  document.getElementById("engine-note").textContent = local
    ? "Local AI active — a small model on this machine drafts the replies, fully offline."
    : cloud
    ? "AI engine active — drafting replies, rules as fallback."
    : "Rule engine (offline). Run Ollama to enable the local AI.";
}

// ---------- message cards ----------

const seen = new Set();

function card(m) {
  const p = Math.min(5, Math.max(1, Number(m.priority) || 1));
  const c = el("article", "card" + (m.scam ? " scam" : m.needs_review ? " review" : "") + (m.status === "sent" ? " done" : ""));
  c.dataset.p = String(p);
  if (!seen.has(m.id)) c.classList.add("enter");

  // Header: channel + sender + time | priority badge
  const head = el("div", "card-head");
  const who = el("div", "who");
  who.appendChild(icon(CHANNEL_ICON[m.channel] || "user", m.channel || "manual"));
  const sender = el("span", "sender", m.sender || "unknown");
  sender.title = (m.channel || "manual") + " · " + (m.sender || "unknown");
  who.appendChild(sender);
  who.appendChild(el("span", "sep", "·"));
  const t = el("span", "time", fmtAgo(m.created_at));
  t.dataset.ts = m.created_at || "";
  const dt = new Date(m.created_at);
  if (!isNaN(dt)) t.title = dt.toLocaleString();
  who.appendChild(t);
  head.appendChild(who);
  const pb = el("span", "prio-badge");
  pb.appendChild(el("b", null, "P" + p));
  pb.appendChild(el("span", null, PRIORITY_LABEL[p]));
  head.appendChild(pb);
  c.appendChild(head);

  // Chips: language + confidence, intent, angry, needs review
  const chips = el("div", "chips row");
  const langChip = el("span", "chip");
  langChip.appendChild(el("b", "code", (m.detected_language || "??").toUpperCase()));
  langChip.appendChild(el("span", null, LANG_NAME[m.detected_language] || m.detected_language || "Unknown"));
  if (typeof m.language_confidence === "number") {
    const pct = Math.round(m.language_confidence * 100);
    langChip.appendChild(el("span", "conf", pct + "%"));
    langChip.title = "Language detection confidence: " + pct + "%";
  }
  chips.appendChild(langChip);
  const imeta = INTENT_META[m.intent] || INTENT_META.general;
  const intentChip = chip("tint", imeta.icon, String(m.intent || "general").replace(/_/g, " "));
  intentChip.style.color = imeta.color;
  chips.appendChild(intentChip);
  if (m.sentiment === "angry") {
    const angry = chip("tint", "flame", "angry");
    angry.style.color = "var(--red)";
    chips.appendChild(angry);
  }
  if (m.scam) chips.appendChild(chip("scam", "shieldalert", "possible scam"));
  if (m.needs_review && !m.scam) chips.appendChild(chip("hot", "eye", "needs review"));
  if (m.vip) chips.appendChild(chip("vip", "star", "VIP"));
  if (m.repeat) chips.appendChild(chip("", "repeat", "returning"));
  c.appendChild(chips);

  // Body: customer message | suggested reply
  const body = el("div", "card-body");

  const mcol = el("div");
  mcol.appendChild(el("h4", "lab", "Customer message"));
  if (m.translation) {
    const tr = el("div", "translation");
    tr.appendChild(icon("globe"));
    tr.appendChild(el("span", null, m.translation)); // owner (English) view
    mcol.appendChild(tr);
  }
  const msg = el("div", "bubble msg", m.raw_text);
  langify(msg, m.detected_language);
  mcol.appendChild(msg);
  body.appendChild(mcol);

  const rcol = el("div");
  const rhead = el("div", "reply-head");
  rhead.appendChild(el("h4", "lab", "Suggested reply"));
  if (m.engine_used === "llm" || m.engine_used === "local")
    rhead.appendChild(chip("ai", "sparkles", m.engine_used === "local" ? "Local AI" : "AI drafted"));
  rcol.appendChild(rhead);
  if (m.suggested_reply) {
    const reply = el("div", "bubble reply", m.suggested_reply);
    langify(reply, m.detected_language);
    rcol.appendChild(reply);
  } else if (m.scam) {
    const box = el("div", "bubble scam-warn");
    box.appendChild(icon("shieldalert"));
    const w = el("div");
    w.appendChild(el("div", "scam-title", "Possible scam — reply blocked"));
    if (m.scam_reasons) w.appendChild(el("div", "scam-reasons", m.scam_reasons));
    box.appendChild(w);
    rcol.appendChild(box);
  } else {
    const spam = el("div", "bubble spam");
    spam.appendChild(icon("ban"));
    spam.appendChild(el("span", null, "No reply — flagged as spam"));
    rcol.appendChild(spam);
  }

  // Actions: Send (if a reply exists) + Done + Snooze — a real to-do workflow.
  const acts = el("div", "acts");
  if (m.suggested_reply) {
    if (m.status === "sent") {
      const badge = el("span", "sent-badge");
      badge.appendChild(icon("check"));
      badge.appendChild(el("span", null, "Sent"));
      acts.appendChild(badge);
    } else {
      const send = el("button", "btn primary sm");
      send.type = "button";
      send.appendChild(icon("send"));
      send.appendChild(el("span", null, m.needs_review ? "Approve & Send" : "Send"));
      send.onclick = () => sendReply(m.id, send);
      acts.appendChild(send);
    }
  }
  const done = el("button", "btn sm ghost");
  done.type = "button"; done.title = "Mark handled";
  done.appendChild(icon("check")); done.appendChild(el("span", null, "Done"));
  done.onclick = () => markMessage(m.id, "done");
  acts.appendChild(done);
  const snooze = el("button", "btn sm ghost");
  snooze.type = "button"; snooze.title = "Snooze";
  snooze.appendChild(icon("clock")); snooze.appendChild(el("span", null, "Snooze"));
  snooze.onclick = () => markMessage(m.id, "snoozed");
  acts.appendChild(snooze);
  rcol.appendChild(acts);

  body.appendChild(rcol);
  c.appendChild(body);
  return c;
}

function emptyState() {
  const box = el("div", "empty");
  const art = el("div", "empty-art");
  art.appendChild(icon("inbox"));
  art.appendChild(icon("spark", "spark"));
  box.appendChild(art);
  const down = online === false;
  box.appendChild(el("h3", null, down ? "Can't reach NoorDesk" : "Inbox is clear"));
  box.appendChild(el("p", null, down
    ? "The local server isn't responding. Start it with ./start.sh — this page reconnects automatically."
    : "Run triage to process the sample inbox. Live WhatsApp and email messages appear here on their own."));
  if (!down) {
    const b = el("button", "btn primary");
    b.type = "button";
    b.appendChild(icon("play"));
    b.appendChild(el("span", null, "Run Triage"));
    b.onclick = runTriage;
    box.appendChild(b);
  }
  return box;
}

function renderQueue(rows, emptyText) {
  const q = document.getElementById("queue");
  const head = document.getElementById("queue-head");
  q.replaceChildren();
  if (!rows.length) {
    head.classList.add("hide");
    if (emptyText) {
      const e = el("div", "empty");
      e.appendChild(el("p", null, emptyText));
      q.appendChild(e);
    } else {
      q.appendChild(emptyState());
    }
    return;
  }
  head.classList.remove("hide");
  const nReview = rows.filter((r) => r.needs_review && r.status !== "sent").length;
  document.getElementById("queue-count").textContent =
    rows.length + (rows.length === 1 ? " message" : " messages") +
    (nReview ? " · " + nReview + " awaiting approval" : "");
  rows.forEach((m, i) => {
    const node = card(m); // API order kept: needs_review first, then priority desc
    if (node.classList.contains("enter")) node.style.animationDelay = Math.min(i * 45, 270) + "ms";
    q.appendChild(node);
  });
  rows.forEach((m) => seen.add(m.id));
}

function refreshTimes() {
  document.querySelectorAll(".time[data-ts]").forEach((n) => {
    if (n.dataset.ts) n.textContent = fmtAgo(n.dataset.ts);
  });
}

// ---------- portals: one page per channel + a cross-channel Priority page ----------

let allRows = [];
let portal = "priority";
let query = "";
let analyticsOpen = false;
try { portal = localStorage.getItem("noordesk-portal") || "priority"; } catch (e) { /* private mode */ }

function activeRows() { return allRows.filter((r) => r.status !== "done" && r.status !== "snoozed"); }
function matchesQuery(r) {
  if (!query) return true;
  const q = query.toLowerCase();
  return [r.raw_text, r.sender, r.translation, r.suggested_reply]
    .some((v) => (v || "").toLowerCase().indexOf(q) !== -1);
}

function isUrgent(r) { return Number(r.priority) >= 4 || r.needs_review; }

function portalMatch(r, key) {
  if (key === "priority") return isUrgent(r);
  if (key === "scam") return !!r.scam;
  if (key === "all") return true;
  return r.channel === key;
}

function renderPortals(rows) {
  const nav = document.getElementById("portals");
  const defs = [
    { key: "priority", label: "Priority", icon: "flame", urgent: true },
  ];
  if (rows.some((r) => r.scam)) defs.push({ key: "scam", label: "Scam", icon: "shieldalert", urgent: true });
  defs.push({ key: "all", label: "All", icon: "inbox" });
  CHANNEL_ORDER.forEach((ch) => {
    if (rows.some((r) => r.channel === ch)) defs.push({ key: ch, label: CHANNEL_LABEL[ch] || ch, icon: CHANNEL_ICON[ch] || "user" });
  });
  if (!defs.some((d) => d.key === portal)) portal = "priority";
  nav.replaceChildren();
  defs.forEach((d) => {
    const b = el("button", "portal" + (d.urgent ? " urgent" : "") + (d.key === portal ? " active" : ""));
    b.type = "button";
    b.appendChild(icon(d.icon));
    b.appendChild(el("span", null, d.label));
    b.appendChild(el("span", "pcount", String(rows.filter((r) => portalMatch(r, d.key)).length)));
    b.onclick = () => {
      portal = d.key;
      try { localStorage.setItem("noordesk-portal", portal); } catch (e) { /* private mode */ }
      renderPortals(activeRows());
      applyPortal();
    };
    nav.appendChild(b);
  });
}

function applyPortal() {
  const sb = document.getElementById("searchbar");
  if (sb) sb.classList.toggle("hide", analyticsOpen || !allRows.length);
  const base = activeRows();
  const rows = base.filter((r) => portalMatch(r, portal) && matchesQuery(r));
  let emptyText = null;
  if (!rows.length) {
    if (query) emptyText = "No messages match your search.";
    else if (!allRows.length) emptyText = null;               // run-triage empty
    else if (!base.length) emptyText = "All caught up — no active messages.";
    else emptyText = portal === "priority"
      ? "No high-priority messages right now — you're all caught up."
      : "No messages in " + (CHANNEL_LABEL[portal] || portal) + " yet.";
  }
  renderQueue(rows, emptyText);
}

// ---------- data loading (5 s auto-refresh, unchanged contract) ----------

let lastSig = "";
let busy = false;     // an action (run/send/clear) is in flight
let inflight = false; // a poll is in flight

async function load(force) {
  if (inflight && !force) return;
  inflight = true;
  try {
    const [rows, stats] = await Promise.all([api("/api/messages"), api("/api/stats")]);
    setConn(true);
    const sig = JSON.stringify(rows) + "|" + JSON.stringify(stats);
    if (!force && sig === lastSig) { refreshTimes(); return; }
    lastSig = sig;
    renderStats(stats);
    setEngine(stats);
    allRows = rows;
    renderPortals(activeRows());
    applyPortal();
    if (analyticsOpen) renderAnalytics();
  } catch (err) {
    setConn(false);
    lastSig = "";
    // Keep whatever is on screen; only draw placeholders on a blank page.
    if (!document.getElementById("stats").childElementCount) {
      renderStats({ total: 0, needs_review: 0, by_language: {}, by_intent: {} });
    }
    if (!document.querySelector("#queue .card")) renderQueue([]);
  } finally {
    inflight = false;
  }
}

// ---------- actions ----------

async function runTriage() {
  if (busy) return;
  busy = true;
  const b = document.getElementById("run");
  const lbl = document.getElementById("run-label");
  b.disabled = true; b.classList.add("loading"); lbl.textContent = "Processing…";
  try {
    const r = await api("/api/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
    toast("Processed " + r.processed + (r.processed === 1 ? " message" : " messages"), "ok");
    await load(true);
  } catch (err) {
    setConn(false);
    toast("Triage failed — is the server running?", "err");
  }
  b.disabled = false; b.classList.remove("loading"); lbl.textContent = "Run Triage";
  busy = false;
}

async function clearQueue() {
  if (busy) return;
  busy = true;
  const b = document.getElementById("clear");
  b.disabled = true;
  try {
    await api("/api/clear", { method: "POST" });
    seen.clear();
    toast("Queue cleared", "ok");
    await load(true);
  } catch (err) {
    setConn(false);
    toast("Couldn't clear the queue", "err");
  }
  b.disabled = false;
  busy = false;
}

async function sendReply(id, btn) {
  if (busy) return;
  busy = true;
  const lbl = btn.querySelector("span:last-child");
  btn.disabled = true; btn.classList.add("loading");
  if (lbl) lbl.textContent = "Sending…";
  try {
    await api("/api/send", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id }) });
    await load(true);
  } catch (err) {
    setConn(false);
    toast("Couldn't send the reply", "err");
    btn.disabled = false; btn.classList.remove("loading");
    if (lbl) lbl.textContent = "Retry send";
  }
  busy = false;
}

// ---------- theme (auto respects prefers-color-scheme) ----------

const THEMES = ["auto", "light", "dark"];

function applyTheme(mode) {
  if (mode === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = mode;
  const btn = document.getElementById("theme");
  btn.title = "Theme: " + mode + " (click to change)";
}

function initTheme() {
  let saved = null;
  try { saved = localStorage.getItem("noordesk-theme"); } catch (err) { /* private mode */ }
  applyTheme(THEMES.includes(saved) ? saved : "auto");
}

document.getElementById("theme").onclick = () => {
  const cur = document.documentElement.dataset.theme || "auto";
  const next = THEMES[(THEMES.indexOf(cur) + 1) % THEMES.length];
  try { localStorage.setItem("noordesk-theme", next); } catch (err) { /* private mode */ }
  applyTheme(next);
};

// ---------- boot ----------

document.getElementById("run").onclick = runTriage;
document.getElementById("clear").onclick = clearQueue;
initTheme();
load();

// Live auto-refresh: new WhatsApp/email messages appear on their own.
// Pauses briefly while you're interacting so it doesn't fight your clicks.
let lastAction = 0;
document.addEventListener("click", () => { lastAction = Date.now(); });
setInterval(() => {
  if (busy || document.hidden) return;
  if (Date.now() - lastAction > 3000) load();
}, 5000);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && !busy) load();
});

// ---------- setup wizard: roles + products ----------

const setupEl = document.getElementById("setup");
let currentProfile = null;
let setupRole = null;
let roleList = [];
const personalRoles = new Set();

function val(id) { return document.getElementById(id).value.trim(); }

async function loadRoles() {
  if (roleList.length) return;
  try {
    roleList = await api("/api/roles");
    roleList.forEach((r) => { if (r.personal) personalRoles.add(r.key); });
  } catch (e) { roleList = []; }
  const grid = document.getElementById("role-grid");
  grid.replaceChildren();
  roleList.forEach((r) => {
    const b = el("button", "role-chip");
    b.type = "button";
    b.dataset.role = r.key;
    b.appendChild(el("span", "rdot"));
    b.appendChild(el("span", null, r.label));
    b.onclick = () => selectRole(r.key);
    grid.appendChild(b);
  });
}

function selectRole(role) {
  setupRole = role;
  document.querySelectorAll(".role-chip").forEach((c) =>
    c.classList.toggle("selected", c.dataset.role === role));
  const personal = personalRoles.has(role);
  document.getElementById("fields-business").classList.toggle("hide", personal);
  document.getElementById("fields-personal").classList.toggle("hide", !personal);
  document.getElementById("fields-tone").classList.remove("hide");
  document.getElementById("setup-save").disabled = false;
}

// ----- product rows -----
function prodRow(name, price) {
  const row = el("div", "prod-row");
  const n = el("input"); n.type = "text"; n.placeholder = "Item name"; n.value = name || ""; n.className = "p-name";
  const p = el("input"); p.type = "text"; p.placeholder = "Price"; p.value = price || ""; p.className = "p-price";
  const d = el("button", "prod-del"); d.type = "button"; d.title = "Remove";
  d.appendChild(icon("trash"));
  d.onclick = () => { row.remove(); syncProdEmpty(); };
  row.append(n, p, d);
  return row;
}
function syncProdEmpty() {
  const list = document.getElementById("prod-list");
  let e = list.querySelector(".prod-empty");
  const has = list.querySelectorAll(".prod-row").length > 0;
  if (!has && !e) list.appendChild(el("div", "prod-empty", "No items yet. Add products so the AI can quote prices."));
  if (has && e) e.remove();
}
function setProducts(products) {
  const list = document.getElementById("prod-list");
  list.replaceChildren();
  (products || []).forEach((p) => list.appendChild(prodRow(p.name, p.price)));
  syncProdEmpty();
}
function collectProducts() {
  return [...document.querySelectorAll("#prod-list .prod-row")].map((row) => ({
    name: row.querySelector(".p-name").value.trim(),
    price: row.querySelector(".p-price").value.trim(),
  })).filter((p) => p.name);
}
document.getElementById("prod-add").onclick = () => {
  const list = document.getElementById("prod-list");
  const e = list.querySelector(".prod-empty"); if (e) e.remove();
  const row = prodRow("", "");
  list.appendChild(row);
  row.querySelector(".p-name").focus();
};

async function openSetup(p) {
  await loadRoles();
  setupRole = p && p.configured ? p.role : null;
  document.querySelectorAll(".role-chip").forEach((c) =>
    c.classList.toggle("selected", c.dataset.role === setupRole));
  if (setupRole) selectRole(setupRole);
  else {
    document.getElementById("fields-business").classList.add("hide");
    document.getElementById("fields-personal").classList.add("hide");
    document.getElementById("fields-tone").classList.add("hide");
    document.getElementById("setup-save").disabled = true;
  }
  if (p) {
    document.getElementById("f-name-biz").value = personalRoles.has(p.role) ? "" : (p.name || "");
    document.getElementById("f-name-me").value = personalRoles.has(p.role) ? (p.name || "") : "";
    document.getElementById("f-sells").value = p.sells || "";
    document.getElementById("f-hours").value = p.hours || "";
    document.getElementById("f-phone").value = p.phone || "";
    document.getElementById("f-location").value = p.location || "";
    document.getElementById("f-tone").value = p.tone || "friendly";
    setProducts(p.products);
    setFaqs(p.faqs);
    document.getElementById("f-away").checked = !!p.away_enabled;
    document.getElementById("f-open").value = p.open_time || "09:00";
    document.getElementById("f-close").value = p.close_time || "18:00";
    document.getElementById("f-vip").value = (p.vip || []).join("\n");
  }
  setupEl.classList.remove("hide");
}
function closeSetup() { setupEl.classList.add("hide"); }

document.getElementById("setup-open").onclick = () => openSetup(currentProfile);
document.getElementById("setup-later").onclick = closeSetup;
setupEl.onclick = (e) => { if (e.target === setupEl) closeSetup(); };

document.getElementById("setup-save").onclick = async () => {
  if (!setupRole) return;
  const personal = personalRoles.has(setupRole);
  const body = personal
    ? { role: setupRole, name: val("f-name-me"), tone: val("f-tone"), products: [] }
    : { role: setupRole, name: val("f-name-biz"), sells: val("f-sells"), hours: val("f-hours"),
        phone: val("f-phone"), location: val("f-location"), tone: val("f-tone"),
        products: collectProducts(), faqs: collectFaqs(),
        vip: document.getElementById("f-vip").value.split("\n").map((s) => s.trim()).filter(Boolean),
        away_enabled: document.getElementById("f-away").checked,
        open_time: document.getElementById("f-open").value || "09:00",
        close_time: document.getElementById("f-close").value || "18:00" };
  try {
    const r = await api("/api/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    currentProfile = r.profile;
    closeSetup();
    toast("Saved — replies are now tailored to you", "ok");
  } catch (e) {
    toast("Couldn't save your setup", "err");
  }
};

(async () => {
  try {
    currentProfile = await api("/api/profile");
    if (!currentProfile.configured) openSetup(currentProfile);
  } catch (e) { /* server not up yet */ }
})();

// ---------- FAQ editor ----------
function faqRow(q, a) {
  const row = el("div", "prod-row faq-row");
  const qi = el("input"); qi.type = "text"; qi.placeholder = "If they ask… (e.g. do you deliver)"; qi.value = q || ""; qi.className = "q-q";
  const ai = el("input"); ai.type = "text"; ai.placeholder = "Answer with…"; ai.value = a || ""; ai.className = "q-a";
  const d = el("button", "prod-del"); d.type = "button"; d.title = "Remove"; d.appendChild(icon("trash"));
  d.onclick = () => row.remove();
  row.append(qi, ai, d);
  return row;
}
function setFaqs(faqs) {
  const l = document.getElementById("faq-list"); l.replaceChildren();
  (faqs || []).forEach((f) => l.appendChild(faqRow(f.q, f.a)));
}
function collectFaqs() {
  return [...document.querySelectorAll("#faq-list .faq-row")].map((r) => ({
    q: r.querySelector(".q-q").value.trim(), a: r.querySelector(".q-a").value.trim(),
  })).filter((f) => f.q && f.a);
}
document.getElementById("faq-add").onclick = () => {
  const r = faqRow("", ""); document.getElementById("faq-list").appendChild(r); r.querySelector(".q-q").focus();
};

// ---------- message workflow: done / snooze ----------
async function markMessage(id, status) {
  try {
    await api("/api/mark", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id, status }) });
    toast(status === "done" ? "Marked done" : "Snoozed", "ok");
    await load(true);
  } catch (e) { toast("Couldn't update the message", "err"); }
}

// ---------- search ----------
const searchInput = document.getElementById("search");
if (searchInput) searchInput.addEventListener("input", () => { query = searchInput.value.trim(); applyPortal(); });

// ---------- analytics ----------
document.getElementById("analytics-open").onclick = () => {
  analyticsOpen = !analyticsOpen;
  document.getElementById("analytics-open").classList.toggle("active", analyticsOpen);
  document.getElementById("analytics").classList.toggle("hide", !analyticsOpen);
  ["portals", "queue-head", "queue"].forEach((id) => {
    const n = document.getElementById(id); if (n) n.classList.toggle("hide", analyticsOpen);
  });
  if (analyticsOpen) renderAnalytics();
  else { renderPortals(activeRows()); applyPortal(); }
};

function countBy(rows, fn) {
  const m = {};
  rows.forEach((r) => { const k = fn(r); if (k == null) return; m[k] = (m[k] || 0) + 1; });
  return Object.entries(m);
}
function barBlock(title, entries, colorFn) {
  const wrap = el("div", "an-block");
  wrap.appendChild(el("h4", "an-title", title));
  if (!entries.length) { wrap.appendChild(el("div", "an-empty", "No data yet.")); return wrap; }
  const total = entries.reduce((s, [, n]) => s + n, 0) || 1;
  entries.sort((a, b) => b[1] - a[1]).forEach(([k, n]) => {
    const row = el("div", "an-row");
    row.appendChild(el("span", "an-label", k));
    const track = el("div", "an-track"); const bar = el("div", "an-bar");
    bar.style.width = Math.round(100 * n / total) + "%";
    if (colorFn) bar.style.background = colorFn(k);
    track.appendChild(bar); row.appendChild(track);
    row.appendChild(el("span", "an-n", String(n)));
    wrap.appendChild(row);
  });
  return wrap;
}
function renderAnalytics() {
  const box = document.getElementById("analytics"); box.replaceChildren();
  const rows = allRows;
  const metrics = el("div", "an-metrics");
  const mk = (label, v, cls) => { const c = el("div", "an-metric" + (cls ? " " + cls : "")); c.appendChild(el("div", "an-mv", String(v))); c.appendChild(el("div", "an-ml", label)); return c; };
  metrics.appendChild(mk("Total", rows.length));
  metrics.appendChild(mk("Needs review", rows.filter((r) => r.needs_review && !r.scam).length, "warn"));
  metrics.appendChild(mk("Scam blocked", rows.filter((r) => r.scam).length, "danger"));
  metrics.appendChild(mk("Returning", rows.filter((r) => r.repeat).length));
  metrics.appendChild(mk("Handled", rows.filter((r) => r.status === "sent" || r.status === "done").length, "ok"));
  box.appendChild(metrics);
  const grid = el("div", "an-grid");
  grid.appendChild(barBlock("By channel", countBy(rows, (r) => CHANNEL_LABEL[r.channel] || r.channel)));
  grid.appendChild(barBlock("By language", countBy(rows, (r) => LANG_NAME[r.detected_language] || r.detected_language)));
  grid.appendChild(barBlock("By intent", countBy(rows, (r) => String(r.intent || "general").replace(/_/g, " ")),
    (k) => (INTENT_META[k.replace(/ /g, "_")] || {}).color || "var(--accent)"));
  grid.appendChild(barBlock("Busiest hours", countBy(rows, (r) => { const d = new Date(r.created_at); return isNaN(d) ? null : String(d.getHours()).padStart(2, "0") + ":00"; })));
  box.appendChild(grid);
}
