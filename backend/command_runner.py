from pathlib import Path
import subprocess
import time
import json
import os
import signal

class CommandError(RuntimeError):
    def __init__(self, command, returncode, stdout, stderr):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"Command failed ({returncode}): {' '.join(command)}")

def append_log(root: Path, message: str):
    with (root / "log.txt").open("a", encoding="utf-8") as f:
        f.write(message + "\n")

def run_logged(root: Path, command: list[str], stage: str, timeout: int | None = None):
    started = time.time()
    append_log(root, "")
    append_log(root, "=" * 80)
    append_log(root, f"STAGE: {stage}")
    append_log(root, "$ " + " ".join(command))
    append_log(root, "=" * 80)

    proc = subprocess.Popen(
        command,
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = proc.communicate(timeout=10)
        except Exception:
            proc.kill()
            stdout, stderr = proc.communicate()
        append_log(root, f"TIMEOUT after {timeout} seconds")
        append_log(root, "--- STDOUT ---")
        append_log(root, stdout or "")
        append_log(root, "--- STDERR ---")
        append_log(root, stderr or "")
        raise CommandError(command, -999, stdout or "", stderr or "Timed out")

    duration = time.time() - started
    append_log(root, f"Exit code: {proc.returncode}")
    append_log(root, f"Duration: {duration:.1f}s")
    append_log(root, "--- STDOUT ---")
    append_log(root, stdout or "")
    append_log(root, "--- STDERR ---")
    append_log(root, stderr or "")

    result = {
        "stage": stage,
        "command": command,
        "returncode": proc.returncode,
        "duration_seconds": round(duration, 2),
        "stdout_tail": tail(stdout),
        "stderr_tail": tail(stderr),
    }

    if proc.returncode != 0:
        raise CommandError(command, proc.returncode, stdout or "", stderr or "")

    return result

def tail(text: str | None, lines: int = 40):
    if not text:
        return ""
    parts = text.splitlines()
    return "\n".join(parts[-lines:])
