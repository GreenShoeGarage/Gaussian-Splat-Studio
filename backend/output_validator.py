from pathlib import Path
import json

MIN_SPLAT_BYTES = 1024
MIN_PLY_BYTES = 256

def validate_project_output(root: Path) -> dict:
    splat = validate_splat(root / "scene.splat")
    ply = validate_ply(root / "scene.ply")
    pipeline = validate_pipeline(root)

    verified = splat["ok"] or ply["ok"]
    real_splat_verified = splat["ok"]

    result = {
        "verified": verified,
        "real_splat_verified": real_splat_verified,
        "splat": splat,
        "ply": ply,
        "pipeline": pipeline,
        "status": "real_splat_verified" if real_splat_verified else "ply_only_verified" if ply["ok"] else "not_verified",
    }
    (root / "validation_manifest.json").write_text(json.dumps(result, indent=2))
    write_validation_report(root, result)
    return result

def validate_splat(path: Path) -> dict:
    result = {"path": str(path), "exists": path.exists(), "ok": False, "checks": []}
    if not path.exists():
        result["checks"].append({"name": "exists", "ok": False, "message": "scene.splat missing"})
        return result

    size = path.stat().st_size
    result["size_bytes"] = size
    result["checks"].append({"name": "non_empty", "ok": size > 0, "message": f"{size} bytes"})
    result["checks"].append({"name": "plausible_size", "ok": size >= MIN_SPLAT_BYTES, "message": f"minimum {MIN_SPLAT_BYTES} bytes"})

    sample = path.read_bytes()[:512]
    looks_like_html = sample.lstrip().lower().startswith(b"<html") or b"traceback" in sample.lower()
    result["checks"].append({"name": "not_text_error", "ok": not looks_like_html, "message": "not obvious HTML/traceback output"})

    # Many splat formats are binary, but exact header varies. This is a sanity check, not a formal spec.
    binaryish = any(b < 9 or b > 126 for b in sample[:128]) if sample else False
    result["checks"].append({"name": "binary_or_structured", "ok": binaryish or size > 4096, "message": "appears binary or sufficiently large"})

    result["ok"] = all(c["ok"] for c in result["checks"])
    return result

def validate_ply(path: Path) -> dict:
    result = {"path": str(path), "exists": path.exists(), "ok": False, "checks": []}
    if not path.exists():
        result["checks"].append({"name": "exists", "ok": False, "message": "scene.ply missing"})
        return result

    size = path.stat().st_size
    result["size_bytes"] = size
    result["checks"].append({"name": "plausible_size", "ok": size >= MIN_PLY_BYTES, "message": f"{size} bytes"})

    head = path.read_bytes()[:2048]
    text = head.decode("utf-8", errors="ignore").lower()
    result["checks"].append({"name": "ply_header", "ok": text.startswith("ply"), "message": "starts with ply"})
    result["checks"].append({"name": "vertex_element", "ok": "element vertex" in text, "message": "contains vertex declaration"})
    result["checks"].append({"name": "end_header", "ok": "end_header" in text, "message": "contains end_header"})

    result["ok"] = all(c["ok"] for c in result["checks"])
    return result

def validate_pipeline(root: Path) -> dict:
    state_path = root / "pipeline_state.json"
    result = {"exists": state_path.exists(), "checks": [], "ok": False}
    if not state_path.exists():
        result["checks"].append({"name": "pipeline_state", "ok": False, "message": "pipeline_state.json missing"})
        return result

    try:
        state = json.loads(state_path.read_text())
    except Exception as exc:
        result["checks"].append({"name": "pipeline_state_parse", "ok": False, "message": str(exc)})
        return result

    stages = state.get("stages", [])
    names = [s.get("name") for s in stages]
    result["checks"].append({"name": "has_stages", "ok": len(stages) > 0, "message": f"{len(stages)} stages recorded"})
    result["checks"].append({"name": "export_attempted", "ok": bool(state.get("export_attempts")), "message": f"{len(state.get('export_attempts', []))} export attempts"})
    result["checks"].append({"name": "train_stage_seen", "ok": "ns-train" in names or any("train" in str(n) for n in names), "message": "training stage recorded"})

    result["ok"] = all(c["ok"] for c in result["checks"])
    return result

def write_validation_report(root: Path, result: dict):
    lines = [
        "# Maker Splat Validation Report",
        "",
        f"Status: `{result['status']}`",
        f"Verified output: `{result['verified']}`",
        f"Real SPLAT verified: `{result['real_splat_verified']}`",
        "",
        "## scene.splat",
        "",
    ]

    for check in result["splat"].get("checks", []):
        lines.append(f"- {'✓' if check['ok'] else '⚠'} **{check['name']}** — {check['message']}")

    lines += ["", "## scene.ply", ""]
    for check in result["ply"].get("checks", []):
        lines.append(f"- {'✓' if check['ok'] else '⚠'} **{check['name']}** — {check['message']}")

    lines += ["", "## Pipeline", ""]
    for check in result["pipeline"].get("checks", []):
        lines.append(f"- {'✓' if check['ok'] else '⚠'} **{check['name']}** — {check['message']}")

    if not result["real_splat_verified"]:
        lines += [
            "",
            "## Next action",
            "",
            "A verified `.splat` was not found. Inspect `REAL_MODE_REPORT.md`, `pipeline_state.json`, and `log.txt`.",
        ]

    (root / "VALIDATION_REPORT.md").write_text("\n".join(lines))
