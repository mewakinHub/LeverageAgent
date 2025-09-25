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

## 3) Start everything (local on wsl)
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
- **API health:** http://api.localhost/health  
- **MinIO console(S3-like file storage):** http://minio.localhost  
- **Qdrant REST(vector DB):** http://qdrant.localhost

- **n8n editor(port 5679, bypassing Traefik):** 
  - http://n8n.localhost (unable to use, due to no `N8N_SECURE_COOKIE=false`)
  - http://localhost:5678 (only on the light laptop itself)
  - http://<light-laptop-IP>:5678 if you exposed port 5678 in compose.edge.yml (same-Wi-Fi)
    - `ipconfig` to get ip addr

If n8n asks to create an account, do it once.

## 4) Your first workflow (2 minutes)
In n8n:
1. “New” → choose **Manual Trigger**.
2. Add a node: **HTTP Request** → URL: `http://api.localhost/health` → GET.
3. Add a node: **Function** → set it to read the JSON and pick a field, e.g. `bucket`.
4. “Execute Workflow”. You should see results from the API.
5. Click **Activate** to let it run on schedule/webhook later.

## 5) Stopping and starting again
- Stop cleanly(but keep data): `docker compose -f infra/docker/compose.edge.yml --env-file infra/.env down` (or `make edge-down`).
- Reset everything (deletes volumes/data): `docker compose -f infra/docker/compose.edge.yml --env-file infra/.env down -v`
  - docker volume rm leverage-edge_pg_data
- Start: `make edge` again. (no need to down though, it already rebuilds only what change)
- Your data is kept in Docker volumes (Postgres/MinIO/Qdrant).
- no need to use build-api cuz we already build it in compose
  ```bash
  make build-api
  make push-api
  ```

## 6) Backups (recommended)
Export your n8n stuff (workflows + credentials) into the `backups/` folder(JSON file on disk) for:
- Spinning up a new device and importing your logic/creds
  - New device from Git = different containers/volumes (new empty volumes)
- Versioning your workflows over time instead of git(code-based).
**Note**: credentials export is encrypted with your N8N_ENCRYPTION_KEY. You must use the same key on the new device to import successfully.
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

## Do you *need* Postgres & Redis?

* **Postgres** – stores n8n’s **workflows, users, credentials (encrypted), run history, settings**.

  * **Yes, you need a database.** In our stack we use **Postgres**. (n8n can also use SQLite for tiny demos, but Postgres is safer and ready for growth.)
* **Redis** – only needed when you use **Queue Mode** (the mode our compose uses). It’s the **job queue** that lets n8n scale with **workers** (parallel jobs, multi-machine later).

  * If you stick to **one process** (no workers), you can run n8n in **Regular Mode** and **skip Redis**.

---

## What about MinIO, Qdrant, and the LangGraph API?

You only start these when your use case needs them:

| Service                           | What it does                                                 | Do you need it now?                                     | Typical use cases                                                           |
| --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------- | --------------------------------------------------------------------------- |
| **MinIO** (S3-compatible storage) | Stores **big files** (videos, zips, datasets) outside the DB | **No**, unless you’re saving large files                | Content repurposing pipelines, exporting zips/CSVs, media storage           |
| **Qdrant** (vector DB)            | **Embeddings / semantic search** for RAG                     | **No**, unless you’re doing retrieval/semantic features | “Find similar content,” knowledge base Q\&A, dedupe by meaning              |
| **LangGraph API** (FastAPI)       | Your **Python/AI code** running as a small web service       | **No**, if n8n nodes are enough for now                 | Custom AI logic, heavy processing, calling local models, special algorithms |

> TL;DR: you can stay very light: **Postgres + n8n** (and optionally **Redis** if you want queue/parallel workers). Turn on MinIO/Qdrant/LangGraph only when your features require them.
