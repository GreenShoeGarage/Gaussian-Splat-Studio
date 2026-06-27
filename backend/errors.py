def friendly_error(exc: Exception) -> str:
    text = str(exc)

    if "ffmpeg" in text.lower() and ("not found" in text.lower() or "no such file" in text.lower()):
        return "ffmpeg is missing. Install ffmpeg or use the Docker version of Maker Splat."

    if "ns-train" in text or "ns-process-data" in text or "ns-export" in text or "Nerfstudio" in text:
        return "Nerfstudio is missing or failed. Use Demo Mode, or install Nerfstudio/COLMAP for real splats."

    if "Need at least 3" in text:
        return "Not enough images. Upload at least 3 photos or use a longer video."

    if "CUDA" in text or "cuda" in text or "nvidia" in text.lower():
        return "CUDA/GPU is unavailable. Real splats need a properly configured NVIDIA GPU, or use Demo Mode."

    return text or "Something went wrong while generating the splat."
