# Email Connector (Gmail · Outlook · any IMAP mailbox)

Connects NoorDesk to an email inbox over **IMAP + SMTP** — no OAuth, no cloud
project, standard library only. Watches your inbox and emails your approved
replies back.

```
inbox ──IMAP──▶ email_poller.py ──HTTP──▶ NoorDesk core (triage → dashboard)
approved reply ◀──SMTP── email_poller.py ◀── polls /api/messages (status = "sent")
```

## Gmail
1. Google Account → Security → turn on **2-Step Verification**.
2. **App passwords** → create one → copy the 16-character code.
   (<https://myaccount.google.com/apppasswords>)
3. Double-click **`Connect-Gmail.command`**, enter your address + the App Password.

## Outlook / Hotmail / Office365
1. Microsoft account → Security → **Advanced security options** → turn on
   two-step verification → **App passwords** → create one.
2. Double-click **`Connect-Outlook.command`**, enter your address + the App Password.
   *(Some work/school 365 accounts disable app passwords — use a personal account.)*

## Any other mailbox (Zoho, iCloud, Fastmail…)
Run it manually with your servers:
```bash
EMAIL_ADDRESS=you@zoho.com EMAIL_APP_PASSWORD=xxxx \
IMAP_HOST=imap.zoho.com SMTP_HOST=smtp.zoho.com SMTP_PORT=465 \
python3 email-connector/email_poller.py
```

## Notes
- Credentials are read from the environment and **never written to disk**.
- Inbound uses IMAP `BODY.PEEK`, so your emails are **not** marked as read.
- Nothing is emailed without your approval on the dashboard.
- Port 465 = SSL, port 587 = STARTTLS (handled automatically).
