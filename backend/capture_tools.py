from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import shutil

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

def cleanup_capture(root: Path) -> dict:
    """Simple maker-friendly cleanup: center-crop very wide images, normalize contrast, save cleaned copies."""
    capture = root / "capture"
    cleaned = root / "capture_cleaned"
    shutil.rmtree(cleaned, ignore_errors=True)
    cleaned.mkdir(parents=True, exist_ok=True)

    count = 0
    skipped = 0
    for path in sorted(capture.iterdir()):
        if path.suffix.lower() not in IMAGE_EXTS:
            skipped += 1
            continue
        try:
            img = Image.open(path).convert("RGB")
            img = crop_reasonably(img)
            img = ImageOps.autocontrast(img, cutoff=1)
            img = ImageEnhance.Sharpness(img).enhance(1.08)
            img.save(cleaned / path.name, quality=92)
            count += 1
        except Exception:
            skipped += 1

    if count:
        backup = root / "capture_original"
        if not backup.exists():
            shutil.copytree(capture, backup)
        shutil.rmtree(capture, ignore_errors=True)
        shutil.copytree(cleaned, capture)

    return {
        "cleaned": count,
        "skipped": skipped,
        "message": "Cleaned photo capture is ready." if count else "No photos were cleaned. Videos are cleaned after frame extraction."
    }

def crop_reasonably(img: Image.Image) -> Image.Image:
    w, h = img.size
    ratio = w / max(h, 1)
    if ratio > 2.0:
        new_w = int(h * 1.6)
        left = max(0, (w - new_w) // 2)
        return img.crop((left, 0, left + new_w, h))
    if ratio < 0.5:
        new_h = int(w * 1.6)
        top = max(0, (h - new_h) // 2)
        return img.crop((0, top, w, top + new_h))
    return img
