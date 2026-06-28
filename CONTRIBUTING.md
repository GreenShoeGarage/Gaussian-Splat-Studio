# Contributing

Thanks for helping improve Maker Splat.

## Project Priorities

Before adding new features, help us make the core MVP reliable:

1. Produce verified real `.splat` output.
2. Improve Real Mode setup.
3. Improve diagnostics.
4. Improve documentation.
5. Improve packaging.

## Development Setup

```bash
docker compose up --build
```

Run checks:

```bash
./qa/check.sh
```

Run MVP structural checks:

```bash
./qa/mvp-check.sh
```

## Pull Requests

A good pull request should include:

- clear description
- linked issue if applicable
- tests or validation notes
- documentation updates when behavior changes

## Code Style

Prefer readable, obvious code over clever code.

User-facing language should be plain English.
