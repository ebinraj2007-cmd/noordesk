# Security & Pre-Deployment Notes

NoorDesk defaults to a single operator running it locally on `127.0.0.1`.
Everything below lets you take it to a shared/exposed host safely. Each item
maps to the standard pre-deployment checklist.

## 1. Authorization
There is one tenant: the operator. Every message record belongs to that
operator's workspace, so we gate all **state-changing** endpoints
(`/api/run`, `/api/ingest`, `/api/send`, `/api/mark`, `/api/clear`,
`/api/profile` POST) behind a shared operator token.

Set it before exposing the app:
```bash
export NOORDESK_TOKEN="$(openssl rand -hex 32)"
```
Clients send `Authorization: Bearer <token>`. With no token set, NoorDesk stays
in trusted local mode and logs a startup warning. Read-only endpoints stay open
so the dashboard renders; lock those behind your reverse proxy if needed.

## 2. Credential hygiene
NoorDesk has no user accounts or password-reset flow, so there are no reset
links to expire. The equivalent control is **token rotation**: the operator
token is a single shared secret held in an env var / secret manager, never in
git. Rotate it by generating a new value and restarting — the old token is
invalid immediately (single active secret).

## 3. Input validation
- All request bodies are Pydantic models with explicit **length caps**.
- `/api/run` resolves the inbox folder through `safe_inbox_path()`, which blocks
  path traversal (`../`, absolute paths) and refuses anything outside
  `NOORDESK_DATA_ROOT`.
- SQL uses **parameterised queries only** (see `storage.py`) — no string
  interpolation, so SQL injection is not possible.
- The dashboard renders message text with `textContent`, so hostile message
  bodies cannot execute as HTML/JS (XSS-safe).

## 4. CORS
`Access-Control-Allow-Origin` is restricted to `NOORDESK_ORIGINS`
(default `localhost`/`127.0.0.1`), not `*`. Methods are limited to GET/POST.

## 5. Rate limiting
A per-IP sliding-window limiter caps requests: 120/min by default, and a strict
12/min on the expensive/abusable endpoints (`/api/run`, `/api/ingest`,
`/api/clear`). Tune with `NOORDESK_RATE` and `NOORDESK_RATE_STRICT`.
Behind a proxy, the client IP is read from `X-Forwarded-For`.

## 6. Error handling
Custom exception handlers return structured JSON (`{"error": "..."}`) and a
clean status code. Stack traces and internals are logged **server-side only**
and never sent to the client.

## 7. Database performance
Targeted indexes back the dashboard's hot paths: a composite index for the main
list ordering (`needs_review, priority, created_at`), plus `status` and
`sender`. The message id is the primary key. We deliberately do **not** index
every column — extra indexes slow writes for no read benefit.

## 8. Logging & monitoring
Structured (JSON-line) request logs record path, status and latency.
`GET /healthz` is a liveness/readiness probe that also confirms storage is
reachable — wire it into your uptime monitor.

## 9. Rollback
See `DEPLOY.md` for the blue-green deploy + rollback procedure.
