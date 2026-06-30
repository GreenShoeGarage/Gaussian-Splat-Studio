#!/bin/bash
cd "$(dirname "$0")"

if [ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
  export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
fi

echo ""
echo "Maker Splat v2.1 — Polish"
echo "Checking Docker..."
echo ""

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker command not found."
  echo ""
  echo "Try this:"
  echo "1. Open Docker Desktop from Applications."
  echo "2. Wait until the whale icon says Docker is running."
  echo "3. Run this launcher again."
  echo ""
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running yet."
  echo "Open Docker Desktop and wait until startup finishes."
  echo ""
  exit 1
fi

echo "Docker is ready."
echo "Starting Maker Splat..."
echo "Open http://localhost:5173 when the build finishes."
echo ""
docker compose up --build
