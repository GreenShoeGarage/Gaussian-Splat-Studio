# Roadmap

## Immediate MVP Goal

Produce one verified real `scene.splat` from a known-good dataset.

Success means:

- a dataset in `datasets/first-splat/images/`
- Real Mode run completes
- `scene.splat` exists
- `validation_manifest.json` reports `real_splat_verified: true`

## Near Term

- Pin tested Nerfstudio/COLMAP/CUDA versions
- Validate the viewer with real splats
- Improve Docker GPU image
- Add integration test dataset
- Harden crash recovery

## Later

- Native installers
- Better live capture guidance
- Background masking
- Plugin architecture
- Additional reconstruction engines
- More export formats
