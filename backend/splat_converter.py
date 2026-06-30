from pathlib import Path
import shutil
import subprocess

def find_converter():
    """Find optional external PLY->SPLAT converter.

    Maker Splat does not pretend every PLY can become a valid Gaussian splat.
    If a converter is installed, this function can use it. Otherwise it reports
    that conversion is unavailable.
    """
    for cmd in ["ply-to-splat", "ply2splat", "splat-transform"]:
        path = shutil.which(cmd)
        if path:
            return path
    return None

def try_convert_ply_to_splat(root: Path, ply_path: Path, splat_path: Path):
    converter = find_converter()
    result = {
        "attempted": False,
        "ok": False,
        "converter": converter,
        "message": ""
    }

    if not converter:
        result["message"] = "No external PLY-to-SPLAT converter found."
        return result

    result["attempted"] = True
    try:
        proc = subprocess.run(
            [converter, str(ply_path), str(splat_path)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout[-4000:]
        result["stderr"] = proc.stderr[-4000:]
        result["ok"] = proc.returncode == 0 and splat_path.exists()
        result["message"] = "Conversion succeeded." if result["ok"] else "Conversion failed."
    except Exception as exc:
        result["message"] = str(exc)
    return result
