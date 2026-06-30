#!/bin/bash
set -e
echo "Maker Splat Real Mode preflight"
echo "Checking common commands..."
for cmd in ffmpeg colmap ns-process-data ns-train ns-export; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "✓ $cmd: $(command -v "$cmd")"
  else
    echo "⚠ $cmd: not found"
  fi
done
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "✓ nvidia-smi available"
  nvidia-smi || true
else
  echo "⚠ nvidia-smi not found"
fi
echo "Done."
