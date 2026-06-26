from pathlib import Path
from initializer import initialize_gaussians


def train_scene(image):

    # Stage 1:
    # image -> depth -> initial gaussian cloud

    cloud = initialize_gaussians(image)

    # Stage 2 production replacement:
    #
    # gsplat optimizer:
    # optimize positions
    # optimize covariance
    # optimize SH coefficients
    # optimize opacity
    #
    # cloud = optimize(cloud)

    output = Path("jobs/gaussian_scene.ply")

    cloud.write(output)

    return output