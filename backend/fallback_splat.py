from pathlib import Path
from PIL import Image
import numpy as np
from plyfile import PlyData, PlyElement


def create_demo_ply(frames_dir: Path, output: Path):
    image_paths = sorted(
        p for p in frames_dir.iterdir()
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )

    xyz_chunks = []
    rgb_chunks = []

    total = max(1, len(image_paths))

    for index, path in enumerate(image_paths[:24]):
        image = Image.open(path).convert("RGB")
        image.thumbnail((480, 480))
        rgb = np.asarray(image, dtype=np.uint8)
        h, w, _ = rgb.shape

        stride = max(1, int(np.sqrt((h * w) / 60000)))
        yy, xx = np.mgrid[0:h:stride, 0:w:stride]

        x = (xx - w / 2) / max(w, 1)
        y = -(yy - h / 2) / max(h, 1)
        z = np.full_like(x, 1.0 + index * 0.035, dtype=np.float32)

        angle = (index - (total - 1) / 2) * 0.06
        x2 = x * np.cos(angle) + z * np.sin(angle)
        z2 = -x * np.sin(angle) + z * np.cos(angle)

        xyz_chunks.append(np.stack([x2, y, z2], axis=-1).reshape(-1, 3))
        rgb_chunks.append(rgb[::stride, ::stride].reshape(-1, 3))

    xyz = np.concatenate(xyz_chunks, axis=0).astype(np.float32)
    rgb = np.concatenate(rgb_chunks, axis=0).astype(np.uint8)

    n = xyz.shape[0]
    vertex = np.empty(
        n,
        dtype=[
            ("x", "f4"), ("y", "f4"), ("z", "f4"),
            ("red", "u1"), ("green", "u1"), ("blue", "u1"),
        ],
    )

    vertex["x"] = xyz[:, 0]
    vertex["y"] = xyz[:, 1]
    vertex["z"] = xyz[:, 2]
    vertex["red"] = rgb[:, 0]
    vertex["green"] = rgb[:, 1]
    vertex["blue"] = rgb[:, 2]

    PlyData([PlyElement.describe(vertex, "vertex")], text=False).write(output)
