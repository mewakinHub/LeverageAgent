#!/usr/bin/env bash
set -euo pipefail
IN="${1:-}"
if [[ -z "$IN" ]]; then
  echo "usage: ./scripts/restore.sh backups/<timestamp>"
  exit 1
fi
docker run --rm --env-file ./.env -v "$PWD/$IN":/in docker.n8n.io/n8nio/n8n:latest n8n import:credentials --input=/in
docker run --rm --env-file ./.env -v "$PWD/$IN":/in docker.n8n.io/n8nio/n8n:latest n8n import:workflow --input=/in
