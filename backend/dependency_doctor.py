from pathlib import Path
import json
import shutil
import subprocess
import platform

REQUIRED_BASIC = ["ffmpeg"]
REQUIRED_REAL = ["ffmpeg", "colmap", "ns-process-data", "ns-train", "ns-export"]

def check_command(cmd):
    path = shutil.which(cmd)
    result = {"name": cmd, "found": bool(path), "path": path}
    if path:
        try:
            proc = subprocess.run([cmd, "--help"], capture_output=True, text=True, timeout=8)
            result["returncode"] = proc.returncode
            result["help_tail"] = (proc.stdout + proc.stderr)[-2000:]
        except Exception as exc:
            result["error"] = str(exc)
    return result

def dependency_report(root: Path | None = None):
    commands = {cmd: check_command(cmd) for cmd in sorted(set(REQUIRED_BASIC + REQUIRED_REAL + ["nvidia-smi"]))}
    basic_ready = all(commands[c]["found"] for c in REQUIRED_BASIC)
    real_ready = all(commands[c]["found"] for c in REQUIRED_REAL)
    gpu_ready = commands.get("nvidia-smi", {}).get("found", False)

    report = {
        "platform": platform.platform(),
        "basic_ready": basic_ready,
        "real_ready": real_ready,
        "gpu_ready": gpu_ready,
        "commands": commands,
        "install_guidance": install_guidance(commands),
    }

    if root:
        (root / "dependency_report.json").write_text(json.dumps(report, indent=2))
        write_markdown(root, report)
    return report

def install_guidance(commands):
    missing = [name for name, info in commands.items() if not info["found"] and name != "nvidia-smi"]
    guidance = []
    if "ffmpeg" in missing:
        guidance.append("Install FFmpeg or use the Docker image.")
    if "colmap" in missing:
        guidance.append("Install COLMAP for Real Mode camera tracking.")
    ns_missing = [m for m in missing if m.startswith("ns-")]
    if ns_missing:
        guidance.append("Install Nerfstudio in the backend environment for Real Mode.")
    if not commands.get("nvidia-smi", {}).get("found"):
        guidance.append("NVIDIA GPU/CUDA was not detected. Real Mode may be slow or unavailable.")
    if not guidance:
        guidance.append("All required Real Mode commands were found.")
    return guidance

def write_markdown(root: Path, report: dict):
    lines = [
        "# Maker Splat Dependency Doctor",
        "",
        f"Basic Mode ready: `{report['basic_ready']}`",
        f"Real Mode ready: `{report['real_ready']}`",
        f"GPU detected: `{report['gpu_ready']}`",
        "",
        "## Commands",
        "",
    ]
    for name, info in report["commands"].items():
        lines.append(f"- {'✓' if info['found'] else '⚠'} **{name}** — `{info.get('path') or 'not found'}`")
    lines += ["", "## Guidance", ""]
    lines += [f"- {g}" for g in report["install_guidance"]]
    (root / "DEPENDENCY_DOCTOR.md").write_text("\n".join(lines))
