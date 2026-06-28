# Troubleshooting

## Docker is not running

Open Docker Desktop and wait until it says Docker is running.

## Missing FFmpeg

Use Docker or install FFmpeg.

## COLMAP failed

Likely causes:

- blurry photos
- not enough overlap
- too few angles
- shiny or transparent subject

Try a known-good dataset.

## Nerfstudio failed

Check:

- `log.txt`
- `REAL_MODE_REPORT.md`
- `pipeline_state.json`
- `ENVIRONMENT_REPORT.md`

## No `.splat` produced

Possible causes:

- export command mismatch
- Nerfstudio version difference
- training failed
- only `.ply` export supported
- no external converter available

## GPU not detected

Run:

```bash
nvidia-smi
```

inside the same environment where Maker Splat runs.
