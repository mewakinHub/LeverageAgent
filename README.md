# LeverageAgent — Edge→Cloud Orchestration Stack (n8n + LangGraph + Traefik)

Run today on laptops. Lift-and-shift to AWS later with the same Docker setup.

## Should we add a remote tunnel?
- **If you only run locally on the same network:** not necessary.
- **If you want webhooks / remote workers anywhere:** add a tunnel (Cloudflare Tunnel is simple). It gives you a public HTTPS domain without opening inbound ports. You can add it later at any time.

## What’s inside
- **n8n (queue mode)** — one MAIN + any number of WORKERs.
- **LangGraph/LLM API** — FastAPI skeleton you can extend as SaaS services.
- **Postgres, Redis, MinIO, Qdrant** — externalized state, cache, objects, vectors.
- **Traefik** — single entrypoint and per‑service routing: `n8n.localhost`, `api.localhost`, `minio.localhost`, `qdrant.localhost`.
- **Backups** — n8n CLI export/import scripts.
- **Makefile** — easy commands for edge (local) and cloud.

## Two‑laptop usage
- Heavy laptop: run **MAIN** + infra 24/7 (`make edge`).
- Light laptop: run only **WORKER(s)** pointing to the same Postgres/Redis (use the `compose.cloud.yml` style pointing to managed or heavy‑laptop endpoints). **Never run two MAINs at once.**

## Quick start (Edge / Local)
```bash
cd infra
cp .env.example .env
# Generate once; reuse forever
openssl rand -hex 32  # paste into N8N_ENCRYPTION_KEY
cd ..
make edge
# UIs
# http://n8n.localhost     (n8n editor)
# http://api.localhost/health
# http://minio.localhost   (console)
# http://qdrant.localhost  (REST)
```

Backups:
```bash
make backup
# commit backups/ to Git if you want versioning
make restore IN=backups/<timestamp>
```

## Cloud (AWS) path
- **EC2 + Compose:** quickest. Create RDS (Postgres), ElastiCache (Redis), S3 bucket. Set envs in `infra/.env`. `make cloud` on the instance.
- **ECS (Fargate):** push your images to ECR; run one `n8n-main` service + N workers; point to RDS/ElastiCache; put ALB/Cloudflare in front of Traefik.

## Design notes
- **Queue mode** distributes work via Redis, with one MAIN scheduling timers/webhooks. Workers can run anywhere with DB/Redis access.
- **External storage** means your workflows, creds, objects, and vectors survive container restarts and are portable.
- **Traefik** keeps ports tidy and enables host‑based routing locally and in cloud.
- **Portability**: same Compose files adapt to cloud by swapping envs.

## Next steps
- Replace `YOURUSER` in `Makefile` with your Docker Hub user (or ECR).
- Add a Cloudflare Tunnel when you need public HTTPS for webhooks.
- Extend `infra/services/langgraph-api/app/main.py` with your endpoints.
