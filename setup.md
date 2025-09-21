# setup.md — Super easy start (no advanced knowledge needed)

This guide assumes you have **Docker Desktop** installed. If not, install it first (Mac/Windows/Linux).

## 1) project structure
- 
```
source/
  infra/
    docker/
      compose.edge.yml   # local stack (Traefik + n8n + Postgres + Redis + MinIO + Qdrant + API)
      compose.cloud.yml  # cloud stack (later, with AWS services)
    services/
      langgraph-api/     # a tiny FastAPI you can extend (AI / logic)
    scripts/
      backup.sh          # export n8n workflows + credentials
      restore.sh         # import them back
    .env.example         # your settings template (copy to .env)
  Makefile               # easy commands (make edge / cloud / backup)
  ...
```

> Installing make on Windows (if you want Makefile workflow)
- Scoop:
  ```
  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
  iwr -useb get.scoop.sh | iex
  scoop install make
  ```
- or Chocolatey:
  ```
  choco install make
  ```
- or use WSL (install Ubuntu and use make there).

## 2) Create your settings file
We use a simple **.env** file to tell services how to connect.

```bash
cd source/infra
cp .env.example .env

# generate a secret key ONCE and paste it in .env for N8N_ENCRYPTION_KEY

# Mac/Linux: 
openssl rand -hex 32

# Window:Windows PowerShell (no Python/OpenSSL)
-join ((1..32 | ForEach-Object { '{0:x2}' -f (Get-Random -Max 256) }))

# Any OS (Python present):
python - << 'PY'
import secrets; print(secrets.token_hex(32))
PY
```

> Tip: Don’t share `.env` publicly. (using .gitignore)

## 3) Start everything (local)
From the repo root:
```bash
cd ..   # go back to /source if you are still in infra/
make edge

# or at the project root as `make -C source edge`
```
> Compose file Creates a private Docker network called proxy and a few volumes to persist data:
- Starts Postgres (data volume), Redis, MinIO (file storage), Qdrant (vectors).
- Start n8n-main (the web UI) and n8n-worker (does background jobs).
- Traefik (traffic router) on port 80 → so `http://*.localhost` goes to the right app.
  - proxy.localhost → Traefik dashboard
- Starts your LangGraph API sample `(api.localhost/health)`

> Wait until Docker finishes pulling images. Then open these in your browser:
- **n8n editor:** http://n8n.localhost  
- **API health:** http://api.localhost/health  
- **MinIO console(S3-like file storage):** http://minio.localhost  
- **Qdrant REST(vector DB):** http://qdrant.localhost

If n8n asks to create an account, do it once.

## 4) Your first workflow (2 minutes)
In n8n:
1. “New” → choose **Manual Trigger**.
2. Add a node: **HTTP Request** → URL: `http://api.localhost/health` → GET.
3. Add a node: **Function** → set it to read the JSON and pick a field, e.g. `bucket`.
4. “Execute Workflow”. You should see results from the API.
5. Click **Activate** to let it run on schedule/webhook later.

## 5) Stopping and starting again
- Stop cleanly(but keep data): `docker compose -f infra/docker/compose.edge.yml down` (or `make edge-down`).
- Reset everything (deletes volumes/data): `docker compose down -v`
- Start: `make edge` again.
- Your data is kept in Docker volumes (Postgres/MinIO/Qdrant).
```bash
make logs      # follow logs (Ctrl+C to stop viewing)
make ps        # list running services in the stack
```

## 6) Backups (recommended)
Export your n8n stuff (workflows + credentials) into the `backups/` folder:
```bash
make backup
# commit backups/ to Git if you want history
```
Restore later:
```bash
make restore IN=backups/<timestamp>
```

## 7) Use light laptop (optional, later)
- Keep the heavy laptop running `make edge` (MAIN).
- On the light laptop, you can run **workers** that connect to the same Postgres/Redis (VPN or tunnel needed). This is optional—skip until you need it.

## 8) Move to cloud (later, when ready)
- Create: **RDS (Postgres)**, **ElastiCache (Redis)**, **S3 bucket** (or alternatives).  
- Put those values into `infra/.env`.  
- On your cloud VM (EC2), run: `make cloud`.  
- Point your domain to the VM. Done.

---

## FigJam: paste‑ready architecture text
Copy from **figjam_architecture.txt** (in this folder). It contains the high‑level and low‑level blocks.

---

## Common problems (FAQ)
**Can’t open http://n8n.localhost**  
- Make sure Docker Desktop is running.  
- Wait for images to finish downloading.  
- If port 80 is busy, stop other local web servers (Traefik uses 80).

**n8n lost credentials**  
- Use the **same `N8N_ENCRYPTION_KEY`** and the same Postgres volume. If you change the key, old creds can’t be decrypted.

**Two n8n mains running**  
- Only run one MAIN at a time. Otherwise timers/webhooks collide.

**Webhooks from the internet**  
- Not needed locally. When you need it, add **Cloudflare Tunnel** (later).

**Where do my files live?**  
- In Docker volumes (Postgres, MinIO, Qdrant). They persist across restarts.

**Is LangGraph required?**  
- No. You can keep everything in n8n. Add Python endpoints only when the flow needs “brainy”/custom logic.

**How do I change service versions?**  
- Edit image tags in the compose files and `make edge` again.

**How do I reset everything?**  
- Stop the stack, then remove volumes via Docker Desktop **(warning: deletes data)**.

---

## Cheat sheet
```bash
make edge        # start local stack
make edge-down   # stop local stack
make logs        # follow logs
make ps          # list services
make backup      # export n8n workflows & credentials
make restore IN=backups/<timestamp>
```

You’re done — build your workflows, then grow as needed. Keep it simple.
