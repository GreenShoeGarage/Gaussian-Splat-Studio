from pathlib import Path
import os
from .base import ReconstructionEngine
from system_check import check_system
from command_runner import run_logged, CommandError, append_log
from real_pipeline import (
    record_stage,
    record_export_attempt,
    discover_config,
    discover_transforms,
    discover_artifacts,
    copy_best_artifacts,
    write_real_mode_report,
)
from splat_converter import try_convert_ply_to_splat
from tool_probe import probe_nerfstudio
from output_validator import validate_project_output

class NerfstudioEngine(ReconstructionEngine):
    id = "nerfstudio"
    name = "Nerfstudio Engine"
    description = "Runs Nerfstudio/COLMAP to create real Gaussian splats."

    def preflight(self) -> dict:
        system = check_system()
        required = ["ffmpeg", "colmap", "ns-process-data", "ns-train", "ns-export"]
        checks = []
        for name in required:
            info = system["tools"].get(name, {"found": False, "path": None})
            checks.append({"name": name, "ok": bool(info.get("found")), "help": info.get("path") or f"{name} not found"})

        gpu = system.get("gpu", {})
        checks.append({"name": "NVIDIA GPU", "ok": bool(gpu.get("found")), "help": gpu.get("message", "nvidia-smi not found. CPU may work but will be slow or unsupported.")})
        missing = [c["name"] for c in checks if not c["ok"] and c["name"] != "NVIDIA GPU"]
        return {"ok": len(missing) == 0, "engine": self.id, "name": self.name, "checks": checks, "missing": missing, "gpu": gpu, "candidate": "v4.0", "probe": probe_nerfstudio()}

    def run(self, root: Path, frame_files, update, preset):
        preflight = self.preflight()
        write_real_mode_report(root, self.id, preflight)
        if preflight["missing"]:
            record_stage(root, "preflight", "failed", preflight)
            write_real_mode_report(root, self.id, preflight)
            raise RuntimeError("Nerfstudio tools missing: " + ", ".join(preflight["missing"]))

        outputs = root / "outputs"
        ns_data = outputs / "nerfstudio-data"
        ns_runs = outputs / "nerfstudio-runs"
        ns_export = outputs / "nerfstudio-export"
        ns_export_alt = outputs / "nerfstudio-export-alt"
        for p in [ns_data, ns_runs, ns_export, ns_export_alt]:
            p.mkdir(parents=True, exist_ok=True)

        timeout = int(os.getenv("MAKER_SPLAT_COMMAND_TIMEOUT", "0")) or None

        try:
            update(30, "Preparing real dataset", "Nerfstudio is organizing your frames")
            record_stage(root, "ns-process-data", "started")
            result = run_logged(root, ["ns-process-data", "images", "--data", str(root / "frames"), "--output-dir", str(ns_data)], "ns-process-data", timeout=timeout)
            transforms = discover_transforms(ns_data)
            record_stage(root, "ns-process-data", "done", {"command": result, "transforms_json": str(transforms) if transforms else None})
            if not transforms:
                raise RuntimeError("Nerfstudio process-data finished, but transforms.json was not found.")

            update(58, "Training real Gaussian splat", "This can take a while")
            record_stage(root, "ns-train", "started")
            result = run_logged(root, ["ns-train", "splatfacto", "--data", str(ns_data), "--output-dir", str(ns_runs), "--max-num-iterations", str(preset["iterations"])], "ns-train splatfacto", timeout=timeout)
            config = discover_config(ns_runs)
            record_stage(root, "ns-train", "done", {"command": result, "config_yml": str(config) if config else None})
            if not config:
                raise RuntimeError("Nerfstudio training finished but no config.yml was found.")

            update(84, "Exporting real splat", "Trying Nerfstudio export strategies")
            copied = self.export_with_strategies(root, config, ns_export, ns_export_alt, timeout)
            all_artifacts = discover_artifacts(ns_export, ns_export_alt, ns_runs, outputs, root)
            copied = list(set(copied + copy_best_artifacts(root, all_artifacts)))

            # Fallback: if only PLY exists, try optional converter.
            if "splat" not in copied and (root / "scene.ply").exists():
                conversion = try_convert_ply_to_splat(root, root / "scene.ply", root / "scene.splat")
                record_export_attempt(root, "optional-ply-to-splat-converter", "done" if conversion.get("ok") else "unavailable-or-failed", conversion)
                if conversion.get("ok"):
                    copied.append("splat")

            write_real_mode_report(root, self.id, preflight, all_artifacts)
            validation = validate_project_output(root)
            record_stage(root, "output-validation", "done", validation)

            if not copied:
                raise RuntimeError("Nerfstudio export finished, but no .ply or .splat was found.")

            if not validation.get("real_splat_verified"):
                append_log(root, "WARNING: Real pipeline did not produce a verified scene.splat.")
                record_stage(root, "splat-validation", "missing-or-invalid", validation.get("splat"))
            else:
                record_stage(root, "splat-validation", "verified", validation.get("splat"))

            return sorted(set(copied))

        except CommandError as exc:
            record_stage(root, "command-failed", "failed", {"command": exc.command, "returncode": exc.returncode, "stdout_tail": exc.stdout[-4000:], "stderr_tail": exc.stderr[-4000:]})
            write_real_mode_report(root, self.id, preflight)
            raise
        except Exception as exc:
            record_stage(root, "pipeline-error", "failed", {"error": str(exc)})
            write_real_mode_report(root, self.id, preflight)
            raise

    def export_with_strategies(self, root: Path, config: Path, ns_export: Path, ns_export_alt: Path, timeout):
        probe = probe_nerfstudio()
        caps = probe.get("capabilities", {})

        strategies = []

        # Standard modern Nerfstudio export path.
        strategies.append({
            "name": "ns-export gaussian-splat standard",
            "command": ["ns-export", "gaussian-splat", "--load-config", str(config), "--output-dir", str(ns_export)]
        })

        # Some versions expose output filename; only try when help suggests support.
        if caps.get("supports_output_filename"):
            strategies.append({
                "name": "ns-export gaussian-splat output-filename",
                "command": ["ns-export", "gaussian-splat", "--load-config", str(config), "--output-dir", str(ns_export_alt), "--output-filename", "scene.splat"]
            })

        # Last resort: some CLIs accept output-dir but reject extra filename flags.
        strategies.append({
            "name": "ns-export gaussian-splat alternate-dir",
            "command": ["ns-export", "gaussian-splat", "--load-config", str(config), "--output-dir", str(ns_export_alt)]
        })

        copied = []
        for strategy in strategies:
            try:
                record_export_attempt(root, strategy["name"], "started", {"command": strategy["command"], "capabilities": caps})
                result = run_logged(root, strategy["command"], strategy["name"], timeout=timeout)
                artifacts = discover_artifacts(ns_export, ns_export_alt, root / "outputs", root)
                now_copied = copy_best_artifacts(root, artifacts)
                copied.extend(now_copied)
                record_export_attempt(root, strategy["name"], "done", {"command": result, "copied": now_copied, "artifacts": artifacts})
                if "splat" in copied:
                    return sorted(set(copied))
            except Exception as exc:
                record_export_attempt(root, strategy["name"], "failed", {"error": str(exc)})
                append_log(root, f"Export strategy failed: {strategy['name']} — {exc}")
        return sorted(set(copied))
