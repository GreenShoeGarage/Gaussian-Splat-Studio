#!/bin/bash
set -e
echo "Maker Splat v4.1 Environment Report"
uname -a || true
for cmd in docker ffmpeg colmap ns-process-data ns-train ns-export nvidia-smi python python3; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "✓ $cmd: $(command -v "$cmd")"
  else
    echo "⚠ $cmd: missing"
  fi
done
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi || true
fi
