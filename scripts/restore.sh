#!/usr/bin/env bash
set -euo pipefail
IN="${1:-}"
if [[ -z "$IN" ]]; then
  echo "Usage: scripts/restore.sh backups/2025-09-13_1200"
  exit 1
fi
docker run --rm --env-file ./.env -v "$PWD/$IN":/in ${N8N_IMAGE:-docker.n8n.io/n8nio/n8n:latest} \
  n8n import:credentials --input=/in
docker run --rm --env-file ./.env -v "$PWD/$IN":/in ${N8N_IMAGE:-docker.n8n.io/n8nio/n8n:latest} \
  n8n import:workflow --input=/in
echo "Imported from $IN"
