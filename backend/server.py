from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pathlib import Path
from typing import List
from uuid import uuid4
import json, shutil, re, zipfile, shutil as shutil_mod

from pipeline import run_pipeline
from quality import analyze_capture
from errors import friendly_error
from preflight import real_mode_preflight

app = FastAPI(title="Maker Splat")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PROJECTS = Path("projects")
PROJECTS.mkdir(exist_ok=True)
jobs = {}
active_job_id = None
cancel_requested = set()

CAPTURE_MODES = {
    "object": {"label": "Object", "tips": ["Circle the object slowly.", "Keep it centered.", "Capture high and low angles."]},
    "room": {"label": "Room", "tips": ["Walk slowly around the room.", "Capture corners and doorways.", "Avoid fast turns."]},
    "outdoor": {"label": "Outdoor", "tips": ["Shoot in soft light.", "Avoid moving people and cars.", "Capture all sides."]},
    "turntable": {"label": "Turntable", "tips": ["Keep camera still.", "Rotate object slowly.", "Use even lighting."]}
}

EXPORT_PRESETS = {
    "supersplat": {"label": "SuperSplat", "files": ["scene.splat", "scene.ply"]},
    "playcanvas": {"label": "PlayCanvas", "files": ["scene.splat", "scene.ply"]},
    "blender": {"label": "Blender", "files": ["scene.ply"]},
    "web": {"label": "Web Viewer ZIP", "files": ["viewer.html", "scene.ply", "scene.splat"]},
    "everything": {"label": "Everything", "files": ["scene.ply", "scene.splat", "thumbnail.jpg", "project.json", "maker-splat.log"]}
}

def recover_projects():
    for p in PROJECTS.iterdir():
        meta_file = p / "project.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                if meta.get("status") in {"running", "queued"}:
                    meta["status"] = "interrupted"
                    meta["stage"] = "Interrupted during previous run"
                    meta["progress"] = 0
                    meta_file.write_text(json.dumps(meta, indent=2))
            except Exception:
                pass

recover_projects()

def slugify(name):
    name = re.sub(r"[^a-zA-Z0-9 _.-]+", "", name).strip()
    return re.sub(r"\s+", " ", name) or "Untitled Project"

def project_dir(pid):
    return PROJECTS / pid

def meta_path(pid):
    return project_dir(pid) / "project.json"

def read_meta(pid):
    path = meta_path(pid)
    if not path.exists():
        raise HTTPException(404, "Project not found")
    return json.loads(path.read_text())

def write_meta(pid, meta):
    meta_path(pid).write_text(json.dumps(meta, indent=2))

def artifact_list(pid):
    root = project_dir(pid)
    names = {
        "ply":"scene.ply","splat":"scene.splat","zip":"maker-splat-package.zip",
        "share":"share-viewer.zip","log":"maker-splat.log","thumbnail":"thumbnail.jpg"
    }
    return [k for k,v in names.items() if (root / v).exists()]

@app.get("/api/health")
def health():
    return {"ok": True, "version": "3.0", "active_job_id": active_job_id}

@app.get("/api/preflight/real-mode")
def real_preflight():
    return real_mode_preflight()

@app.get("/api/setup")
def setup():
    check = check_computer()
    real = real_mode_preflight()
    return {
        "welcome": "Welcome to Maker Splat.",
        "demo_mode": "Demo mode works on normal computers and creates a previewable PLY.",
        "real_mode": "Real mode uses Nerfstudio to generate real Gaussian splats.",
        "real_mode_preflight": real,
        "real_mode_steps": [
            "Install NVIDIA drivers and NVIDIA Container Toolkit.",
            "Run the GPU compose profile.",
            "Confirm ffmpeg, COLMAP, ns-process-data, ns-train, and ns-export are available.",
            "Upload 30–150 overlapping photos or a slow video.",
            "Generate with Balanced first, then Best for final results."
        ],
        "computer": check,
        "next_steps": check["install_steps"]
    }

@app.get("/api/check-computer")
def check_computer():
    mapping = {
        "ffmpeg":"ffmpeg",
        "COLMAP":"colmap",
        "Nerfstudio process":"ns-process-data",
        "Nerfstudio train":"ns-train",
        "Nerfstudio export":"ns-export",
        "NVIDIA GPU":"nvidia-smi"
    }
    tools = {}
    for name, cmd in mapping.items():
        path = shutil_mod.which(cmd)
        tools[name] = {"found": bool(path), "path": path, "help": name}
    ready = tools["ffmpeg"]["found"] and tools["Nerfstudio train"]["found"]
    steps = []
    if not tools["ffmpeg"]["found"]:
        steps.append("Install ffmpeg so videos can be converted to frames.")
    if not tools["Nerfstudio train"]["found"]:
        steps.append("Install Nerfstudio to enable real splat generation.")
    if not tools["NVIDIA GPU"]["found"]:
        steps.append("A CUDA-capable NVIDIA GPU is recommended for real splats.")
    if not steps:
        steps.append("Everything looks ready.")
    return {
        "ready_for_demo": tools["ffmpeg"]["found"],
        "ready_for_real_splats": ready,
        "tools": tools,
        "summary": "Ready for real splats" if ready else "Demo mode available; real-mode tools missing.",
        "install_steps": steps
    }

@app.get("/api/capture-modes")
def capture_modes():
    return CAPTURE_MODES

@app.get("/api/export-presets")
def export_presets():
    return EXPORT_PRESETS

@app.get("/api/projects")
def list_projects():
    out = []
    for p in sorted(PROJECTS.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_dir() and (p/"project.json").exists():
            meta = json.loads((p/"project.json").read_text())
            meta["artifacts"] = artifact_list(meta["id"])
            out.append(meta)
    return out

@app.post("/api/projects")
def create_project(name: str = Form(...), source_type: str = Form("video"), preset: str = Form("balanced"), capture_mode: str = Form("object")):
    pid = str(uuid4())
    root = project_dir(pid)
    for folder in ["capture", "frames", "outputs", "exports"]:
        (root/folder).mkdir(parents=True, exist_ok=True)
    mode = CAPTURE_MODES.get(capture_mode, CAPTURE_MODES["object"])
    meta = {
        "id": pid, "name": slugify(name), "source_type": source_type, "preset": preset,
        "capture_mode": capture_mode, "status": "created", "stage": "Ready for files",
        "progress": 0, "quality": None, "artifacts": [], "mode_tips": mode["tips"]
    }
    write_meta(pid, meta)
    return meta

@app.get("/api/projects/{pid}")
def get_project(pid: str):
    meta = read_meta(pid)
    meta["artifacts"] = artifact_list(pid)
    return meta

@app.patch("/api/projects/{pid}")
def rename_project(pid: str, name: str = Form(...)):
    meta = read_meta(pid)
    meta["name"] = slugify(name)
    write_meta(pid, meta)
    return meta

@app.post("/api/projects/{pid}/upload")
async def upload(pid: str, files: List[UploadFile] = File(...)):
    meta = read_meta(pid)
    cap = project_dir(pid) / "capture"
    shutil.rmtree(cap, ignore_errors=True)
    cap.mkdir(parents=True)
    for i, f in enumerate(files):
        suffix = Path(f.filename or "").suffix.lower()
        if suffix not in {".png",".jpg",".jpeg",".webp",".mp4",".mov",".m4v",".webm"}:
            raise HTTPException(400, "Unsupported file type")
        (cap / f"capture_{i:04d}{suffix}").write_bytes(await f.read())
    meta["status"] = "uploaded"
    meta["stage"] = f"{len(files)} file(s) uploaded"
    write_meta(pid, meta)
    return meta

@app.post("/api/projects/{pid}/analyze")
def analyze(pid: str):
    meta = read_meta(pid)
    report = analyze_capture(project_dir(pid), meta.get("capture_mode","object"))
    meta["quality"] = report
    meta["stage"] = "Capture analyzed"
    write_meta(pid, meta)
    return report

@app.post("/api/projects/{pid}/generate")
def generate(pid: str, background_tasks: BackgroundTasks):
    global active_job_id
    if active_job_id:
        raise HTTPException(409, "Another splat is already generating. Wait for it to finish or cancel it first.")
    meta = read_meta(pid)
    if not list((project_dir(pid)/"capture").glob("*")):
        raise HTTPException(400, "Upload files first")
    jid = str(uuid4())
    active_job_id = jid
    jobs[jid] = {"id": jid, "project_id": pid, "status": "queued", "progress": 0, "stage": "Queued", "message": "Queued"}
    meta["status"] = "queued"
    write_meta(pid, meta)
    background_tasks.add_task(run_job, jid, pid)
    return jobs[jid]

@app.post("/api/jobs/{jid}/cancel")
def cancel_job(jid: str):
    if jid not in jobs:
        raise HTTPException(404, "Job not found")
    cancel_requested.add(jid)
    jobs[jid]["status"] = "canceling"
    jobs[jid]["message"] = "Cancel requested"
    return jobs[jid]

def run_job(jid, pid):
    global active_job_id
    root = project_dir(pid)
    def update(progress, stage, message=None):
        if jid in cancel_requested:
            raise RuntimeError("Generation canceled.")
        jobs[jid].update({"progress": progress, "stage": stage, "message": message or stage, "status": "running"})
        meta = read_meta(pid)
        meta.update({"progress": progress, "stage": stage, "status": "running"})
        write_meta(pid, meta)
    try:
        artifacts = run_pipeline(root, update)
        meta = read_meta(pid)
        meta.update({"status":"done","stage":"Ready to explore","progress":100,"artifacts":artifacts})
        write_meta(pid, meta)
        jobs[jid].update({"status":"done","progress":100,"stage":"Ready to explore","message":"Done"})
    except Exception as e:
        status = "canceled" if jid in cancel_requested else "error"
        msg = "Generation canceled." if status == "canceled" else friendly_error(e)
        meta = read_meta(pid)
        meta.update({"status":status,"stage":msg,"error":msg})
        write_meta(pid, meta)
        jobs[jid].update({"status":status,"message":msg})
    finally:
        if active_job_id == jid:
            active_job_id = None
        cancel_requested.discard(jid)

@app.get("/api/jobs/{jid}")
def job(jid: str):
    if jid not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[jid]

@app.get("/api/projects/{pid}/log")
def log(pid: str):
    path = project_dir(pid) / "maker-splat.log"
    return PlainTextResponse(path.read_text(errors="replace") if path.exists() else "")

@app.post("/api/projects/{pid}/export/{preset}")
def export_preset(pid: str, preset: str):
    if preset not in EXPORT_PRESETS:
        raise HTTPException(404, "Unknown export preset")
    if preset == "web":
        make_viewer_html(project_dir(pid))
    return make_export(pid, preset)

def make_viewer_html(root: Path):
    html = """<!doctype html>
<html><head><meta charset="utf-8"><title>Maker Splat Viewer</title>
<style>body{margin:0;background:#111;color:white;font-family:system-ui}#top{position:fixed;top:0;left:0;right:0;padding:12px 16px;background:#181818;z-index:2}#viewer{position:fixed;inset:56px 0 0 0}</style>
</head><body><div id="top"><strong>Maker Splat Viewer</strong> <input id="file" type="file" accept=".ply"> Choose the included scene.ply file.</div><div id="viewer"></div>
<script type="module">
import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { PLYLoader } from 'https://unpkg.com/three@0.160.0/examples/jsm/loaders/PLYLoader.js';
const el=document.getElementById('viewer'),scene=new THREE.Scene();scene.background=new THREE.Color(0x111111);
const camera=new THREE.PerspectiveCamera(55,el.clientWidth/el.clientHeight,.01,1000);camera.position.set(0,0,3);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setSize(el.clientWidth,el.clientHeight);el.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);scene.add(new THREE.AmbientLight(0xffffff,1));let points=null;
function render(){requestAnimationFrame(render);controls.update();renderer.render(scene,camera)}render();
window.addEventListener('resize',()=>{camera.aspect=el.clientWidth/el.clientHeight;camera.updateProjectionMatrix();renderer.setSize(el.clientWidth,el.clientHeight)});
document.getElementById('file').addEventListener('change',e=>{const file=e.target.files[0];if(!file)return;const url=URL.createObjectURL(file);new PLYLoader().load(url,geom=>{if(points)scene.remove(points);const hasColor=!!geom.getAttribute('color');points=new THREE.Points(geom,new THREE.PointsMaterial({size:.01,vertexColors:hasColor,color:0xffffff}));geom.computeBoundingSphere();scene.add(points);if(geom.boundingSphere){camera.position.set(0,0,Math.max(2,geom.boundingSphere.radius*3));controls.target.copy(geom.boundingSphere.center)}})});
</script></body></html>"""
    (root/"viewer.html").write_text(html)

def make_export(pid: str, preset: str):
    root = project_dir(pid)
    cfg = EXPORT_PRESETS[preset]
    export_name = f"maker-splat-{preset}.zip"
    export_path = root / "exports" / export_name
    export_path.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in cfg["files"]:
            path = root / name
            if path.exists():
                z.write(path, name)
    return {"ok": True, "preset": preset, "filename": export_name}

@app.get("/api/projects/{pid}/download/{artifact}")
def download(pid: str, artifact: str):
    allowed = {"ply":"scene.ply","splat":"scene.splat","zip":"maker-splat-package.zip","thumbnail":"thumbnail.jpg","log":"maker-splat.log"}
    if artifact not in allowed:
        raise HTTPException(404, "Unknown artifact")
    path = project_dir(pid) / allowed[artifact]
    if not path.exists():
        raise HTTPException(404, "Artifact missing")
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download-export/{preset}")
def download_export(pid: str, preset: str):
    path = project_dir(pid) / "exports" / f"maker-splat-{preset}.zip"
    if not path.exists():
        raise HTTPException(404, "Export missing")
    return FileResponse(path, filename=path.name)

@app.delete("/api/projects/{pid}")
def delete(pid: str):
    shutil.rmtree(project_dir(pid), ignore_errors=True)
    return {"ok": True}
