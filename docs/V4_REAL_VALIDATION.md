# v4.0 Real Output Validation

v4.0 introduces validation as a first-class concept.

Previous releases could run commands and search for artifacts. v4.0 asks a stricter question:

> Did Maker Splat produce files that look like usable real outputs?

## Validation files

After a real run, inspect:

```text
VALIDATION_REPORT.md
validation_manifest.json
REAL_MODE_REPORT.md
pipeline_state.json
diagnostics.json
log.txt
```

## Validation categories

### scene.splat

Maker Splat checks:

- file exists
- file is not empty
- file is larger than a tiny placeholder
- binary content is present
- file is not obvious HTML/text error output

This is not a complete format validator, but it catches common false positives.

### scene.ply

Maker Splat checks:

- file exists
- PLY header exists
- vertex declaration exists
- file size is plausible

### Pipeline

Maker Splat checks:

- `ns-process-data` stage completed
- `ns-train` stage completed
- export stage attempted
- export artifacts were discovered

## What counts as success?

A project is considered **real splat verified** only when:

```text
scene.splat exists
scene.splat passes sanity checks
```

A project with only `scene.ply` is useful, but it is not a verified `.splat` success.

## Why validation matters

Without validation, software can accidentally report success when it merely created logs or copied an unrelated file.

Maker Splat should never pretend a real splat exists when it does not.
