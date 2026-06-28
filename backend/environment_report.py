from pathlib import Path
import subprocess, platform, sys, json, shutil

COMMANDS = {
    "ffmpeg": ["ffmpeg", "-version"],
    "colmap": ["colmap", "-h"],
    "ns-process-data": ["ns-process-data", "--help"],
    "ns-train": ["ns-train", "--help"],
    "ns-export": ["ns-export", "--help"],
    "nvidia-smi": ["nvidia-smi"],
}

def run_probe(command, timeout=10):
    path = shutil.which(command[0])
    result = {"command": command, "found": bool(path), "path": path}
    if not path:
        return result
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        result.update({"returncode": proc.returncode, "stdout": proc.stdout[-6000:], "stderr": proc.stderr[-6000:]})
    except Exception as exc:
        result["error"] = str(exc)
    return result

def collect_environment(root: Path | None = None) -> dict:
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "commands": {name: run_probe(cmd) for name, cmd in COMMANDS.items()},
    }
    report["nerfstudio_compatibility"] = build_compatibility(report)
    if root:
        (root / "environment_report.json").write_text(json.dumps(report, indent=2))
        write_environment_markdown(root, report)
        (root / "NERFSTUDIO_COMPATIBILITY.json").write_text(json.dumps(report["nerfstudio_compatibility"], indent=2))
    return report

def build_compatibility(report: dict) -> dict:
    ns_export = report["commands"].get("ns-export", {})
    text = (ns_export.get("stdout", "") + "\n" + ns_export.get("stderr", "")).lower()
    return {
        "ns_export_found": ns_export.get("found", False),
        "mentions_gaussian_splat": "gaussian" in text and "splat" in text,
        "mentions_output_dir": "--output-dir" in text,
        "mentions_load_config": "--load-config" in text,
        "raw_help_available": bool(text.strip()),
    }

def write_environment_markdown(root: Path, report: dict):
    lines = [
        "# Maker Splat Environment Report",
        "",
        f"Platform: `{report['platform']}`",
        f"Python: `{report['python'].split()[0]}`",
        f"Machine: `{report['machine']}`",
        "",
        "## Commands",
        "",
    ]
    for name, data in report["commands"].items():
        mark = "✓" if data.get("found") else "⚠"
        lines.append(f"- {mark} **{name}** — `{data.get('path') or 'not found'}`")
    lines += ["", "## Nerfstudio Compatibility", "", "```json", json.dumps(report["nerfstudio_compatibility"], indent=2), "```"]
    (root / "ENVIRONMENT_REPORT.md").write_text("\n".join(lines))
