from pathlib import Path
from PIL import Image
import numpy as np

MODE_ADVICE = {
    "object": "For objects, capture all sides and a few higher angles.",
    "room": "For rooms, move slowly and capture corners.",
    "outdoor": "For outdoor captures, soft light and static scenes work best.",
    "turntable": "For turntables, keep the camera fixed and rotate slowly."
}

def analyze_capture(root: Path, mode: str = "object") -> dict:
    capture = root / "capture"
    files = sorted(capture.glob("*"))
    videos = [p for p in files if p.suffix.lower() in {".mp4",".mov",".m4v",".webm"}]
    images = [p for p in files if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}]
    warnings, tips = [], [MODE_ADVICE.get(mode, MODE_ADVICE["object"])]
    if videos:
        count_label, score = f"{len(videos)} video", 76
        tips.append("Move slowly and keep the subject centered.")
    else:
        count_label, score = f"{len(images)} photos", min(95,45+len(images)*2)
        if len(images) < 20: warnings.append("More photos usually make a better splat. Aim for 30–150.")
    blur = estimate_blur(images[:30]); dup = duplicate_score(images[:40])
    if blur is not None and blur < 18: warnings.append("Some images may be blurry or low texture."); score -= 15
    if dup is not None and dup > .65: warnings.append("Many frames look nearly identical."); score -= 10
    score = max(10, min(100, score))
    return {"score":score,"label":"Looks great" if score>=85 else "Should work" if score>=65 else "Try improving capture","count":count_label,"mode":mode,"warnings":warnings,"tips":tips,"metrics":{"sharpness":metric_from_blur(blur),"coverage":min(100,score+5),"overlap":min(100,score+3),"variety":int(max(0,min(100,100-(dup or 0)*100)))}}

def estimate_blur(paths):
    vals=[]
    for path in paths:
        try:
            img=Image.open(path).convert("L"); img.thumbnail((320,320)); arr=np.asarray(img,dtype=np.float32)
            vals.append(float(np.diff(arr,axis=0).var()+np.diff(arr,axis=1).var()))
        except Exception: pass
    return float(np.median(vals)) if vals else None

def duplicate_score(paths):
    thumbs=[]
    for path in paths:
        try:
            img=Image.open(path).convert("L"); img.thumbnail((32,32)); arr=np.asarray(img,dtype=np.float32).flatten()
            if arr.std()>1: arr=(arr-arr.mean())/arr.std()
            thumbs.append(arr)
        except Exception: pass
    if len(thumbs)<3: return None
    matches=total=0
    for a,b in zip(thumbs, thumbs[1:]):
        n=min(len(a),len(b))
        if n:
            corr=float(np.corrcoef(a[:n],b[:n])[0,1]); total+=1
            if corr>.98: matches+=1
    return matches/total if total else None

def metric_from_blur(value):
    return 75 if value is None else int(max(0,min(100,value*2)))
