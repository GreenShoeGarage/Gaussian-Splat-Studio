@echo off
cd /d %~dp0
echo.
echo Maker Splat v2.1 - Polish
echo Checking Docker...
echo.
where docker >nul 2>nul
if errorlevel 1 (
  echo Docker command not found.
  echo Open Docker Desktop, wait until it is running, then try again.
  pause
  exit /b 1
)
docker info >nul 2>nul
if errorlevel 1 (
  echo Docker is installed but not running yet.
  echo Open Docker Desktop and wait until startup finishes.
  pause
  exit /b 1
)
echo Docker is ready.
echo Starting Maker Splat...
echo Open http://localhost:5173 when the build finishes.
docker compose up --build
pause
