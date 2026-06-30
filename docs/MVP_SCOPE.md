# Maker Splat MVP Scope

The MVP is not every feature imagined for Maker Splat.

The MVP is the smallest release that can honestly deliver the core promise:

> A non-technical user can capture an object, generate a real 3D splat when dependencies are available, preview it, export it, and understand what happened if it fails.

## MVP Area 1 — Real Reconstruction Pipeline

Required:

- frame preparation
- Nerfstudio/COLMAP orchestration
- artifact discovery
- validation
- diagnostics

Status: implemented as a validated pipeline runner, but still requires real machine validation.

## MVP Area 2 — Dependency Installation

Required:

- dependency checks
- install guidance
- Docker-first path
- compatible tool report

Status: dependency doctor and packaging scaffolds included.

## MVP Area 3 — Guided Capture

Required:

- capture checklist
- quality check
- file count
- blur/lighting/coverage guidance

Status: capture coach and quality reports included.

## MVP Area 4 — Robust Jobs

Required:

- cancel
- recover interrupted jobs
- job state
- logs
- diagnostics

Status: job state, cancel, recovery, reports, and manifest added.

## MVP Area 5 — Built-in Viewer

Required:

- orbit
- zoom
- pan
- point size
- background
- screenshot

Status: included.

## MVP Area 6 — Simple Export

Required:

- `.splat`
- `.ply`
- ZIP package
- diagnostics bundle

Status: included.

## MVP Area 7 — Error Reporting

Required:

- classify failures
- user-facing explanations
- logs for developers

Status: included.

## MVP Area 8 — Cross-platform Packaging

Required:

- macOS launcher
- Windows launcher
- Linux launcher
- packaging docs

Status: scaffolds included.
