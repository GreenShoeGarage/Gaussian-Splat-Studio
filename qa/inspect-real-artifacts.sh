#!/bin/bash
set -e
PROJECT_DIR="$1"
if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: ./qa/inspect-real-artifacts.sh backend/projects/<project-id>"
  exit 1
fi

echo "Inspecting $PROJECT_DIR"
for f in scene.splat scene.ply REAL_MODE_REPORT.md pipeline_state.json diagnostics.json log.txt; do
  if [ -f "$PROJECT_DIR/$f" ]; then
    echo "✓ $f"
  else
    echo "⚠ missing $f"
  fi
done

echo ""
echo "Searching for exported artifacts..."
find "$PROJECT_DIR" -type f \( -name "*.splat" -o -name "*.ply" -o -name "config.yml" -o -name "transforms.json" \) -print
