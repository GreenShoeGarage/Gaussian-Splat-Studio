from PIL import Image
import numpy as np


def preprocess(path):

    image = Image.open(path).convert("RGB")

    return {
        "image": np.array(image),
        "camera": None,
        "depth": None
    }