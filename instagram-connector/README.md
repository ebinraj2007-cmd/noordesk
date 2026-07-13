# Instagram Connector — EXPERIMENTAL ⚠️

Reads and replies to Instagram DMs locally via [instagrapi](https://github.com/subzeroid/instagrapi).

## Read this first
- **This is unofficial and against Instagram's Terms of Service.** Instagram
  aggressively detects automation and **can lock or permanently ban the account**.
- **Use a throwaway / test account** — never a personal or business account you
  care about.
- It can hit **login challenges** (email/SMS codes) and rate limits; it may stop
  working at any time when Instagram changes things.
- For a real product, use the **official Instagram Messaging API** (needs a
  Business/Creator account, a Meta app, and webhooks) instead.

There is no reliable, ToS-compliant way to bundle Instagram DMs into a local
app — this connector exists for experimentation only.

## Run it
1. Start NoorDesk (`NoorDesk.command`).
2. Double-click **`Connect-Instagram.command`**, type `yes` to accept the risk,
   then enter the test account's username and password.
3. First run installs `instagrapi` in a local venv, then logs in. If Instagram
   sends a challenge code, follow the prompts.

DMs then appear on the dashboard; approved replies are sent back to the DM.
Your session is cached in `session.json` (git-ignored) to reduce logins.
