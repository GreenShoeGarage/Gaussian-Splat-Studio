from pathlib import Path
from preprocess import preprocess
from optimizer import train_gaussians
from exporter import export_ply


def run_pipeline(image):

    data = preprocess(image)

    trained = train_gaussians(data)

    output = Path("jobs/output.ply")

    export_ply(
        trained,
        output
    )

    return output