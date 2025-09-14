#!/usr/bin/env bash
set -euo pipefail
IN="${1:-}"
if [[ -z "$IN" ]]; then
  echo "Usage: infra/scripts/restore.sh backups/<timestamp>"
  exit 1
fi
echo "[*] Importing from $IN"
docker compose -f infra/docker/compose.edge.yml run --rm n8n-main n8n import:credentials --input="/home/node/$IN"
docker compose -f infra/docker/compose.edge.yml run --rm n8n-main n8n import:workflow --input="/home/node/$IN"
