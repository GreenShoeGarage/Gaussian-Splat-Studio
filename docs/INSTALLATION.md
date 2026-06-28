# Installation

## Recommended: Docker

Install Docker Desktop, then run:

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

## macOS

```bash
./launch-mac.command
```

## Windows

```bat
launch-windows.bat
```

## Linux

```bash
./launch-linux.sh
```

## Real Mode Requirements

Real Mode requires:

- FFmpeg
- COLMAP
- Nerfstudio
- `ns-process-data`
- `ns-train`
- `ns-export`
- NVIDIA GPU and CUDA strongly recommended

Run:

```bash
./qa/collect-environment.sh
./qa/probe-nerfstudio.sh
```

## Common Setup Problems

### Docker not running

Open Docker Desktop and wait for it to finish starting.

### Real Mode tools missing

Use Demo Engine or install the missing tools in the backend environment.

### GPU unavailable

Check `nvidia-smi` inside the environment where Maker Splat runs.
