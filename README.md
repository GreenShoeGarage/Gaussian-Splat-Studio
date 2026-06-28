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

GNU GPLv3

<img width="1438" height="796" alt="Screenshot 2026-06-28 at 6 50 49 AM" src="https://github.com/user-attachments/assets/288d972b-a51e-4122-bc16-27bacb1615e4" />

<img width="1443" height="786" alt="Screenshot 2026-06-28 at 6 51 07 AM" src="https://github.com/user-attachments/assets/305e299d-c1ba-4277-a85d-6949b082d502" />

<img width="1450" height="786" alt="Screenshot 2026-06-28 at 6 51 17 AM" src="https://github.com/user-attachments/assets/f5a61431-0dfe-4e55-aec8-5245f9ee0edd" />

<img width="1447" height="794" alt="Screenshot 2026-06-28 at 6 51 31 AM" src="https://github.com/user-attachments/assets/5d359b2b-4f51-4e79-bf6d-47fcef7dc1a9" />

<img width="1448" height="794" alt="Screenshot 2026-06-28 at 6 51 40 AM" src="https://github.com/user-attachments/assets/b1c045c2-b1d2-4d47-8a50-08408e1fe783" />


