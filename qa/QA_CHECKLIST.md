# Maker Splat 3.0 QA Checklist

## Docker

- [ ] `docker compose up --build` starts demo mode
- [ ] `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build` builds GPU profile
- [ ] `/api/preflight/real-mode` reports tools clearly

## Backend

- [ ] `pytest` passes
- [ ] project creation works
- [ ] preflight endpoint works
- [ ] missing Nerfstudio gives friendly error

## Real generation

- [ ] upload 30+ photos
- [ ] `ns-process-data images` completes
- [ ] `ns-train splatfacto` completes
- [ ] `ns-export gaussian-splat` exports PLY/SPLAT
- [ ] UI exposes exported artifact

## Frontend

- [ ] `npm run build` passes
- [ ] setup screen explains real mode
- [ ] missing tools are obvious
