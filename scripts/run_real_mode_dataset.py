#!/usr/bin/env python3
from pathlib import Path
import sys, shutil, json, time, os
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pipeline import run_pipeline
from output_validator import validate_project_output
from failure_classifier import classify_failure

def main():
    if len(sys.argv) < 3:
        print("Usage: run_real_mode_dataset.py <dataset_dir> <project_dir>")
        return 2
    dataset = Path(sys.argv[1]).resolve()
    project = Path(sys.argv[2]).resolve()
    images = dataset / "images"
    if not images.exists():
        print(f"Missing images folder: {images}")
        return 2

    capture = project / "capture"
    capture.mkdir(parents=True, exist_ok=True)
    (project / "frames").mkdir(exist_ok=True)
    (project / "outputs").mkdir(exist_ok=True)

    files = [p for p in sorted(images.iterdir()) if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    if len(files) < 3:
        print("Dataset needs at least 3 images.")
        return 2

    for idx, src in enumerate(files):
        shutil.copyfile(src, capture / f"dataset_{idx:04d}{src.suffix.lower()}")

    meta = {
        "id": project.name, "name": f"Dataset {dataset.name}", "preset": os.getenv("MAKER_SPLAT_PRESET", "fast"),
        "engine": "nerfstudio", "status": "uploaded", "stage": "Dataset copied", "progress": 0,
        "created_at": int(time.time()), "updated_at": int(time.time()), "quality": None, "error": None,
        "artifacts": [], "favorite": False, "deleted": False, "versions": [], "notes": "Created by qa/run-real-mode-dataset.sh"
    }
    (project / "project.json").write_text(json.dumps(meta, indent=2))

    def update(progress, stage, message=None):
        print(f"[{progress:03d}%] {stage}: {message or ''}")

    try:
        artifacts = run_pipeline(project, update)
        validation = validate_project_output(project)
        print(json.dumps({"artifacts": artifacts, "validation": validation}, indent=2))
        return 0 if validation.get("real_splat_verified") else 3
    except Exception as exc:
        print(f"Pipeline failed: {exc}")
        try:
            print(json.dumps(classify_failure(project), indent=2))
        except Exception:
            pass
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
