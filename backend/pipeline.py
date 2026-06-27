from pathlib import Path
import os
import subprocess
import shutil
import zipfile

from fallback_splat import create_demo_ply

REAL_MODE = os.getenv("GSS_REAL_MODE", "0") == "1"
FRAME_RATE = int(os.getenv("GSS_FRAME_RATE", "2"))


def log(job_dir: Path, message: str):
    with (job_dir / "maker-splat.log").open("a") as f:
        f.write(message + "\n")


def run(cmd: list[str], job_dir: Path):
    log(job_dir, "$ " + " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=job_dir)


def run_pipeline(job_dir: Path, update):
    input_dir = job_dir / "input"
    frames_dir = job_dir / "frames"
    output_dir = job_dir / "output"

    frames_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    update(10, "Preparing files")
    log(job_dir, "Maker Splat started")

    videos = [p for p in input_dir.iterdir() if p.suffix.lower() in {".mp4", ".mov", ".m4v", ".webm"}]
    images = [p for p in input_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]

    if videos:
        update(20, "Extracting video frames")
        run([
            "ffmpeg",
            "-y",
            "-i",
            str(videos[0]),
            "-vf",
            f"fps={FRAME_RATE}",
            str(frames_dir / "frame_%05d.png"),
        ], job_dir)
    else:
        update(20, "Copying images")
        for i, image in enumerate(images):
            shutil.copyfile(image, frames_dir / f"frame_{i:05d}{image.suffix.lower()}")

    frame_count = len(list(frames_dir.glob("*")))
    log(job_dir, f"Frames/images ready: {frame_count}")

    if frame_count < 3:
        raise RuntimeError("Need at least 3 images/frames. Try a longer video or more photos.")

    artifacts = []

    if REAL_MODE:
        update(35, "Processing cameras with Nerfstudio")
        ns_data = job_dir / "nerfstudio-data"
        run([
            "ns-process-data",
            "images",
            "--data",
            str(frames_dir),
            "--output-dir",
            str(ns_data),
        ], job_dir)

        update(55, "Training splat")
        ns_runs = job_dir / "nerfstudio-runs"
        run([
            "ns-train",
            "splatfacto",
            "--data",
            str(ns_data),
            "--output-dir",
            str(ns_runs),
            "--max-num-iterations",
            "7000",
        ], job_dir)

        update(85, "Exporting splat")
        configs = sorted(ns_runs.rglob("config.yml"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not configs:
            raise RuntimeError("Training finished but no Nerfstudio config.yml was found.")

        ns_export = job_dir / "nerfstudio-export"
        run([
            "ns-export",
            "gaussian-splat",
            "--load-config",
            str(configs[0]),
            "--output-dir",
            str(ns_export),
        ], job_dir)

        for candidate in ns_export.rglob("*"):
            if candidate.suffix.lower() == ".ply":
                shutil.copyfile(candidate, job_dir / "scene.ply")
                artifacts.append("ply")
            elif candidate.suffix.lower() == ".splat":
                shutil.copyfile(candidate, job_dir / "scene.splat")
                artifacts.append("splat")

        if not artifacts:
            raise RuntimeError("Nerfstudio export completed, but no .ply or .splat file was found.")
    else:
        update(60, "Creating demo splat preview")
        create_demo_ply(frames_dir, job_dir / "scene.ply")
        artifacts.append("ply")
        log(job_dir, "Demo mode created scene.ply. Set GSS_REAL_MODE=1 for real Nerfstudio generation.")

    update(95, "Packaging result")
    with zipfile.ZipFile(job_dir / "maker-splat-output.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in ["scene.ply", "scene.splat", "maker-splat.log"]:
            path = job_dir / name
            if path.exists():
                z.write(path, path.name)
    artifacts.append("zip")
    artifacts.append("log")

    return sorted(set(artifacts))
