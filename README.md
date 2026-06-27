# Gaussian Splat Studio v5

Adds:
- real pipeline stages
- background worker abstraction
- viewer integration layer
- training configuration

Architecture:

Upload
 -> preprocess
 -> reconstruction
 -> gaussian optimization
 -> export
 -> viewer

The optimizer module is designed to be replaced with gsplat.