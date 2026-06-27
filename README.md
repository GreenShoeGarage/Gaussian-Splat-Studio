# Maker Splat

A simple local browser app for everyday makers who want to turn a video or photo set into a Gaussian splat.

No accounts. No cloud. No billing. No enterprise stack.

## What it does

Open a browser, upload a video or images, click **Generate**, preview/download the result.

```text
Upload video/photos
  -> extract frames if video
  -> run Nerfstudio splatfacto if installed
  -> export result
  -> preview/download
```

## Quick start

```bash
docker compose up --build
```

Open:

```text
http://localhost:5173
```

## Real splat generation

For real splats, the backend machine needs:

- ffmpeg
- COLMAP
- Nerfstudio
- CUDA GPU recommended

Enable real generation:

```bash
GSS_REAL_MODE=1 docker compose up --build
```

Without real mode, Maker Splat runs a friendly demo/fallback path so the app can be tested.

## Good input tips

Use a short video or 30–150 photos.

Best results:

- walk slowly around the object or space
- keep the subject in frame
- avoid motion blur
- use good lighting
- avoid shiny/transparent objects

## Output

Generated files appear in:

```text
backend/runs/
```

The UI exposes downloads for available artifacts.
