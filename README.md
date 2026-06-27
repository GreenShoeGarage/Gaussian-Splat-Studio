# Maker Splat 3.1 Release Candidate

Maker Splat is a local browser/desktop-style maker app for generating Gaussian splats from videos or photo sets.

3.1 is a release-candidate reliability pass over 3.0.

## What changed in 3.1

- Restored the full project workflow UI around the 3.0 real-mode backend
- Added backend syntax validation notes
- Added a safer QA script that checks Python syntax before tests
- Added a frontend build sanity path
- Improved real-mode setup messaging
- Kept GPU/Nerfstudio Docker profile
- Kept Demo Mode for normal computers

## Demo mode

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

## Real GPU/Nerfstudio mode

```bash
MAKER_SPLAT_REAL_MODE=1 docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

Then open:

```text
http://localhost:5173
```

## QA

```bash
./qa/run-all.sh
```

## Real-mode expectations

Real mode requires:

- NVIDIA GPU
- NVIDIA Container Toolkit
- compatible host NVIDIA driver
- ffmpeg
- COLMAP
- Nerfstudio
- `ns-process-data`
- `ns-train`
- `ns-export`

Start with **Balanced** quality on a dataset of 30–150 overlapping images.
