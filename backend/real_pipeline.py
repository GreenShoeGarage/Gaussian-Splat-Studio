from pathlib import Path
import json
import shutil
from command_runner import append_log

def write_state(root: Path, state: dict):
    (root / "pipeline_state.json").write_text(json.dumps(state, indent=2))

def load_state(root: Path) -> dict:
    path = root / "pipeline_state.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"stages": [], "artifacts": [], "errors": [], "export_attempts": []}

def record_stage(root: Path, name: str, status: str, data: dict | None = None):
    state = load_state(root)
    state["stages"].append({"name": name, "status": status, "data": data or {}})
    write_state(root, state)

def record_export_attempt(root: Path, strategy: str, status: str, data: dict | None = None):
    state = load_state(root)
    state.setdefault("export_attempts", []).append({"strategy": strategy, "status": status, "data": data or {}})
    write_state(root, state)

def discover_config(ns_runs: Path):
    configs = sorted(ns_runs.rglob("config.yml"), key=lambda p: p.stat().st_mtime, reverse=True)
    return configs[0] if configs else None

def discover_transforms(ns_data: Path):
    transforms = sorted(ns_data.rglob("transforms.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return transforms[0] if transforms else None

def discover_artifacts(*roots: Path):
    found = {"ply": [], "splat": [], "ckpt": [], "config": [], "other": []}
    seen = set()
    for root in roots:
        if not root or not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            suffix = p.suffix.lower()
            name = p.name.lower()
            if suffix == ".ply":
                found["ply"].append(str(p))
            elif suffix == ".splat":
                found["splat"].append(str(p))
            elif suffix in {".ckpt", ".pth", ".pt"}:
                found["ckpt"].append(str(p))
            elif name == "config.yml" or suffix in {".yaml", ".yml"}:
                found["config"].append(str(p))
            elif suffix in {".json", ".txt", ".log"}:
                found["other"].append(str(p))
    for k in found:
        found[k] = sorted(found[k], key=lambda x: Path(x).stat().st_mtime if Path(x).exists() else 0, reverse=True)
    return found

def copy_best_artifacts(root: Path, artifacts: dict):
    copied = []
    if artifacts.get("ply"):
        src = Path(artifacts["ply"][0])
        shutil.copyfile(src, root / "scene.ply")
        copied.append("ply")
    if artifacts.get("splat"):
        src = Path(artifacts["splat"][0])
        shutil.copyfile(src, root / "scene.splat")
        copied.append("splat")
    return copied

def write_real_mode_report(root: Path, engine_id: str, preflight: dict, artifacts: dict | None = None):
    state = load_state(root)
    lines = [
        "# Maker Splat Real Mode Report",
        "",
        f"Engine: `{engine_id}`",
        "",
        "## Output Status",
        "",
        f"- scene.splat: `{'yes' if (root/'scene.splat').exists() else 'no'}`",
        f"- scene.ply: `{'yes' if (root/'scene.ply').exists() else 'no'}`",
        "",
        "## Preflight",
        "",
        f"Overall ready: `{preflight.get('ok')}`",
        "",
    ]

    for check in preflight.get("checks", []):
        mark = "✓" if check.get("ok") else "⚠"
        lines.append(f"- {mark} **{check.get('name')}** — {check.get('help')}")

    lines += ["", "## Pipeline Stages", ""]
    for stage in state.get("stages", []):
        lines.append(f"- **{stage.get('name')}** — `{stage.get('status')}`")

    lines += ["", "## Export Attempts", ""]
    attempts = state.get("export_attempts", [])
    if attempts:
        for attempt in attempts:
            lines.append(f"- **{attempt.get('strategy')}** — `{attempt.get('status')}`")
    else:
        lines.append("- none recorded")

    if artifacts:
        lines += ["", "## Discovered Artifacts", "", "### SPLAT"]
        lines += [f"- `{p}`" for p in artifacts.get("splat", [])] or ["- none"]
        lines += ["", "### PLY"]
        lines += [f"- `{p}`" for p in artifacts.get("ply", [])] or ["- none"]
        lines += ["", "### Configs"]
        lines += [f"- `{p}`" for p in artifacts.get("config", [])] or ["- none"]
        lines += ["", "### Checkpoints"]
        lines += [f"- `{p}`" for p in artifacts.get("ckpt", [])] or ["- none"]

    if not (root / "scene.splat").exists():
        lines += [
            "",
            "## Why `.splat` may be missing",
            "",
            "- Nerfstudio version may export `.ply` only.",
            "- `ns-export gaussian-splat` may have different CLI flags.",
            "- Training may have completed but export failed.",
            "- External PLY-to-SPLAT converter may not be installed.",
            "",
            "Check `pipeline_state.json` and `log.txt` for exact command output.",
        ]

    lines += [
        "",
        "## Files to inspect",
        "",
        "- `log.txt`",
        "- `diagnostics.json`",
        "- `pipeline_state.json`",
        "- `REAL_MODE_REPORT.md`",
    ]

    (root / "REAL_MODE_REPORT.md").write_text("\n".join(lines))
