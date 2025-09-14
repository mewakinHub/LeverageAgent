#!/usr/bin/env bash
set -euo pipefail
TS=$(date +%F_%H%M)
OUT="backups/${TS}"
mkdir -p "$OUT"
docker run --rm --env-file ./.env -v "$PWD/$OUT":/out docker.n8n.io/n8nio/n8n:latest n8n export:workflow --backup --output=/out
docker run --rm --env-file ./.env -v "$PWD/$OUT":/out docker.n8n.io/n8nio/n8n:latest n8n export:credentials --backup --output=/out
echo "Backed up to $OUT"
