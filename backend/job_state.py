from pathlib import Path
import json
import time

def write_job_state(root: Path, job_id: str, status: str, stage: str, progress: int, message: str = ""):
    state = {
        "job_id": job_id,
        "status": status,
        "stage": stage,
        "progress": progress,
        "message": message,
        "updated_at": int(time.time()),
    }
    (root / "job_state.json").write_text(json.dumps(state, indent=2))
    return state

def read_job_state(root: Path):
    path = root / "job_state.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None
