#!/bin/bash
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker, then run this again."
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running."
  exit 1
fi
echo "Starting Maker Splat MVP..."
docker compose up --build
