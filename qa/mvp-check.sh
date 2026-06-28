#!/bin/bash
set -e
echo "Maker Splat MVP Check"

required_files=(
  "backend/app.py"
  "backend/pipeline.py"
  "backend/engines/nerfstudio.py"
  "backend/output_validator.py"
  "backend/dependency_doctor.py"
  "backend/failure_classifier.py"
  "frontend/src/App.jsx"
  "frontend/src/Preview.jsx"
  "docker-compose.yml"
  "launch-mac.command"
  "launch-windows.bat"
  "launch-linux.sh"
  "qa/run-real-mode-dataset.sh"
)

for f in "${required_files[@]}"; do
  if [ -f "$f" ]; then
    echo "✓ $f"
  else
    echo "⚠ missing $f"
    exit 1
  fi
done

python -m py_compile backend/*.py backend/engines/*.py scripts/*.py
echo "MVP structural check passed."
