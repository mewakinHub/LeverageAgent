#!/usr/bin/env bash
set -euo pipefail
TS=$(date +%F_%H%M%S)
OUT="backups/$TS"
mkdir -p "$OUT"
echo "[*] Exporting workflows and credentials to $OUT"
docker compose -f infra/docker/compose.edge.yml run --rm n8n-main n8n export:workflow --backup --output=/home/node/$TS || true
docker compose -f infra/docker/compose.edge.yml run --rm n8n-main n8n export:credentials --backup --output=/home/node/$TS || true
echo "[*] Done. Commit backups/ to Git if desired."
