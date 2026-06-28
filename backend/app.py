from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, HTMLResponse
from pathlib import Path
from typing import List
from uuid import uuid4
import json, shutil, time, zipfile

from pipeline import run_pipeline
from quality import analyze_project
from system_check import check_system
from errors import friendly_error
from capture_tools import cleanup_capture
from share_tools import make_share_package, project_manifest, import_project_zip, write_share_viewer
from settings_store import load_settings, save_settings
from engines import list_engines, get_engine
from output_validator import validate_project_output
from failure_classifier import classify_failure
from environment_report import collect_environment
from dependency_doctor import dependency_report
from job_state import write_job_state, read_job_state

app = FastAPI(title="Maker Splat", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

PROJECTS = Path("projects")
PROJECTS.mkdir(exist_ok=True)
jobs = {}
active_job_id = None
cancel_requested = set()

def project_dir(pid): return PROJECTS / pid
def meta_path(pid): return project_dir(pid) / "project.json"
def now(): return int(time.time())

def read_meta(pid):
    p = meta_path(pid)
    if not p.exists(): raise HTTPException(404, "Project not found.")
    return json.loads(p.read_text())

def write_meta(pid, data):
    meta_path(pid).write_text(json.dumps(data, indent=2))

def artifact_list(pid):
    root = project_dir(pid)
    mapping = {"ply":"scene.ply","splat":"scene.splat","zip":"export.zip","thumbnail":"thumbnail.jpg","log":"log.txt","diagnostics":"diagnostics.json","report":"REAL_MODE_REPORT.md","state":"pipeline_state.json","validation":"VALIDATION_REPORT.md","manifest":"validation_manifest.json","environment":"ENVIRONMENT_REPORT.md","failure":"FAILURE_CLASSIFICATION.md","compatibility":"NERFSTUDIO_COMPATIBILITY.json","dependency":"DEPENDENCY_DOCTOR.md","jobstate":"job_state.json","share":"maker-splat-share.zip"}
    return [k for k,v in mapping.items() if (root/v).exists()]

def recover():
    for p in PROJECTS.iterdir():
        m = p / "project.json"
        if m.exists():
            try:
                d = json.loads(m.read_text())
                if d.get("status") in {"queued","running"}:
                    d.update({"status":"interrupted","stage":"Interrupted during previous run","progress":0})
                    m.write_text(json.dumps(d, indent=2))
            except Exception:
                pass
recover()

@app.get("/api/health")
def health():
    return {"ok": True, "version": "1.0.0-mvp", "release": "MVP Candidate", "active_job_id": active_job_id}

@app.get("/api/system")
def system():
    return check_system()



@app.get("/api/engines")
def engines():
    return {
        "current": load_settings().get("engine", "demo"),
        "engines": list_engines()
    }

@app.get("/api/engines/{engine_id}/preflight")
def engine_preflight(engine_id: str):
    return get_engine(engine_id).preflight()

@app.patch("/api/projects/{pid}/engine")
def set_project_engine(pid: str, engine: str = Form(...)):
    d = read_meta(pid)
    d["engine"] = engine
    d["updated_at"] = now()
    write_meta(pid, d)
    return d





@app.get("/api/dependencies")
def dependencies():
    return dependency_report()

@app.get("/api/projects/{pid}/job-state")
def get_project_job_state(pid: str):
    state = read_job_state(project_dir(pid))
    return state or {"status": "none"}

@app.get("/api/projects/{pid}/download/dependency")
def download_dependency_report(pid: str):
    path = project_dir(pid) / "DEPENDENCY_DOCTOR.md"
    if not path.exists():
        dependency_report(project_dir(pid))
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download/jobstate")
def download_job_state(pid: str):
    path = project_dir(pid) / "job_state.json"
    if not path.exists():
        raise HTTPException(404, "Job state missing.")
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/export-bundle")
def export_bundle(pid: str):
    root = project_dir(pid)
    out = root / "maker-splat-mvp-bundle.zip"
    import zipfile
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in [
            "scene.splat", "scene.ply", "thumbnail.jpg", "project.json", "log.txt",
            "diagnostics.json", "VALIDATION_REPORT.md", "validation_manifest.json",
            "REAL_MODE_REPORT.md", "pipeline_state.json", "ENVIRONMENT_REPORT.md",
            "FAILURE_CLASSIFICATION.md", "DEPENDENCY_DOCTOR.md", "job_state.json"
        ]:
            p = root / name
            if p.exists():
                z.write(p, name)
    return FileResponse(out, filename=out.name)

@app.get("/api/environment")
def environment():
    return collect_environment()

@app.get("/api/projects/{pid}/classify-failure")
def classify_project_failure(pid: str):
    return classify_failure(project_dir(pid))

@app.get("/api/projects/{pid}/download/environment")
def download_environment_report(pid: str):
    path = project_dir(pid) / "ENVIRONMENT_REPORT.md"
    if not path.exists():
        collect_environment(project_dir(pid))
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download/failure")
def download_failure_report(pid: str):
    path = project_dir(pid) / "FAILURE_CLASSIFICATION.md"
    if not path.exists():
        classify_failure(project_dir(pid))
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download/compatibility")
def download_compatibility(pid: str):
    path = project_dir(pid) / "NERFSTUDIO_COMPATIBILITY.json"
    if not path.exists():
        collect_environment(project_dir(pid))
    return FileResponse(path, filename=path.name)

@app.post("/api/projects/{pid}/verify-output")
def verify_output(pid: str):
    result = validate_project_output(project_dir(pid))
    d = read_meta(pid)
    d["validation"] = result
    d["updated_at"] = now()
    write_meta(pid, d)
    return result

@app.get("/api/projects/{pid}/download/validation")
def download_validation_report(pid: str):
    path = project_dir(pid) / "VALIDATION_REPORT.md"
    if not path.exists():
        validate_project_output(project_dir(pid))
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download/validation-manifest")
def download_validation_manifest(pid: str):
    path = project_dir(pid) / "validation_manifest.json"
    if not path.exists():
        validate_project_output(project_dir(pid))
    return FileResponse(path, filename=path.name)

@app.get("/api/nerfstudio/probe")
def nerfstudio_probe():
    from tool_probe import probe_nerfstudio
    return probe_nerfstudio()

@app.get("/api/projects/{pid}/download/report")
def download_real_mode_report(pid: str):
    path = project_dir(pid) / "REAL_MODE_REPORT.md"
    if not path.exists():
        raise HTTPException(404, "Real Mode report missing.")
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download/pipeline-state")
def download_pipeline_state(pid: str):
    path = project_dir(pid) / "pipeline_state.json"
    if not path.exists():
        raise HTTPException(404, "Pipeline state missing.")
    return FileResponse(path, filename=path.name)

@app.get("/api/projects/{pid}/download/diagnostics")
def download_diagnostics(pid: str):
    root = project_dir(pid)
    diag = root / "diagnostics.json"
    if not diag.exists():
        data = {
            "project": read_meta(pid),
            "artifacts": artifact_list(pid),
            "log_exists": (root / "log.txt").exists(),
        }
        diag.write_text(json.dumps(data, indent=2))
    return FileResponse(diag, filename="diagnostics.json")


@app.get("/api/readiness")
def readiness():
    sys = check_system()
    project_count = len([p for p in PROJECTS.iterdir() if p.is_dir() and (p / "project.json").exists()])
    return {
        "ok": True,
        "release": "MVP Candidate",
        "checks": [
            {"name": "Local backend", "ok": True, "help": "Maker Splat backend is running."},
            {"name": "Project storage", "ok": PROJECTS.exists(), "help": "Local project folder is available."},
            {"name": "Video support", "ok": sys["demo_ready"], "help": "FFmpeg is used to turn videos into photos."},
            {"name": "Real mode tools", "ok": sys["real_ready"], "help": "Optional advanced Gaussian splat generation tools."},
        ],
        "project_count": project_count,
        "local_first": True,
        "engine": load_settings().get("engine", "demo"),
        "message": "Demo Engine is ready." if load_settings().get("engine", "demo") == "demo" else ("Nerfstudio Engine is ready." if sys["real_ready"] else "Nerfstudio Engine needs setup.")
    }

@app.get("/api/settings")
def get_settings():
    return load_settings()

@app.patch("/api/settings")
async def update_settings(payload: dict):
    return save_settings(payload)

@app.post("/api/projects/{pid}/undo-delete")
def undo_delete(pid: str):
    return restore_project(pid)



@app.post("/api/sample-project")
def create_sample_project():
    project = create_project(name="Sample Splat", preset="fast")
    pid = project["id"]
    root = project_dir(pid)
    capture = root / "capture"
    sample_assets = Path("sample_assets")
    for index, image in enumerate(sorted(sample_assets.glob("*.jpg"))):
        shutil.copyfile(image, capture / f"sample_{index:04d}.jpg")
    project.update({
        "status": "uploaded",
        "stage": "Sample photos ready",
        "updated_at": now(),
    })
    write_meta(pid, project)
    return project

@app.get("/api/projects")
def list_projects():
    out = []
    for p in sorted(PROJECTS.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        m = p / "project.json"
        if p.is_dir() and m.exists():
            d = json.loads(m.read_text())
            d.setdefault("favorite", False)
            d.setdefault("deleted", False)
            d.setdefault("versions", [])
            d["artifacts"] = artifact_list(d["id"])
            if not d.get("deleted", False):
                out.append(d)
    return out

@app.post("/api/projects")
def create_project(name: str = Form("My Splat"), preset: str = Form("balanced")):
    pid = str(uuid4())
    root = project_dir(pid)
    for sub in ["capture","frames","outputs"]:
        (root/sub).mkdir(parents=True, exist_ok=True)
    data = {"id":pid,"name":name.strip() or "My Splat","preset":preset,"engine":load_settings().get("engine","demo"),"status":"created","stage":"Ready for files","progress":0,"created_at":now(),"updated_at":now(),"quality":None,"error":None,"artifacts":[],"favorite":False,"deleted":False,"versions":[],"notes":"","cleanup":None}
    write_meta(pid, data)
    return data

@app.get("/api/projects/{pid}")
def get_project(pid: str):
    d = read_meta(pid)
    d.setdefault("favorite", False)
    d.setdefault("deleted", False)
    d.setdefault("versions", [])
    d["artifacts"] = artifact_list(pid)
    return d

@app.patch("/api/projects/{pid}")
def rename_project(pid: str, name: str = Form(...)):
    d = read_meta(pid)
    d["name"] = name.strip() or d["name"]
    d["updated_at"] = now()
    write_meta(pid, d)
    return d

@app.post("/api/projects/{pid}/upload")
async def upload(pid: str, files: List[UploadFile] = File(...)):
    d = read_meta(pid)
    capture = project_dir(pid) / "capture"
    shutil.rmtree(capture, ignore_errors=True)
    capture.mkdir(parents=True, exist_ok=True)
    allowed = {".png",".jpg",".jpeg",".webp",".mp4",".mov",".m4v",".webm"}
    if not files: raise HTTPException(400, "Upload at least one file.")
    for i, f in enumerate(files):
        suffix = Path(f.filename or "").suffix.lower()
        if suffix not in allowed: raise HTTPException(400, f"Unsupported file type: {suffix}")
        (capture / f"capture_{i:04d}{suffix}").write_bytes(await f.read())
    d.update({"status":"uploaded","stage":f"{len(files)} file(s) uploaded","progress":0,"quality":None,"error":None,"updated_at":now()})
    write_meta(pid, d)
    return d

@app.post("/api/projects/{pid}/analyze")
def analyze(pid: str):
    d = read_meta(pid)
    q = analyze_project(project_dir(pid))
    d["quality"] = q
    d["stage"] = "Capture analyzed"
    d["updated_at"] = now()
    write_meta(pid, d)
    return q

@app.post("/api/projects/{pid}/generate")
def generate(pid: str, background_tasks: BackgroundTasks):
    global active_job_id
    if active_job_id:
        raise HTTPException(409, "Another project is already generating.")
    d = read_meta(pid)
    if not list((project_dir(pid)/"capture").glob("*")):
        raise HTTPException(400, "Upload files first.")
    jid = str(uuid4())
    active_job_id = jid
    jobs[jid] = {"id":jid,"project_id":pid,"status":"queued","stage":"Queued","message":"Queued","progress":0}
    d.update({"status":"queued","stage":"Queued","progress":0,"error":None,"updated_at":now()})
    write_meta(pid, d)
    background_tasks.add_task(run_job, jid, pid)
    return jobs[jid]

@app.post("/api/jobs/{jid}/cancel")
def cancel(jid: str):
    if jid not in jobs: raise HTTPException(404, "Job not found.")
    cancel_requested.add(jid)
    jobs[jid].update({"status":"canceling","message":"Cancel requested"})
    return jobs[jid]

def run_job(jid, pid):
    global active_job_id
    root = project_dir(pid)
    def update(progress, stage, message=None):
        if jid in cancel_requested: raise RuntimeError("Generation canceled.")
        jobs[jid].update({"status":"running","progress":progress,"stage":stage,"message":message or stage})
        try:
            write_job_state(project_dir(pid), jid, "running", stage, progress, message or stage)
        except Exception:
            pass
        d = read_meta(pid); d.update({"status":"running","progress":progress,"stage":stage,"updated_at":now()}); write_meta(pid,d)
    try:
        arts = run_pipeline(root, update)
        d = read_meta(pid); versions=d.get("versions", []); versions.append({"time": now(), "artifacts": arts, "label": f"Version {len(versions)+1}"}); d.update({"status":"done","stage":"Ready to explore","progress":100,"artifacts":arts,"versions":versions,"error":None,"updated_at":now()}); write_meta(pid,d)
        try:
            write_job_state(project_dir(pid), jid, "done", "Ready to explore", 100, "Done")
        except Exception:
            pass
        jobs[jid].update({"status":"done","progress":100,"stage":"Ready to preview","message":"Done"})
    except Exception as e:
        canceled = jid in cancel_requested
        msg = "Generation canceled." if canceled else friendly_error(e)
        status = "canceled" if canceled else "error"
        d = read_meta(pid); d.update({"status":status,"stage":msg,"error":msg,"updated_at":now()}); write_meta(pid,d)
        try:
            classify_failure(project_dir(pid))
        except Exception:
            pass
        try:
            write_job_state(project_dir(pid), jid, status, msg, 0, msg)
        except Exception:
            pass
        jobs[jid].update({"status":status,"message":msg,"stage":msg})
    finally:
        if active_job_id == jid: active_job_id = None
        cancel_requested.discard(jid)

@app.get("/api/jobs/{jid}")
def get_job(jid: str):
    if jid not in jobs: raise HTTPException(404, "Job not found.")
    return jobs[jid]

@app.post("/api/projects/{pid}/export")
def export_project(pid: str):
    root = project_dir(pid)
    if not (root/"scene.ply").exists() and not (root/"scene.splat").exists():
        raise HTTPException(400, "Generate a scene first.")
    with zipfile.ZipFile(root/"export.zip","w",zipfile.ZIP_DEFLATED) as z:
        for name in ["scene.ply","scene.splat","thumbnail.jpg","project.json","log.txt"]:
            p = root/name
            if p.exists(): z.write(p, name)
    return {"ok": True}


@app.get("/api/projects/{pid}/manifest")
def get_manifest(pid: str):
    d = read_meta(pid)
    return project_manifest(project_dir(pid), d.get("share_link"))

@app.post("/api/projects/{pid}/share-package")
def create_share_package(pid: str):
    d = read_meta(pid)
    root = project_dir(pid)
    if not (root / "scene.ply").exists() and not (root / "scene.splat").exists():
        raise HTTPException(400, "Generate a scene before sharing.")
    make_share_package(root, pid, d.get("name", "Maker Splat"))
    d["share_package_ready"] = True
    d["share_link"] = f"http://localhost:8000/share/{pid}"
    d["updated_at"] = now()
    write_meta(pid, d)
    return {"ok": True, "share_link": d["share_link"]}

@app.get("/share/{pid}", response_class=HTMLResponse)
def local_share_page(pid: str):
    d = read_meta(pid)
    root = project_dir(pid)
    write_share_viewer(root, pid, d.get("name", "Maker Splat"))
    html = (root / "share.html").read_text()
    html = html.replace("scene.ply", f"/api/projects/{pid}/download/ply")
    html = html.replace("scene.splat", f"/api/projects/{pid}/download/splat")
    html = html.replace("project.json", f"/api/projects/{pid}/manifest")
    return HTMLResponse(html)

@app.get("/api/projects/{pid}/download/share")
def download_share_package(pid: str):
    path = project_dir(pid) / "maker-splat-share.zip"
    if not path.exists():
        d = read_meta(pid)
        make_share_package(project_dir(pid), pid, d.get("name", "Maker Splat"))
    return FileResponse(path, filename=path.name)

@app.post("/api/import-project")
async def import_project(file: UploadFile = File(...)):
    new_id = str(uuid4())
    tmp = PROJECTS / f"import-{new_id}.zip"
    tmp.write_bytes(await file.read())
    try:
        meta = import_project_zip(PROJECTS, tmp, new_id)
    finally:
        try:
            tmp.unlink()
        except Exception:
            pass
    return meta

@app.get("/api/trash")
def trash():
    return deleted_projects()


@app.get("/api/projects/{pid}/download/{artifact}")
def download(pid: str, artifact: str):
    mapping = {"ply":"scene.ply","splat":"scene.splat","zip":"export.zip","thumbnail":"thumbnail.jpg","log":"log.txt","diagnostics":"diagnostics.json","report":"REAL_MODE_REPORT.md","state":"pipeline_state.json","validation":"VALIDATION_REPORT.md","manifest":"validation_manifest.json","environment":"ENVIRONMENT_REPORT.md","failure":"FAILURE_CLASSIFICATION.md","compatibility":"NERFSTUDIO_COMPATIBILITY.json","dependency":"DEPENDENCY_DOCTOR.md","jobstate":"job_state.json","share":"maker-splat-share.zip"}
    if artifact not in mapping: raise HTTPException(404, "Unknown artifact.")
    p = project_dir(pid) / mapping[artifact]
    if not p.exists(): raise HTTPException(404, "Artifact missing.")
    return FileResponse(p, filename=p.name)

@app.get("/api/projects/{pid}/log")
def get_log(pid: str):
    p = project_dir(pid) / "log.txt"
    return PlainTextResponse(p.read_text(errors="replace") if p.exists() else "")



@app.patch("/api/projects/{pid}/notes")
def update_notes(pid: str, notes: str = Form("")):
    d = read_meta(pid)
    d["notes"] = notes
    d["updated_at"] = now()
    write_meta(pid, d)
    return d

@app.post("/api/projects/{pid}/cleanup-capture")
def cleanup_project_capture(pid: str):
    d = read_meta(pid)
    result = cleanup_capture(project_dir(pid))
    d["stage"] = result["message"]
    d["updated_at"] = now()
    d["cleanup"] = result
    write_meta(pid, d)
    return result

@app.post("/api/projects/{pid}/favorite")
def toggle_favorite(pid: str):
    d = read_meta(pid)
    d["favorite"] = not d.get("favorite", False)
    d["updated_at"] = now()
    write_meta(pid, d)
    return d

@app.post("/api/projects/{pid}/duplicate")
def duplicate_project(pid: str):
    src = project_dir(pid)
    if not src.exists():
        raise HTTPException(404, "Project not found.")
    new_id = str(uuid4())
    dst = project_dir(new_id)
    shutil.copytree(src, dst)
    d = json.loads((dst / "project.json").read_text())
    d["id"] = new_id
    d["name"] = d.get("name", "Splat") + " Copy"
    d["created_at"] = now()
    d["updated_at"] = now()
    d["favorite"] = False
    d["deleted"] = False
    write_meta(new_id, d)
    return d

@app.post("/api/projects/{pid}/soft-delete")
def soft_delete_project(pid: str):
    d = read_meta(pid)
    d["deleted"] = True
    d["updated_at"] = now()
    write_meta(pid, d)
    return {"ok": True}

@app.post("/api/projects/{pid}/restore")
def restore_project(pid: str):
    d = read_meta(pid)
    d["deleted"] = False
    d["updated_at"] = now()
    write_meta(pid, d)
    return d

@app.get("/api/deleted-projects")
def deleted_projects():
    out = []
    for p in sorted(PROJECTS.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        m = p / "project.json"
        if p.is_dir() and m.exists():
            d = json.loads(m.read_text())
            if d.get("deleted", False):
                d["artifacts"] = artifact_list(d["id"])
                out.append(d)
    return out

@app.post("/api/projects/{pid}/share-link")
def share_link(pid: str):
    d = read_meta(pid)
    d["share_link"] = f"http://localhost:8000/share/{pid}"
    d["updated_at"] = now()
    write_meta(pid, d)
    return {"share_link": d["share_link"], "note": "Local share link created. This works on your computer/network."}

@app.get("/api/phone")
def phone_upload_page():
    html = """
<!doctype html>
<html>
<head>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>Maker Splat Phone Upload</title>
<style>
body{font-family:system-ui;background:#17120d;color:#f8efe2;margin:0;padding:24px}
.card{max-width:680px;margin:auto;background:#211a13;border:1px solid #3b2e20;border-radius:24px;padding:24px}
input,button,select{font:inherit;padding:14px;border-radius:14px;border:0;margin:8px 0;width:100%}
button{background:#f2c46d;color:#18120c;font-weight:900}
.muted{color:#b9a78f}
</style>
</head>
<body><div class='card'>
<h1>Send capture to Maker Splat</h1>
<p class='muted'>Choose an existing project, then upload a phone video or photos.</p>
<select id='project'></select>
<input id='files' type='file' multiple accept='image/*,video/*'>
<button onclick='upload()'>Upload to Maker Splat</button>
<pre id='out'></pre>
<script>
async function loadProjects(){
 const res=await fetch('/api/projects'); const projects=await res.json();
 const sel=document.getElementById('project');
 sel.innerHTML=projects.map(p=>`<option value="${p.id}">${p.name}</option>`).join('');
}
async function upload(){
 const pid=document.getElementById('project').value;
 const files=document.getElementById('files').files;
 const body=new FormData();
 for(const f of files) body.append('files',f);
 const res=await fetch('/api/projects/'+pid+'/upload',{method:'POST',body});
 document.getElementById('out').textContent=res.ok?'Upload complete. Go back to your computer.':await res.text();
}
loadProjects();
</script>
</div></body></html>
"""
    return HTMLResponse(html)


@app.delete("/api/projects/{pid}")
def delete_project(pid: str):
    shutil.rmtree(project_dir(pid), ignore_errors=True)
    return {"ok": True}
