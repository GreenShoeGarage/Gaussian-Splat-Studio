from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from typing import List
from uuid import uuid4
import shutil

from pipeline import run_pipeline

app = FastAPI(title="Maker Splat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RUNS = Path("runs")
RUNS.mkdir(exist_ok=True)

jobs = {}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate")
async def generate(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(400, "Upload at least one video or image.")

    job_id = str(uuid4())
    job_dir = RUNS / job_id
    input_dir = job_dir / "input"
    input_dir.mkdir(parents=True)

    for index, file in enumerate(files):
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".m4v", ".webm"}:
            raise HTTPException(400, f"Unsupported file type: {suffix}")
        target = input_dir / f"upload_{index:03d}{suffix}"
        target.write_bytes(await file.read())

    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Queued",
        "artifacts": [],
    }

    background_tasks.add_task(run_job, job_id, job_dir)

    return jobs[job_id]


def run_job(job_id: str, job_dir: Path):
    def update(progress, message):
        jobs[job_id]["progress"] = progress
        jobs[job_id]["message"] = message

    try:
        jobs[job_id]["status"] = "running"
        artifacts = run_pipeline(job_dir, update)
        jobs[job_id]["artifacts"] = artifacts
        jobs[job_id]["status"] = "done"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = "Done"
    except Exception as exc:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = str(exc)


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found.")
    return jobs[job_id]


@app.get("/jobs/{job_id}/log")
def get_log(job_id: str):
    log = RUNS / job_id / "maker-splat.log"
    if not log.exists():
        return PlainTextResponse("")
    return PlainTextResponse(log.read_text(errors="replace"))


@app.get("/jobs/{job_id}/download/{name}")
def download(job_id: str, name: str):
    allowed = {
        "ply": "scene.ply",
        "splat": "scene.splat",
        "zip": "maker-splat-output.zip",
        "log": "maker-splat.log",
    }
    if name not in allowed:
        raise HTTPException(404, "Artifact not found.")

    path = RUNS / job_id / allowed[name]
    if not path.exists():
        raise HTTPException(404, "Artifact missing.")

    return FileResponse(path, filename=path.name)


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    shutil.rmtree(RUNS / job_id, ignore_errors=True)
    jobs.pop(job_id, None)
    return {"ok": True}
