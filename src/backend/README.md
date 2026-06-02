# backend

API FastAPI que expone inferencia LibreYOLO.

## Endpoints

- `GET /health` — ping
- `GET /model` — pesos cargados
- `POST /detect` — sube imagen (`multipart/form-data`, campo `file`)

## Dev

```bash
source ../../.venv/bin/activate
make backend    # desde la raíz del repo
```

Docs interactivas: http://127.0.0.1:8000/docs
