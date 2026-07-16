# Deploying NoorDesk (with a rollback path)

NoorDesk is a stateless FastAPI app; all state lives in the SQLite file at
`NOORDESK_DB`. That makes blue-green deployment straightforward.

## Environment
```bash
export NOORDESK_TOKEN="$(openssl rand -hex 32)"     # operator token (required in prod)
export NOORDESK_ORIGINS="https://desk.yourdomain.com"
export NOORDESK_DB="/var/lib/noordesk/noordesk.db"  # persistent volume
export NOORDESK_DATA_ROOT="/var/lib/noordesk/inbox" # allowlisted inbox root
export NOORDESK_RATE_STRICT=12
```

## Blue-green deploy
Two identical app instances point at the **same** persistent DB volume; a load
balancer sends live traffic to one at a time.

1. **Blue** is live on `:8001`. Deploy the new build to **green** on `:8002`.
2. Smoke-test green directly:
   ```bash
   curl -f http://127.0.0.1:8002/healthz
   ```
3. Flip the load balancer's upstream from blue to green.
4. Watch logs / error rate for a few minutes. Keep blue running and untouched.

## Rollback
If green misbehaves, flip the load balancer's upstream **back to blue**. No
rebuild, no restart — blue is still warm. Because both instances share one DB,
there is no data to migrate back.

> Schema changes: `storage.init_db()` is additive (it only *adds* missing
> columns and `CREATE INDEX IF NOT EXISTS`), so an old build keeps working
> against a newer DB — that is what makes instant rollback safe here. Avoid
> destructive migrations; if you must, take a DB snapshot first.

## Health & monitoring
- Liveness/readiness: `GET /healthz`
- Alert on: 5xx rate, `429` spikes (possible abuse), and `/healthz` failures.
