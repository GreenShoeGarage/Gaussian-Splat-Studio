from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
from worker import submit_job

app = FastAPI()

Path("jobs").mkdir(exist_ok=True)

@app.post("/api/jobs")
async def create_job(file: UploadFile = File(...)):

    path = Path("jobs/input")
    path.write_bytes(await file.read())

    result = submit_job(path)

    return FileResponse(
        result,
        filename="gaussian_scene.ply"
    )