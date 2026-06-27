from pathlib import Path
from PIL import Image
import os, shutil, subprocess, zipfile, json
from fallback_splat import create_demo_ply
from preflight import real_mode_preflight

REAL_MODE = os.getenv("MAKER_SPLAT_REAL_MODE", "0") == "1"
FRAME_RATE = int(os.getenv("MAKER_SPLAT_FRAME_RATE", "2"))
PRESETS = {"fast":{"iterations":"2500","label":"Fast"},"balanced":{"iterations":"7000","label":"Balanced"},"best":{"iterations":"15000","label":"Best"}}

def log(root, msg):
    with (root/"maker-splat.log").open("a") as f:
        f.write(msg + "\\n")

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
    mode = meta.get("capture_mode", "object")
    artifacts = []

    log(root, f"Maker Splat started. Mode={'real' if REAL_MODE else 'demo'} Preset={preset['label']} Capture={mode}")
    update(8, "Preparing capture", "Checking your video/photos")

    videos = [p for p in capture.iterdir() if p.suffix.lower() in {".mp4",".mov",".m4v",".webm"}]
    images = [p for p in capture.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}]

    if videos:
        update(18, "Preparing photos", "Extracting useful frames")
        run_command(root, ["ffmpeg","-y","-i",str(videos[0]),"-vf",f"fps={FRAME_RATE}",str(frames/"frame_%05d.png")])
    else:
        update(18, "Preparing photos", "Copying photos")
        for i, img in enumerate(images):
            shutil.copyfile(img, frames/f"frame_{i:05d}{img.suffix.lower()}")

    frame_files = sorted([p for p in frames.iterdir() if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}])
    if len(frame_files) < 3:
        raise RuntimeError("Need at least 3 photos or frames.")

    make_thumbnail(root, frame_files[0])
    artifacts.append("thumbnail")

    if REAL_MODE:
        preflight = real_mode_preflight()
        log(root, "Real-mode preflight: " + json.dumps(preflight))
        if preflight["missing"]:
            raise RuntimeError("Nerfstudio real-mode tools are missing: " + ", ".join(preflight["missing"]))

        update(34, "Finding camera positions", "Nerfstudio is processing")
        ns_data = outputs/"nerfstudio-data"
        run_command(root, ["ns-process-data","images","--data",str(frames),"--output-dir",str(ns_data)])

        update(58, "Creating Gaussian splats", "Training splat")
        ns_runs = outputs/"nerfstudio-runs"
        run_command(root, ["ns-train","splatfacto","--data",str(ns_data),"--output-dir",str(ns_runs),"--max-num-iterations",preset["iterations"]])

        configs = sorted(ns_runs.rglob("config.yml"), key=lambda p:p.stat().st_mtime, reverse=True)
        if not configs:
            raise RuntimeError("No Nerfstudio config found.")

        update(86, "Exporting", "Saving splat")
        ns_export = outputs/"nerfstudio-export"
        run_command(root, ["ns-export","gaussian-splat","--load-config",str(configs[0]),"--output-dir",str(ns_export)])

        for c in ns_export.rglob("*"):
            if c.suffix.lower() == ".ply":
                shutil.copyfile(c, root/"scene.ply"); artifacts.append("ply")
            if c.suffix.lower() == ".splat":
                shutil.copyfile(c, root/"scene.splat"); artifacts.append("splat")

        if "ply" not in artifacts and "splat" not in artifacts:
            raise RuntimeError("Nerfstudio export finished, but no PLY/SPLAT artifact was found.")
    else:
        update(42, "Finding camera positions", "Demo mode is arranging frames")
        update(68, "Creating Gaussian splats", "Making preview scene")
        create_demo_ply(frames, root/"scene.ply", mode=mode)
        artifacts.append("ply")
        log(root, "Demo mode output created.")

    update(94, "Packing export", "Creating zip")
    package(root); artifacts += ["zip","log"]
    update(100, "Ready to explore", "Open viewer or export")
    return sorted(set(artifacts))

def make_thumbnail(root, image_path):
    try:
        img = Image.open(image_path).convert("RGB"); img.thumbnail((720,480)); img.save(root/"thumbnail.jpg", quality=88)
    except Exception:
        pass

def package(root):
    with zipfile.ZipFile(root/"maker-splat-package.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in ["scene.ply","scene.splat","thumbnail.jpg","project.json","maker-splat.log"]:
            p = root/name
            if p.exists(): z.write(p, name)
