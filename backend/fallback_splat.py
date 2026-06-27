from pathlib import Path
from PIL import Image
import numpy as np
from plyfile import PlyData, PlyElement

def create_demo_ply(frames_dir: Path, output: Path, mode: str = "object"):
    image_paths = sorted(p for p in frames_dir.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"})
    xyz_chunks, rgb_chunks = [], []
    total = max(1, len(image_paths))
    spread = {"object":0.055,"room":0.025,"outdoor":0.035,"turntable":0.08}.get(mode,0.055)
    for index, path in enumerate(image_paths[:36]):
        image = Image.open(path).convert("RGB"); image.thumbnail((560,560))
        rgb = np.asarray(image, dtype=np.uint8); h,w,_ = rgb.shape
        stride = max(1, int(np.sqrt((h*w)/80000)))
        yy, xx = np.mgrid[0:h:stride, 0:w:stride]
        x = (xx-w/2)/max(w,1); y = -(yy-h/2)/max(h,1); z = np.full_like(x, 1.0 + index*0.03, dtype=np.float32)
        angle = (index-(total-1)/2)*spread
        x2 = x*np.cos(angle)+z*np.sin(angle); z2 = -x*np.sin(angle)+z*np.cos(angle)
        xyz_chunks.append(np.stack([x2,y,z2], axis=-1).reshape(-1,3))
        rgb_chunks.append(rgb[::stride,::stride].reshape(-1,3))
    xyz = np.concatenate(xyz_chunks).astype(np.float32); rgb = np.concatenate(rgb_chunks).astype(np.uint8)
    vertex = np.empty(xyz.shape[0], dtype=[("x","f4"),("y","f4"),("z","f4"),("red","u1"),("green","u1"),("blue","u1")])
    vertex["x"],vertex["y"],vertex["z"] = xyz[:,0],xyz[:,1],xyz[:,2]
    vertex["red"],vertex["green"],vertex["blue"] = rgb[:,0],rgb[:,1],rgb[:,2]
    PlyData([PlyElement.describe(vertex, "vertex")], text=False).write(output)
