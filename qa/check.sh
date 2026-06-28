#!/bin/bash
set -e
echo "Maker Splat MVP Candidate"
python -m py_compile backend/*.py backend/engines/*.py scripts/*.py
./qa/mvp-check.sh
cd backend
pytest -q
cd ../frontend
npm install
npm run build
cd ..
echo "All checks passed."
