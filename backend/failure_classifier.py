from pathlib import Path
import json

PATTERNS = [
    ("missing_tool", ["not found", "no such file or directory", "nerfstudio tools missing"]),
    ("bad_capture", ["not enough matches", "no good initial image pair", "failed to reconstruct", "need at least 3"]),
    ("colmap_failed", ["colmap", "mapper", "feature_extractor", "exhaustive_matcher"]),
    ("training_failed", ["ns-train", "cuda out of memory", "out of memory", "runtimeerror", "splatfacto"]),
    ("export_failed", ["ns-export", "export", "no .ply or .splat", "no splat"]),
    ("gpu_failed", ["nvidia", "cuda", "gpu", "driver"]),
]

def classify_failure(root: Path) -> dict:
    text = ""
    for name in ["log.txt", "REAL_MODE_REPORT.md", "VALIDATION_REPORT.md"]:
        p = root / name
        if p.exists():
            text += "\n" + p.read_text(errors="replace")[-20000:]
    lowered = text.lower()
    matches = []
    for category, needles in PATTERNS:
        hit = [n for n in needles if n in lowered]
        if hit:
            matches.append({"category": category, "signals": hit})
    category = matches[0]["category"] if matches else "unknown"
    result = {"category": category, "matches": matches, "recommendation": recommendation_for(category)}
    (root / "failure_classification.json").write_text(json.dumps(result, indent=2))
    write_failure_markdown(root, result)
    return result

def recommendation_for(category):
    return {
        "missing_tool": "Install the missing command inside the backend environment, then rerun the dataset.",
        "bad_capture": "Use a known-good dataset with more overlap, sharper photos, and full object coverage.",
        "colmap_failed": "Check capture overlap and COLMAP availability. Try 40–80 sharp photos before video.",
        "training_failed": "Check GPU/CUDA memory and Nerfstudio logs. Try the Quick preset first.",
        "export_failed": "Training may have completed but export failed. Check ns-export help and export attempts.",
        "gpu_failed": "Check NVIDIA driver, CUDA, Docker GPU passthrough, and nvidia-smi inside the backend container.",
    }.get(category, "Inspect log.txt and pipeline_state.json manually.")

def write_failure_markdown(root: Path, result: dict):
    lines = ["# Maker Splat Failure Classification", "", f"Category: `{result['category']}`", "", f"Recommendation: {result['recommendation']}", "", "## Signals", ""]
    for match in result.get("matches", []):
        lines.append(f"- **{match['category']}**: {', '.join(match['signals'])}")
    if not result.get("matches"):
        lines.append("- none")
    (root / "FAILURE_CLASSIFICATION.md").write_text("\n".join(lines))
