#!/bin/bash
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not on PATH."
  exit 1
fi
MAKER_SPLAT_REAL_MODE=1 docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
