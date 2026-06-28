#!/bin/bash
set -e
PROJECT_DIR="$1"
if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: ./qa/validate-project-output.sh backend/projects/<project-id>"
  exit 1
fi

echo "Validating Maker Splat output: $PROJECT_DIR"

check_file() {
  if [ -f "$PROJECT_DIR/$1" ]; then
    echo "✓ $1 ($(wc -c < "$PROJECT_DIR/$1") bytes)"
  else
    echo "⚠ missing $1"
  fi
}

check_file scene.splat
check_file scene.ply
check_file VALIDATION_REPORT.md
check_file validation_manifest.json
check_file REAL_MODE_REPORT.md
check_file pipeline_state.json
check_file diagnostics.json
check_file log.txt

if [ -f "$PROJECT_DIR/scene.splat" ]; then
  size=$(wc -c < "$PROJECT_DIR/scene.splat")
  if [ "$size" -lt 1024 ]; then
    echo "⚠ scene.splat is suspiciously small"
    exit 2
  else
    echo "✓ scene.splat size looks plausible"
  fi
else
  echo "⚠ no scene.splat to validate"
  exit 3
fi
