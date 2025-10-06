# LeverageAgent — Simple Edge→Cloud Automation Stack
> PURPOSE: For prototyping and private use, not product
> **Goal:** Run everything on your **heavy laptop** today, and move to **cloud** later without changing how you work. Keep things simple.

**Start here →** See **[setup.md](./setup.md)** for a super-easy, step‑by‑step guide.

## What’s inside (plain English)
- **n8n (the conductor):** main orchestrator for each workflow
- **LangGraph / LangChain API (the worker):** microservices

- **Postgres (memory):** Remembers n8n workflows and history.
- **Redis (queue):** Helps share work between machines/workers.
- **MinIO / S3 (files):** Stores big files (videos, exports, etc.).
- **Qdrant (vectors):** Optional database for embeddings/semantic search.
- **Traefik (traffic manager):** Lets you open sites like `n8n.localhost`, `api.localhost`, `minio.localhost` easily.

## Two levels of “orchestrators” (why there are two)
- **Level 1 – n8n:** button clicks, timers, webhooks, call APIs, pass data between steps.
- **Level 2 – LangGraph/Chain code:** when a step needs “thinking” or custom logic, the API does it, then returns results to n8n.

This keeps your logic clean: *n8n for flow*, *Python for brains*.

## How it runs (local → cloud)
- **Local (edge):** one command starts *all services* with Docker. Your data lives in volumes; it survives restarts.
- **Cloud later:** same Docker files, just point environment variables to managed services (RDS, ElastiCache, S3). No code rewrite.
  - **EC2 + Compose:** quickest. Create RDS (Postgres), ElastiCache (Redis), S3 bucket. Set envs in `infra/.env`. `make cloud` on the instance.
  - **ECS (Fargate):** push your images to ECR; run one `n8n-main` service + N workers; point to RDS/ElastiCache; put ALB/Cloudflare in front of Traefik.

## Two-laptop mode (your use case)
- Heavy laptop: run make edge (starts MAIN + infra).
- Light laptop: you have two choices:
  1. Worker-only against heavy laptop (best): point env to the heavy laptop’s Postgres/Redis over VPN or tunnel and run a compose that only starts n8n-worker.
  2. Emergency MAIN on light: only do this if the heavy MAIN is off (queue mode needs one MAIN). 

## What you can build with this
- Auto content repurpose (upload → transcribe → cut → caption → export).
- Ads analyst (pull metrics → detect winners → recommend actions).
- Lead scoring + qualification (enrich → score → schedule calls).

## File map (what to look for)
```
infra/
  docker/
    compose.edge.yml   # run locally on your laptop
    compose.cloud.yml  # run in the cloud later
  services/
    langgraph-api/     # your Python API (edit here)
  scripts/
    backup.sh          # n8n export (workflows + credentials)
    restore.sh         # n8n import
  .env.example         # copy to .env and fill values
Makefile               # quick commands: make edge / cloud / backup
workflows/             # keep JSON exports here (version control)
```

## FigJam architecture (paste-friendly text)
See **figjam_architecture.txt** in this folder. Paste it into FigJam as sticky notes/tables to draw your diagram fast.

## Next steps
1) Follow **[setup.md](./setup.md)** to get everything running.
2) Build your first workflow in n8n (simple demo included in setup).
3) Add your own API endpoints to `infra/services/langgraph-api/app/main.py`.
4) When you need 24/7, migrate DB/queue/file storage to the cloud and use `compose.cloud.yml`.

---

## FAQ (quick)
**Q: Do I need a public domain/tunnel now?**  
A: No, not for local experiments. Add Cloudflare Tunnel when you need public webhooks or remote access.

**Q: Can both laptops be used?**  
A: Yes. Run “MAIN” on the heavy laptop. The light laptop can run workers pointing to the same DB/Redis. Don’t run two MAINs at once.

**Q: Will I lose my n8n credentials after restart?**  
A: No, as long as you keep the same **N8N_ENCRYPTION_KEY** and the Postgres volume. Backups: use `make backup`.

Q: volume, cache, bind mouth use case??