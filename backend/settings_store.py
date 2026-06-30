from pathlib import Path
import json

SETTINGS_PATH = Path("projects") / "settings.json"

DEFAULT_SETTINGS = {
    "appearance": "dark",
    "performance": "balanced",
    "viewer_auto_rotate": True,
    "viewer_point_size": 0.012,
    "reduced_motion": False,
    "high_contrast": False,
    "default_preset": "balanced",
    "engine": "demo",
    "phone_upload_enabled": True,
    "show_advanced_details": False
}

def load_settings():
    SETTINGS_PATH.parent.mkdir(exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text())
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    save_settings(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)

def save_settings(data):
    SETTINGS_PATH.parent.mkdir(exist_ok=True)
    merged = {**DEFAULT_SETTINGS, **data}
    SETTINGS_PATH.write_text(json.dumps(merged, indent=2))
    return merged
