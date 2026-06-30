from pathlib import Path
from .base import ReconstructionEngine
from demo_ply import create_demo_ply

class DemoEngine(ReconstructionEngine):
    id = "demo"
    name = "Demo Engine"
    description = "Creates a previewable PLY on normal computers."

    def preflight(self) -> dict:
        return {
            "ok": True,
            "engine": self.id,
            "name": self.name,
            "checks": [
                {"name": "Demo generator", "ok": True, "help": "Built into Maker Splat."}
            ],
            "missing": []
        }

    def run(self, root: Path, frame_files, update, preset):
        update(45, "Building your 3D preview", "Demo Engine is making a preview scene")
        create_demo_ply(root / "frames", root / "scene.ply")
        with (root / "log.txt").open("a") as f:
            f.write("Demo Engine created scene.ply. Use Nerfstudio Engine for real Gaussian splats.\n")
        return ["ply"]
