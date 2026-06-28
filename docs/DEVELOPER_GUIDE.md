# Developer Guide

## Run

```bash
docker compose up --build
```

## Test

```bash
./qa/check.sh
```

## MVP Check

```bash
./qa/mvp-check.sh
```

## Code Areas

- `backend/app.py` — API
- `backend/pipeline.py` — orchestration
- `backend/engines/` — reconstruction engines
- `frontend/src/` — UI
- `qa/` — validation scripts
- `docs/` — documentation

## Rule

Do not add features until the first verified real `.splat` is repeatable.
