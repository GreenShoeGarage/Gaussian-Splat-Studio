# Engine Guide

Engines convert captures into 3D outputs.

## Demo Engine

Works on normal computers.

Produces:

- `scene.ply`

## Nerfstudio Engine

Requires external tools.

Attempts to produce:

- `scene.splat`
- `scene.ply`

## Engine Principles

- UI should not depend on one engine.
- Engines must produce diagnostics.
- Engines must not fake success.
- Real output must be validated.
