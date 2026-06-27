import os
import shutil
import subprocess

REAL_MODE = os.getenv("MAKER_SPLAT_REAL_MODE", "0") == "1"

def tool_status(command: str):
    path = shutil.which(command)
    return {"found": bool(path), "path": path}

def gpu_status():
    nvidia = shutil.which("nvidia-smi")
    if not nvidia:
        return {"found": False, "message": "nvidia-smi not found"}
    try:
        out = subprocess.check_output([nvidia, "--query-gpu=name,memory.total", "--format=csv,noheader"], text=True, timeout=5)
        return {"found": True, "message": out.strip()}
    except Exception as exc:
        return {"found": False, "message": str(exc)}

def real_mode_preflight():
    tools = {
        "ffmpeg": tool_status("ffmpeg"),
        "colmap": tool_status("colmap"),
        "ns-process-data": tool_status("ns-process-data"),
        "ns-train": tool_status("ns-train"),
        "ns-export": tool_status("ns-export"),
    }
    gpu = gpu_status()
    missing = [name for name, info in tools.items() if not info["found"]]
    ok = not missing and gpu["found"]
    return {
        "real_mode": REAL_MODE,
        "ok": ok,
        "tools": tools,
        "gpu": gpu,
        "missing": missing,
        "message": "Real mode is ready." if ok else "Real mode is not ready yet.",
    }
