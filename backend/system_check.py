import os, shutil, subprocess
REAL_MODE = os.getenv("MAKER_SPLAT_REAL_MODE","0") == "1"
ENGINE = os.getenv("MAKER_SPLAT_ENGINE", "nerfstudio" if REAL_MODE else "demo")

def which(cmd):
    p = shutil.which(cmd)
    return {"found": bool(p), "path": p}

def gpu():
    p = shutil.which("nvidia-smi")
    if not p: return {"found": False, "message": "nvidia-smi not found"}
    try:
        out = subprocess.check_output([p,"--query-gpu=name,memory.total","--format=csv,noheader"], text=True, timeout=5)
        return {"found": True, "message": out.strip()}
    except Exception as e:
        return {"found": False, "message": str(e)}

def check_system():
    tools = {name: which(name) for name in ["ffmpeg","colmap","ns-process-data","ns-train","ns-export"]}
    missing = [k for k,v in tools.items() if not v["found"]]
    g = gpu()
    return {"real_mode":REAL_MODE,"engine":ENGINE,"demo_ready":tools["ffmpeg"]["found"],"real_ready":not missing and g["found"],"tools":tools,"gpu":g,"missing_real_tools":missing}
