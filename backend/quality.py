from pathlib import Path
from PIL import Image
import numpy as np

def analyze_project(root: Path):
    capture = root/"capture"
    files = sorted(capture.glob("*"))
    videos = [p for p in files if p.suffix.lower() in {".mp4",".mov",".m4v",".webm"}]
    images = [p for p in files if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"}]

    warnings, tips, advice, missing = [], [], [], []
    if videos:
        score, count = 78, f"{len(videos)} video"
        tips.append("Video detected. Maker Splat will pick frames automatically.")
        advice.append("If the result has holes, record another slow orbit from a different height.")
    else:
        score, count = min(96,45+len(images)*2), f"{len(images)} photos"
        if len(images)<20:
            warnings.append("More photos usually make a better splat.")
            advice.append("Add 20–40 more overlapping photos.")
            missing.append("more coverage")
        if len(images)<8:
            missing.append("back side")
            missing.append("top angle")
        tips.append("Photos detected. Overlap matters more than perfect individual shots.")

    blur = estimate_blur(images[:30])
    duplicate = duplicate_score(images[:40])
    brightness = estimate_brightness(images[:30])
    aspect = aspect_variety(images[:30])

    if blur is not None and blur < 18:
        warnings.append("Some images may be blurry or low texture.")
        advice.append("Move slower, use brighter light, or use photos instead of video.")
        score -= 15

    if duplicate is not None and duplicate > .65:
        warnings.append("Many frames look nearly identical.")
        advice.append("Move around the subject more so Maker Splat sees new angles.")
        missing.append("side variety")
        score -= 10

    if brightness is not None:
        if brightness < 55:
            warnings.append("The capture looks dark.")
            advice.append("Add light or move near a window. Dark captures often look noisy.")
            score -= 8
        elif brightness > 215:
            warnings.append("The capture may be overexposed.")
            advice.append("Avoid harsh sunlight or bright white backgrounds.")
            score -= 6

    if aspect is not None and aspect < .08 and not videos and len(images) > 10:
        advice.append("Most photos have the same framing. Add a few higher and lower angles.")

    score = max(10,min(100,score))
    likely = likely_result(score, warnings, missing)
    fix_steps = build_fix_steps(score, warnings, missing, videos=bool(videos), images=len(images))

    return {
        "score":score,
        "label":"Looks great" if score>=85 else "Should work" if score>=65 else "Try improving capture",
        "count":count,
        "likely_result":likely,
        "warnings":dedupe(warnings),
        "tips":dedupe(tips),
        "advice":dedupe(advice),
        "missing_angles":dedupe(missing),
        "fix_steps":fix_steps,
        "readiness":"ready" if score>=70 else "needs_help",
        "metrics":{
            "sharpness":metric(blur),
            "coverage":min(100,score+5),
            "overlap":min(100,score+3),
            "lighting":metric_brightness(brightness),
            "variety":int(max(0,min(100,100-(duplicate or 0)*100))),
        }
    }

def likely_result(score, warnings, missing):
    if score >= 85:
        return "This should make a strong 3D preview."
    if score >= 70:
        return "This should work, but small holes are possible."
    if "back side" in missing:
        return "This may have holes on the back or top."
    if warnings:
        return "This may look fuzzy or incomplete unless you add a better capture."
    return "This may need more angles before it works well."

def build_fix_steps(score, warnings, missing, videos, images):
    steps = []
    if "more coverage" in missing:
        steps.append("Add more photos or use a longer video.")
    if "back side" in missing:
        steps.append("Capture the back side of the subject.")
    if "top angle" in missing:
        steps.append("Add a few photos from slightly above.")
    if "side variety" in missing:
        steps.append("Move around the subject more, not just in place.")
    if any("dark" in w.lower() for w in warnings):
        steps.append("Use brighter, softer light.")
    if any("blurry" in w.lower() for w in warnings):
        steps.append("Record slower or switch to still photos.")
    if videos:
        steps.append("Try a second slower video if the first result has holes.")
    if not steps and score >= 70:
        steps.append("This capture is ready. Generate the 3D scene.")
    if not steps:
        steps.append("Try again with 30–150 clear overlapping photos.")
    return dedupe(steps)

def dedupe(items):
    out=[]
    for item in items:
        if item not in out:
            out.append(item)
    return out

def estimate_blur(paths):
    vals=[]
    for p in paths:
        try:
            img=Image.open(p).convert("L"); img.thumbnail((320,320)); arr=np.asarray(img,dtype=np.float32)
            vals.append(float(np.diff(arr,axis=0).var()+np.diff(arr,axis=1).var()))
        except Exception: pass
    return float(np.median(vals)) if vals else None

def estimate_brightness(paths):
    vals=[]
    for p in paths:
        try:
            img=Image.open(p).convert("L"); img.thumbnail((160,160)); vals.append(float(np.asarray(img).mean()))
        except Exception: pass
    return float(np.median(vals)) if vals else None

def aspect_variety(paths):
    vals=[]
    for p in paths:
        try:
            img=Image.open(p); vals.append(img.size[0]/max(1,img.size[1]))
        except Exception: pass
    return float(np.std(vals)) if len(vals)>2 else None

def duplicate_score(paths):
    thumbs=[]
    for p in paths:
        try:
            img=Image.open(p).convert("L"); img.thumbnail((32,32)); arr=np.asarray(img,dtype=np.float32).flatten()
            if arr.std()>1: arr=(arr-arr.mean())/arr.std()
            thumbs.append(arr)
        except Exception: pass
    if len(thumbs)<3: return None
    matches=total=0
    for a,b in zip(thumbs, thumbs[1:]):
        corr=float(np.corrcoef(a,b)[0,1]); total+=1
        if corr>.98: matches+=1
    return matches/total if total else None

def metric(v): return 75 if v is None else int(max(0,min(100,v*2)))
def metric_brightness(v):
    if v is None: return 75
    return int(max(0,min(100,100-abs(v-135)*.9)))
