# v4.1 Verified Real Splat Runbook

Do not add features until this command succeeds:

```bash
./qa/run-real-mode-dataset.sh datasets/first-splat
```

## Steps

1. Run `./qa/collect-environment.sh`
2. Add 40–80 known-good photos to `datasets/first-splat/images/`
3. Run `MAKER_SPLAT_PRESET=fast ./qa/run-real-mode-dataset.sh datasets/first-splat`
4. Inspect the generated project folder
5. Patch exactly one blocker
6. Repeat until `validation_manifest.json` contains `"real_splat_verified": true`

## Reports

- `VALIDATION_REPORT.md`
- `ENVIRONMENT_REPORT.md`
- `FAILURE_CLASSIFICATION.md`
- `REAL_MODE_REPORT.md`
- `pipeline_state.json`
- `log.txt`
