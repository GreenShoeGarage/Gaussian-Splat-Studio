@echo off
python -m py_compile backend\*.py
cd backend
pytest -q
cd ..\frontend
npm install
npm run build
cd ..
pause
