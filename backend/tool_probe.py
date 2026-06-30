import shutil
import subprocess
import re

def command_exists(command: str) -> bool:
    return shutil.which(command) is not None

def run_help(command: list[str], timeout: int = 10):
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": proc.returncode in {0, 1, 2},
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
            "text": (proc.stdout + "\n" + proc.stderr)[-12000:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "text": ""}

def probe_nerfstudio():
    data = {
        "ns_process_data": probe_command("ns-process-data"),
        "ns_train": probe_command("ns-train"),
        "ns_export": probe_command("ns-export"),
        "export_help": run_help(["ns-export", "--help"]) if command_exists("ns-export") else {"ok": False, "text": ""},
        "gaussian_splat_help": run_help(["ns-export", "gaussian-splat", "--help"]) if command_exists("ns-export") else {"ok": False, "text": ""},
    }
    data["capabilities"] = infer_export_capabilities(data)
    return data

def probe_command(command):
    path = shutil.which(command)
    result = {"found": bool(path), "path": path}
    if path:
        result["help"] = run_help([command, "--help"])
    return result

def infer_export_capabilities(probe):
    text = (probe.get("gaussian_splat_help", {}).get("text") or "") + "\n" + (probe.get("export_help", {}).get("text") or "")
    return {
        "has_gaussian_splat_subcommand": "gaussian-splat" in text or "gaussian splat" in text.lower(),
        "supports_output_dir": "--output-dir" in text,
        "supports_output_filename": "--output-filename" in text,
        "supports_load_config": "--load-config" in text,
        "mentions_ply": ".ply" in text or "ply" in text.lower(),
        "mentions_splat": ".splat" in text or "splat" in text.lower(),
    }
