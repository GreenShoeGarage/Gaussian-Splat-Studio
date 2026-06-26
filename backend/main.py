from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
from trainer import train_scene

app = FastAPI()

Path("jobs").mkdir(exist_ok=True)

@app.post("/api/v1/create")
async def create(file: UploadFile = File(...)):

    src = Path("jobs/input.png")
    src.write_bytes(await file.read())

    result = train_scene(src)

    return FileResponse(
        result,
        filename="gaussian_scene.ply"
    )