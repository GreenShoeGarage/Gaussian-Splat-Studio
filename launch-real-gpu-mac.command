#!/bin/bash
cd "$(dirname "$0")"
if [ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
  export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker command not found."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running."
  exit 1
fi
MAKER_SPLAT_REAL_MODE=1 MAKER_SPLAT_ENGINE=nerfstudio docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
