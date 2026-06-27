#!/bin/bash
set -e
echo "Python syntax check"
python -m py_compile backend/*.py
echo "Backend tests"
cd backend
pytest -q
cd ..
echo "Frontend build check"
cd frontend
npm install
npm run build
cd ..
echo "Maker Splat 3.1 QA complete"
