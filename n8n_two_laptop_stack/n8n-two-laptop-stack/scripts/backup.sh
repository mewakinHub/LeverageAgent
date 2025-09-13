#!/usr/bin/env bash
set -euo pipefail
OUT="backups/$(date +%F_%H%M)"
mkdir -p "$OUT"
# Run a temporary n8n container that talks directly to your DB using .env
docker run --rm --env-file ./.env -v "$PWD/$OUT":/out ${N8N_IMAGE:-docker.n8n.io/n8nio/n8n:latest} \
  n8n export:workflow --backup --output=/out
docker run --rm --env-file ./.env -v "$PWD/$OUT":/out ${N8N_IMAGE:-docker.n8n.io/n8nio/n8n:latest} \
  n8n export:credentials --backup --output=/out
echo "Backup written to $OUT"
