#!/bin/bash
set -e
echo "Nerfstudio capability probe"
for cmd in ffmpeg colmap ns-process-data ns-train ns-export nvidia-smi; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "✓ $cmd: $(command -v "$cmd")"
  else
    echo "⚠ $cmd: missing"
  fi
done

echo ""
echo "ns-export gaussian-splat help:"
if command -v ns-export >/dev/null 2>&1; then
  ns-export gaussian-splat --help || true
fi
