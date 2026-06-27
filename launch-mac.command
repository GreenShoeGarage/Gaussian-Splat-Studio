#!/bin/bash
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not on PATH."
  echo "Install Docker Desktop, then run this again."
  exit 1
fi
docker compose up --build
