# Maker Splat

**Maker Splat** is a local-first browser app for turning phone captures into 3D Gaussian splat projects.

This repository is the consolidated **v1.0.0 MVP Candidate**.

## Current MVP Status

Maker Splat includes:

- browser GUI
- project workflow
- Capture Coach
- Demo Engine
- Nerfstudio Engine integration layer
- real-mode diagnostics
- dependency doctor
- failure classification
- validation reports
- built-in viewer
- export bundles
- phone upload
- documentation suite

The remaining blocker for MVP confidence is repeated validation of real `.splat` output on a known-good Nerfstudio/CUDA environment.

## Quick Start

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

## Real Mode

```bash
MAKER_SPLAT_ENGINE=nerfstudio MAKER_SPLAT_REAL_MODE=1 docker compose up --build
```

## First Verified Splat Run

Place 40–80 photos in:

```text
datasets/first-splat/images/
```

Run:

```bash
./qa/run-real-mode-dataset.sh datasets/first-splat
```

Success requires:

```json
"real_splat_verified": true
```

inside `validation_manifest.json`.

## Documentation

Start here:

- [Documentation Index](docs/README.md)
- [Quick Start](docs/QUICK_START.md)
- [Installation](docs/INSTALLATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [Capture Guide](docs/CAPTURE_GUIDE.md)
- [Real Mode](docs/REAL_MODE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)

## Project Structure

```text
backend/       FastAPI backend
frontend/      React/Vite frontend
docs/          full Markdown documentation suite
qa/            validation and test scripts
datasets/      test dataset folders
packaging/     installer scaffolds
scripts/       command-line helpers
```

## License

MIT
