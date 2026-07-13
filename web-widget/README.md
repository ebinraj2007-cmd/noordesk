# Web Chat Widget

A tiny embeddable chat bubble for any website. Visitor messages drop straight
into your NoorDesk dashboard (channel: **web**), triaged like every other channel.

## Try the demo
1. Start NoorDesk (`NoorDesk.command`).
2. Open `web-widget/index.html` in your browser.
3. Click the 💬 bubble, send a message — it appears on the dashboard.

## Put it on your website
Add these two lines before `</body>`, and host `widget.js` alongside your site:
```html
<script>window.NOORDESK_CORE = "http://127.0.0.1:8000";</script>
<script src="widget.js"></script>
```
Optional: `window.NOORDESK_TITLE` (header text) and `window.NOORDESK_ACCENT` (color).

## Notes
- The widget is **inbound** (visitor → dashboard). You reply from your own
  channels; the message includes any email/phone the visitor leaves.
- For a public website to reach NoorDesk, your machine must be reachable at
  `NOORDESK_CORE` (e.g. via a tunnel like Cloudflare Tunnel). On a locally-served
  site it works out of the box (CORS is enabled on the API).
