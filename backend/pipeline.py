from pathlib import Path
from PIL import Image
import json, os, shutil, subprocess, zipfile
from engines import get_engine
from environment_report import collect_environment
from dependency_doctor import dependency_report

FRAME_RATE = int(os.getenv("MAKER_SPLAT_FRAME_RATE","2"))
PRESETS = {
    "fast":{"iterations":"2500","label":"Fast"},
    "balanced":{"iterations":"7000","label":"Balanced"},
    "best":{"iterations":"15000","label":"Best"}
}

def log(root, msg):
    with (root/"log.txt").open("a") as f:
        f.write(msg + "\n")

def run_command(root, cmd):
    log(root, "$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=root, check=True)

def run_pipeline(root: Path, update):
    capture, frames, outputs = root/"capture", root/"frames", root/"outputs"
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir(exist_ok=True)
    outputs.mkdir(exist_ok=True)

    meta = json.loads((root/"project.json").read_text())
    preset = PRESETS.get(meta.get("preset","balanced"), PRESETS["balanced"])
    engine = get_engine(meta.get("engine"))

    artifacts = []
    log(root, f"Maker Splat started. Engine={engine.id} Preset={preset['label']}")
    collect_environment(root)
    dependency_report(root)
    update(8, "Looking at your capture", "Checking your video or photos")

    videos = [p for p in capture.iterdir() if p.suffix.lower() in {".mp4",".mov",".m4v",".webm"}]
    images = [p for p in capture.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}]

    if videos:
        update(18, "Turning video into photos", "Picking useful frames from your video")
        run_command(root, ["ffmpeg","-y","-i",str(videos[0]),"-vf",f"fps={FRAME_RATE}",str(frames/"frame_%05d.png")])
    else:
        update(18, "Preparing photos", "Getting your photos ready")
        for i,img in enumerate(images):
            shutil.copyfile(img, frames/f"frame_{i:05d}{img.suffix.lower()}")

    frame_files = sorted(p for p in frames.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"})
    if len(frame_files) < 3:
        raise RuntimeError("Need at least 3 photos or frames.")

    make_thumbnail(root, frame_files[0])
    artifacts.append("thumbnail")

    engine_artifacts = engine.run(root, frame_files, update, preset)
    artifacts.extend(engine_artifacts)

    update(94, "Packing your download", "Creating a shareable download")
    with zipfile.ZipFile(root/"export.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in ["scene.ply","scene.splat","thumbnail.jpg","project.json","log.txt","diagnostics.json","pipeline_state.json","REAL_MODE_REPORT.md","VALIDATION_REPORT.md","validation_manifest.json","ENVIRONMENT_REPORT.md","environment_report.json","NERFSTUDIO_COMPATIBILITY.json","FAILURE_CLASSIFICATION.md","failure_classification.json","DEPENDENCY_DOCTOR.md","dependency_report.json","job_state.json"]:
            p = root/name
            if p.exists():
                z.write(p, name)
    artifacts += ["zip","log"]

    write_diagnostics(root, engine.id, artifacts)
    update(100, "Ready to explore", "Done")
    return sorted(set(artifacts))

def write_diagnostics(root, engine_id, artifacts):
    data = {
        "engine": engine_id,
        "artifacts": artifacts,
        "has_ply": (root/"scene.ply").exists(),
        "has_splat": (root/"scene.splat").exists(),\n        "first_splat_candidate": True,\n        "validation_manifest": (root/"validation_manifest.json").exists(),\n        "validation_report": (root/"VALIDATION_REPORT.md").exists(),
        "environment_report": (root/"ENVIRONMENT_REPORT.md").exists(),
        "failure_classification": (root/"FAILURE_CLASSIFICATION.md").exists(),
        "dependency_report": (root/"DEPENDENCY_DOCTOR.md").exists(),
        "job_state": (root/"job_state.json").exists(),
        "log": "log.txt",\n        "pipeline_state": (root/"pipeline_state.json").exists(),\n        "real_mode_report": (root/"REAL_MODE_REPORT.md").exists()
    }
    (root/"diagnostics.json").write_text(json.dumps(data, indent=2))

def make_thumbnail(root, image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img.thumbnail((720,480))
        img.save(root/"thumbnail.jpg", quality=88)
    except Exception:
        pass
