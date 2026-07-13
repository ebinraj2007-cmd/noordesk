/* NoorDesk web chat widget — drop this on any website.
 * It posts visitor messages into NoorDesk's dashboard (channel: "web").
 * Configure the endpoint by setting window.NOORDESK_CORE before loading this
 * script (default http://127.0.0.1:8000).
 */
(function () {
  var CORE = (window.NOORDESK_CORE || "http://127.0.0.1:8000").replace(/\/$/, "");
  var ACCENT = window.NOORDESK_ACCENT || "#4f46e5";

  var style = document.createElement("style");
  style.textContent =
    ".ndw-btn{position:fixed;right:20px;bottom:20px;width:56px;height:56px;border-radius:50%;" +
    "background:" + ACCENT + ";color:#fff;border:none;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.25);" +
    "font-size:24px;z-index:2147483000;display:flex;align-items:center;justify-content:center}" +
    ".ndw-panel{position:fixed;right:20px;bottom:88px;width:320px;max-width:calc(100vw - 40px);" +
    "background:#fff;color:#101828;border-radius:14px;box-shadow:0 16px 48px rgba(0,0,0,.28);" +
    "font-family:system-ui,-apple-system,Segoe UI,sans-serif;z-index:2147483000;overflow:hidden;display:none}" +
    ".ndw-panel.open{display:block}" +
    ".ndw-head{background:" + ACCENT + ";color:#fff;padding:14px 16px;font-weight:600}" +
    ".ndw-body{padding:14px 16px}" +
    ".ndw-body input,.ndw-body textarea{width:100%;box-sizing:border-box;margin-bottom:8px;padding:9px 11px;" +
    "border:1px solid #e4e7ec;border-radius:9px;font:inherit}" +
    ".ndw-body textarea{min-height:72px;resize:vertical}" +
    ".ndw-send{width:100%;padding:10px;border:none;border-radius:9px;background:" + ACCENT + ";color:#fff;" +
    "font-weight:600;cursor:pointer}" +
    ".ndw-ok{color:#15803d;font-size:14px;text-align:center;padding:8px 0}";
  document.head.appendChild(style);

  var btn = document.createElement("button");
  btn.className = "ndw-btn"; btn.setAttribute("aria-label", "Chat with us"); btn.textContent = "💬";
  document.body.appendChild(btn);

  var panel = document.createElement("div");
  panel.className = "ndw-panel";
  var head = document.createElement("div"); head.className = "ndw-head";
  head.textContent = window.NOORDESK_TITLE || "Chat with us";
  var body = document.createElement("div"); body.className = "ndw-body";
  var name = document.createElement("input"); name.placeholder = "Your name (optional)";
  var contact = document.createElement("input"); contact.placeholder = "Email or phone (optional)";
  var msg = document.createElement("textarea"); msg.placeholder = "How can we help?";
  var send = document.createElement("button"); send.className = "ndw-send"; send.textContent = "Send";
  body.appendChild(name); body.appendChild(contact); body.appendChild(msg); body.appendChild(send);
  panel.appendChild(head); panel.appendChild(body);
  document.body.appendChild(panel);

  btn.onclick = function () { panel.classList.toggle("open"); };

  send.onclick = function () {
    var text = msg.value.trim();
    if (!text) { msg.focus(); return; }
    var sender = (name.value.trim() || "Website visitor") + (contact.value.trim() ? " <" + contact.value.trim() + ">" : "");
    send.disabled = true; send.textContent = "Sending…";
    fetch(CORE + "/api/ingest", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: "web-" + Date.now(), sender: sender, channel: "web", raw_text: text })
    }).then(function () {
      body.replaceChildren();
      var ok = document.createElement("div"); ok.className = "ndw-ok";
      ok.textContent = "Thanks! We got your message and will get back to you soon.";
      body.appendChild(ok);
    }).catch(function () {
      send.disabled = false; send.textContent = "Try again";
    });
  };
})();
