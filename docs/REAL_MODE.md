# Real Mode

Real Mode attempts to produce real Gaussian splats through Nerfstudio/COLMAP.

## Required commands

```bash
ffmpeg
colmap
ns-process-data
ns-train
ns-export
```

## Run Real Mode

```bash
MAKER_SPLAT_ENGINE=nerfstudio MAKER_SPLAT_REAL_MODE=1 docker compose up --build
```

## Verify environment

```bash
./qa/collect-environment.sh
./qa/probe-nerfstudio.sh
```

## First real splat

Place photos in:

```text
datasets/first-splat/images/
```

Run:

```bash
./qa/run-real-mode-dataset.sh datasets/first-splat
```

## Success

Success requires:

```json
"real_splat_verified": true
```

inside `validation_manifest.json`.
