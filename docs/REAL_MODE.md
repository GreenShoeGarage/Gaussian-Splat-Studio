# Real Mode

Real Mode is Maker Splat's path for creating real Gaussian splats.

It uses external reconstruction tools instead of the built-in Demo Engine.

## Required tools

Real Mode expects these commands to be available in the backend environment:

```bash
ffmpeg
colmap
ns-process-data
ns-train
ns-export
```

## Recommended hardware

- NVIDIA RTX GPU
- CUDA-compatible driver
- 8 GB VRAM minimum
- 16 GB or more VRAM recommended
- 32 GB system RAM recommended

## Why these tools matter

### FFmpeg

Turns videos into still frames.

### COLMAP

Estimates camera positions from overlapping images.

### Nerfstudio

Trains and exports Gaussian splats.

## Engine selection

Maker Splat v3.0 introduces engines.

The two built-in engines are:

- Demo Engine
- Nerfstudio Engine

Demo Engine creates a previewable PLY from images and works on normal computers.

Nerfstudio Engine attempts real Gaussian splat reconstruction.

## Running Real Mode

```bash
MAKER_SPLAT_ENGINE=nerfstudio MAKER_SPLAT_REAL_MODE=1 docker compose up --build
```

## Common failures

### Nerfstudio missing

Install Nerfstudio in the backend environment.

### COLMAP missing

Install COLMAP or use a Docker image that includes it.

### CUDA unavailable

Use Demo Engine, or configure an NVIDIA CUDA environment.

### No camera positions found

Capture more overlapping images.

### Export completed but no splat found

Check Nerfstudio version and export command compatibility.
