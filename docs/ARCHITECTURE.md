# Architecture

Maker Splat has four main layers:

```text
Frontend → Backend API → Engine Layer → Project Storage
```

## Frontend

React/Vite browser app.

Responsibilities:

- workflow
- viewer
- progress display
- project controls

## Backend

FastAPI app.

Responsibilities:

- projects
- uploads
- jobs
- engines
- diagnostics
- exports

## Engines

Engines implement reconstruction strategies.

Built-in engines:

- Demo Engine
- Nerfstudio Engine

## Project Storage

Each project stores:

- capture files
- generated artifacts
- metadata
- logs
- reports
