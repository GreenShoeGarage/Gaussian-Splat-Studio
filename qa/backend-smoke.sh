#!/bin/bash
set -e
curl -fsS http://localhost:8000/api/health
curl -fsS http://localhost:8000/api/setup
curl -fsS http://localhost:8000/api/preflight/real-mode
echo "Backend smoke OK"
