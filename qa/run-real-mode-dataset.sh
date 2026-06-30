#!/bin/bash
set -e
DATASET="$1"
if [ -z "$DATASET" ]; then
  echo "Usage: ./qa/run-real-mode-dataset.sh datasets/first-splat"
  exit 2
fi
if [ ! -d "$DATASET/images" ]; then
  echo "Dataset must contain an images/ folder: $DATASET/images"
  exit 2
fi
PROJECT_ID="real-mode-$(date +%Y%m%d-%H%M%S)"
PROJECT_DIR="backend/projects/$PROJECT_ID"
mkdir -p "$PROJECT_DIR"

echo "Maker Splat v4.1 Real Mode Dataset Run"
echo "Dataset: $DATASET"
echo "Project: $PROJECT_DIR"

export MAKER_SPLAT_ENGINE=nerfstudio
export MAKER_SPLAT_REAL_MODE=1
export MAKER_SPLAT_PRESET=${MAKER_SPLAT_PRESET:-fast}

python3 scripts/run_real_mode_dataset.py "$DATASET" "$PROJECT_DIR" || RESULT=$?
RESULT=${RESULT:-0}

echo ""
echo "Artifacts:"
find "$PROJECT_DIR" -maxdepth 4 -type f \( -name "*.splat" -o -name "*.ply" -o -name "*.md" -o -name "*.json" \) -print || true

if [ "$RESULT" = "0" ]; then
  echo "SUCCESS: verified real .splat produced."
else
  echo "NOT VERIFIED: inspect reports in $PROJECT_DIR"
fi
exit "$RESULT"
