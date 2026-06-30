# Real Mode Testing

This document is the working checklist for turning Maker Splat's Nerfstudio Engine into a production-quality real `.splat` generator.

## Required environment

Confirm these commands work inside the backend environment:

```bash
ffmpeg -version
colmap -h
ns-process-data --help
ns-train --help
ns-export --help
nvidia-smi
```

GPU is strongly recommended.

## Test dataset

Start with a simple matte object.

Recommended:

- 40–80 photos
- good overlap
- soft lighting
- full orbit
- no reflective surfaces

Avoid videos for the first test. Photos remove one variable.

## Expected pipeline

Maker Splat should run:

```text
capture/
  photos or video
    ↓
frames/
  normalized image sequence
    ↓
outputs/nerfstudio-data/
  processed dataset
    ↓
outputs/nerfstudio-runs/
  training outputs and config.yml
    ↓
outputs/nerfstudio-export/
  exported Gaussian splat artifacts
    ↓
scene.ply / scene.splat
```

## Success criteria

A successful Real Mode run produces at least one of:

```text
scene.splat
scene.ply
```

and these files:

```text
log.txt
diagnostics.json
pipeline_state.json
REAL_MODE_REPORT.md
```

## Failure investigation

Open:

```text
log.txt
REAL_MODE_REPORT.md
diagnostics.json
pipeline_state.json
```

Check:

- which command failed
- command exit code
- stdout/stderr
- missing files
- whether a config.yml was discovered
- whether export produced `.ply` or `.splat`

## Known fragile areas

- Nerfstudio CLI flags can change by version.
- `ns-export gaussian-splat` output format may vary.
- Some installs export `.ply` but not `.splat`.
- Docker GPU passthrough varies by OS.
- COLMAP may fail on blurry or low-overlap captures.


## v3.2 Export Strategy Notes

v3.2 tries more than one Nerfstudio export command.

It records each attempt in:

```text
pipeline_state.json
```

and summarizes them in:

```text
REAL_MODE_REPORT.md
```

If Nerfstudio exports `.ply` but not `.splat`, v3.2 attempts to find an optional external converter:

```text
ply-to-splat
ply2splat
splat-transform
```

Maker Splat does **not** fake a `.splat` file. If no valid converter is available, it reports that honestly.

## Inspect artifacts

```bash
./qa/inspect-real-artifacts.sh backend/projects/<project-id>
```
