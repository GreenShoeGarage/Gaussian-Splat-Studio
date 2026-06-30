# Pipeline

Maker Splat's pipeline:

```text
capture/
  ↓
frames/
  ↓
dataset preparation
  ↓
camera tracking
  ↓
training
  ↓
export
  ↓
validation
```

## Demo Engine

Creates a preview PLY from image frames.

## Nerfstudio Engine

Runs:

```text
ns-process-data
ns-train splatfacto
ns-export gaussian-splat
```

## Artifacts

Common outputs:

- `scene.splat`
- `scene.ply`
- `thumbnail.jpg`
- `log.txt`
- `diagnostics.json`
- `pipeline_state.json`
- `VALIDATION_REPORT.md`
