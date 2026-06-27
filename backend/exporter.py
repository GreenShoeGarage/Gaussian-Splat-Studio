import numpy as np


def export_ply(scene,path):

    # Replace with real Gaussian PLY writer

    np.save(
        str(path)+".data.npy",
        scene.data["image"]
    )