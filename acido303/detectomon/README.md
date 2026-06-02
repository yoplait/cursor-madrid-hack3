# DetectoMon

Live camera object detection with visual overlays, clickable detections, and an in-memory card registry for discovered objects.

## Architecture

```text
Browser webcam → video + overlay canvas → WebSocket JPEG → FastAPI + LibreYOLO
                                                      ↓
                                            JSON detections + card API
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- Webcam
- LibreYOLO model file (optional if using mock mode)

## Backend setup (PowerShell)

```powershell
cd C:\projects\cursor-madrid-hack3\acido303\detectomon

py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt

copy .\.env.example .\.env
# Edit .env: set MODEL_PATH to your .pt file, or MOCK_DETECTION=1 for dev
```

Run the API:

```powershell
cd C:\projects\cursor-madrid-hack3\acido303\detectomon\backend
python .\main.py
```

Or:

```powershell
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API: `http://127.0.0.1:8000`  
WebSocket: `ws://127.0.0.1:8000/ws/detect`

## Frontend setup (PowerShell)

```powershell
cd C:\projects\cursor-madrid-hack3\acido303\detectomon\frontend

npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` and `/ws` to the backend.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `LibreYOLO9t.pt` | Path to LibreYOLO weights (required for real inference) |
| `MOCK_DETECTION` | `0` | Set to `1` for fake bounding boxes without a model |
| `DEFAULT_CONFIDENCE` | `0.45` | Default confidence threshold |
| `DEFAULT_SAMPLE_FPS` | `5` | Documented default; frontend samples every 200ms |
| `MAX_FRAME_WIDTH` | `640` | Max frame width sent to detector |
| `MAX_FRAME_HEIGHT` | `480` | Max frame height sent to detector |
| `BACKEND_HOST` | `127.0.0.1` | API bind host |
| `BACKEND_PORT` | `8000` | API bind port |

If LibreYOLO fails to load and `MOCK_DETECTION` is not set, the backend automatically falls back to mock detection.

## API

- `WS /ws/detect` — send `{ frameId, imageBase64, classes, confidence }`, receive detections with `sourceFrameWidth`, `sourceFrameHeight`, and per-detection `knownObject` / `cardId`.
- `POST /api/cards/generate` — create or reuse a card for a detection.
- `GET /api/cards/{cardId}` — fetch card details.
- `GET /api/health` — status and mock mode flag.

## Mock mode

For development without a model:

```env
MOCK_DETECTION=1
```

Mock mode draws 1–3 random boxes for enabled classes each frame.

## Custom classes

The default COCO-style classes work with standard LibreYOLO models. Classes not in the model (e.g. `weapon`) will never be detected unless you use a custom-trained model.

## Acceptance criteria

1. Bounding boxes on live video  
2. Class name + confidence on each box  
3. Overlay scaled to displayed video size  
4. Clickable detections (highest confidence on overlap)  
5. Selected detection highlighted  
6. Side panel shows selected object details  
7. Known objects show “Already discovered”  
8. New objects show generate action  
9. Selection persists during card generation  
10. Visual states: normal, selected, known, new, generating  
