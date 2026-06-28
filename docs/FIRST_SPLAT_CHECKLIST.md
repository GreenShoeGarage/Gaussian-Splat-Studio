# First Real Splat Checklist

Use this checklist to get Maker Splat's first verified real `.splat` output.

## 1. Confirm tools inside the backend environment

```bash
ffmpeg -version
colmap -h
ns-process-data --help
ns-train --help
ns-export --help
nvidia-smi
```

## 2. Use a controlled capture

Recommended first subject:

- shoe
- mug with printed design
- toy
- matte statue

Avoid:

- glass
- mirrors
- black glossy objects
- chrome
- transparent plastic

## 3. Use photos first

Use 40–80 JPG photos.

Do not use video for the first validation because video adds frame extraction variables.

## 4. Use Nerfstudio Engine

In Maker Splat:

```text
Engines → Nerfstudio Engine → Use this engine
```

Then:

```text
Create Project → Add Capture → Check Capture → Create 3D Scene
```

## 5. Inspect outputs

After generation, download:

```text
Diagnostics
Real Mode Report
Pipeline State
```

Expected files:

```text
scene.splat
scene.ply
REAL_MODE_REPORT.md
pipeline_state.json
diagnostics.json
log.txt
```

## 6. If no `.splat` exists

Check the Real Mode Report:

- Did `ns-process-data` complete?
- Was `transforms.json` found?
- Did `ns-train` complete?
- Was `config.yml` found?
- Which export strategy succeeded?
- Did Nerfstudio create `.ply` only?
- Did the PLY-to-SPLAT fallback run?

## 7. Patch based on the first real failure

Do not add new features until one controlled capture produces a real `.splat`.
