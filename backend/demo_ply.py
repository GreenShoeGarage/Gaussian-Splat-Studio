from pathlib import Path
from PIL import Image
import numpy as np
from plyfile import PlyData, PlyElement

def create_demo_ply(frames_dir: Path, output: Path):
    paths = sorted(p for p in frames_dir.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"})
    xyzs, rgbs = [], []
    total = max(1, len(paths))
    for i,p in enumerate(paths[:36]):
        img = Image.open(p).convert("RGB"); img.thumbnail((560,560))
        rgb = np.asarray(img, dtype=np.uint8); h,w,_ = rgb.shape
        stride = max(1, int(np.sqrt((h*w)/80000)))
        yy,xx = np.mgrid[0:h:stride, 0:w:stride]
        x = (xx-w/2)/max(w,1); y = -(yy-h/2)/max(h,1); z = np.full_like(x, 1+i*.03, dtype=np.float32)
        ang = (i-(total-1)/2)*.055
        x2 = x*np.cos(ang)+z*np.sin(ang); z2 = -x*np.sin(ang)+z*np.cos(ang)
        xyzs.append(np.stack([x2,y,z2], axis=-1).reshape(-1,3)); rgbs.append(rgb[::stride,::stride].reshape(-1,3))
    if not xyzs: raise RuntimeError("Need at least one image frame to create demo PLY.")
    xyz = np.concatenate(xyzs).astype(np.float32); rgb = np.concatenate(rgbs).astype(np.uint8)
    v = np.empty(xyz.shape[0], dtype=[("x","f4"),("y","f4"),("z","f4"),("red","u1"),("green","u1"),("blue","u1")])
    v["x"],v["y"],v["z"] = xyz[:,0],xyz[:,1],xyz[:,2]; v["red"],v["green"],v["blue"] = rgb[:,0],rgb[:,1],rgb[:,2]
    PlyData([PlyElement.describe(v, "vertex")], text=False).write(output)
