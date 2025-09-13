# n8n Two‑Laptop Stack (Docker + shared Postgres/Redis)

Goal: Run n8n 24/7 on a **heavy laptop** but be able to hop onto a **light laptop** anywhere and keep working with the exact same workflows, credentials, and run history.

## Architecture (recommended)
- **External Postgres** stores workflows/credentials/history (shared by both laptops).  
- **External Redis** provides the queue for workers.  
- Heavy laptop runs **main + workers** (24/7).  
- Light laptop runs **worker** only (default) and can optionally run **main** if the heavy laptop is OFF.

> Why this? No data sync drama, no DB files in Git. Both machines point to the same DB/Redis, so “progress” is always in one place.

### Docs referenced
- Queue mode & multi‑instance: https://docs.n8n.io/hosting/scaling/queue-mode/
- Docker & Compose: https://docs.n8n.io/hosting/installation/docker/ and /server-setups/docker-compose/
- DB/Redis env vars: https://docs.n8n.io/hosting/configuration/environment-variables/
- Webhook URL config: https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/
- CLI export/import: https://docs.n8n.io/hosting/cli-commands/

## Setup
1) **Create Postgres + Redis** (managed services or self-host). Enable TLS if available.  
2) `cp .env.example .env` and fill in all values. Generate once:
   ```bash
   ./scripts/generate_key.sh  # paste into N8N_ENCRYPTION_KEY
   ```
3) On the **heavy laptop**:
   ```bash
   docker compose -f compose.heavy.yml up -d
   ```
   - Main UI: `https://$N8N_HOST` (use reverse proxy or Cloudflare Tunnel for public access)
   - Queue workers auto‑start.

4) On the **light laptop** (worker only):
   ```bash
   docker compose -f compose.light.yml --profile worker up -d
   ```

5) **Emergency** (run main on light laptop) — only if heavy main is OFF:
   ```bash
   docker compose -f compose.light.yml --profile main up -d
   ```

## Backups to Git (Community Edition)
Enterprise Source Control uses Git directly in-product. For CE, use the CLI:
```bash
./scripts/backup.sh                      # exports workflows + credentials to backups/<timestamp>/
git add backups && git commit -m "n8n backup" && git push
# On another machine:
./scripts/restore.sh backups/<timestamp>
```

## Webhooks (important)
Set `WEBHOOK_URL` to your public domain (HTTPS). If behind a proxy/tunnel, the editor may display :5678; setting `WEBHOOK_URL` fixes registration.

## Notes
- The **same N8N_ENCRYPTION_KEY** must be used on all machines. Changing it breaks access to stored credentials.
- In queue mode, **only the MAIN** schedules timers & receives webhooks; **workers** execute. Avoid starting two mains simultaneously.
- If you don’t want external DB/Redis, switch to **Option B (Git backups)** in the README and use local Postgres on each laptop + export/import when switching. This won’t be real‑time.

## Option B (no external DB)
- Run local Postgres + single n8n per laptop. Before switching machines:
  1. `./scripts/backup.sh && git push`
  2. On second laptop: `git pull && ./scripts/restore.sh backups/<timestamp>`
- Pros: no cloud DB. Cons: not live; you must export/import to sync.

## Optional: Cloudflare Tunnel
Add the `cloudflared` service in `compose.heavy.yml` and set `CLOUDFLARE_TUNNEL_TOKEN` to expose your main securely without opening ports.

## Update
```bash
docker compose -f compose.heavy.yml pull && docker compose -f compose.heavy.yml up -d
```

