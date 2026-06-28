# Maker Splat — MVP Candidate

This release implements the eight MVP areas needed for a credible first public build:

1. Real reconstruction pipeline
2. Dependency installation/checking
3. Guided capture workflow
4. Robust job handling
5. Built-in viewer
6. Simple export
7. Plain-language error reporting
8. Cross-platform packaging scaffolds

## Important status

This is an **MVP candidate**, not a guaranteed production `.splat` generator on every machine.

The app now has the operational structure needed to produce and verify real splats, but actual `.splat` output still depends on a working Nerfstudio/COLMAP/CUDA environment and real test validation.

## Quick start

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

## First verified splat run

Add 40–80 photos to:

```text
datasets/first-splat/images/
```

Then run:

```bash
./qa/run-real-mode-dataset.sh datasets/first-splat
```

## MVP checks

```bash
./qa/mvp-check.sh
```

## Packaging

Packaging scaffolds are in:

```text
packaging/
  macos/
  windows/
  linux/
```

They are starter scripts/specs, not signed production installers.
