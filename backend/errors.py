def friendly_error(exc: Exception) -> str:
    text = str(exc)
    low = text.lower()

    if "generation canceled" in low:
        return "No problem — generation was canceled."

    if "need at least 3" in low:
        return "This capture is too short. Add more photos or use a longer, slower video."

    if "ffmpeg" in low:
        return "Maker Splat could not turn your video into photos. Try a different video, or make sure FFmpeg is available."

    if "nerfstudio tools missing" in low or "ns-process-data" in text or "ns-train" in text or "ns-export" in text or "nerfstudio" in low:
        return "Real Mode is not ready. Open Settings → Engines to see which Nerfstudio/COLMAP tools are missing, or switch back to Demo Engine."

    if "colmap" in low:
        return "COLMAP is missing or failed. Real splats need COLMAP for camera tracking."

    if "cuda" in low or "nvidia" in low:
        return "GPU/CUDA is unavailable. Real splats work best with a configured NVIDIA CUDA GPU."

    if "no .ply or .splat" in low:
        return "The real engine finished, but no preview file was exported. Check the diagnostics bundle and Nerfstudio version."

    return text or "Something went wrong. Try again with a slower video or more photos."
