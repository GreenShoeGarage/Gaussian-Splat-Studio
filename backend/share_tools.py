from pathlib import Path
import json
import zipfile
import shutil

def project_manifest(root: Path, public_url: str | None = None) -> dict:
    meta_path = root / "project.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    artifacts = []
    for name in ["scene.ply", "scene.splat", "thumbnail.jpg", "log.txt", "project.json"]:
        if (root / name).exists():
            artifacts.append(name)
    return {
        "app": "Maker Splat",
        "schema": "maker-splat-project-v2",
        "project": {
            "id": meta.get("id"),
            "name": meta.get("name"),
            "preset": meta.get("preset"),
            "status": meta.get("status"),
            "favorite": meta.get("favorite", False),
            "notes": meta.get("notes", ""),
        },
        "artifacts": artifacts,
        "public_url": public_url,
    }

def write_share_viewer(root: Path, project_id: str, project_name: str):
    html = f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{project_name} - Maker Splat</title>
<style>
body{{margin:0;background:#17120d;color:#f8efe2;font-family:system-ui}}
header{{padding:18px 22px;background:#211a13;border-bottom:1px solid #3b2e20}}
main{{padding:24px;max-width:900px;margin:auto}}
.card{{background:#211a13;border:1px solid #3b2e20;border-radius:24px;padding:24px;margin:18px 0}}
a{{color:#f2c46d}}
img{{max-width:100%;border-radius:18px}}
</style>
</head>
<body>
<header><strong>Maker Splat Share</strong></header>
<main>
<div class='card'>
<h1>{project_name}</h1>
<p>This is a local Maker Splat share package.</p>
<p>Open the included <code>scene.ply</code> or <code>scene.splat</code> in Maker Splat, SuperSplat, PlayCanvas, Blender, or another compatible viewer.</p>
</div>
<div class='card'>
<h2>Files</h2>
<ul>
<li><a href='scene.ply'>scene.ply</a></li>
<li><a href='scene.splat'>scene.splat</a></li>
<li><a href='project.json'>project.json</a></li>
</ul>
</div>
</main>
</body>
</html>"""
    (root / "share.html").write_text(html)

def make_share_package(root: Path, project_id: str, project_name: str):
    write_share_viewer(root, project_id, project_name)
    manifest = project_manifest(root)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2))
    out = root / "maker-splat-share.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ["share.html", "manifest.json", "scene.ply", "scene.splat", "thumbnail.jpg", "project.json", "log.txt"]:
            p = root / name
            if p.exists():
                z.write(p, name)
    return out

def import_project_zip(projects_root: Path, uploaded_zip: Path, new_id: str):
    target = projects_root / new_id
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(uploaded_zip, "r") as z:
        z.extractall(target)
    meta_path = target / "project.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    else:
        meta = {"name": "Imported Splat", "preset": "balanced"}
    meta["id"] = new_id
    meta["status"] = "done" if (target/"scene.ply").exists() or (target/"scene.splat").exists() else "imported"
    meta["stage"] = "Imported"
    meta["deleted"] = False
    meta["favorite"] = False
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta
