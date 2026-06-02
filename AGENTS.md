# AGENTS.md

## Cursor Cloud specific instructions

### Product scope

This repo is a **Cursor Madrid Hackathon #3** workspace. The only runnable application is the **LibreYOLO Video Viewer** CLI at `acido303/libreyolo-video-viewer/`. Everything else (`ejemplos/`, `libreria/`, `linkedin/`, root `.webloc` files) is reference material, not a service.

There is no Docker, web server, or database. End-to-end work is a single Python process (`analyze_video.py`).

### Working directory

Always run commands from:

```bash
cd acido303/libreyolo-video-viewer
source .venv/bin/activate
```

### System dependency (one-time per VM image)

Ubuntu images without `python3-venv` cannot create `.venv`. If `python -m venv .venv` fails:

```bash
sudo apt-get install -y python3.12-venv
```

The VM **update script** only refreshes pip packages inside `.venv`; it does not install apt packages.

### Lint / test / run

| Task | Command |
|------|---------|
| Unit tests | `pytest tests/` |
| Lint | Not configured in this repo |
| Headless E2E | `python analyze_video.py --video ./videos/<file>.mp4 --model LibreYOLOXs.pt` |
| Interactive viewer | Add `--viewer` (requires a display; often unavailable in headless cloud VMs) |

See `acido303/libreyolo-video-viewer/README.md` for all CLI flags.

### Model weights

Weights are **not** in git (`models/` is gitignored). On first use, LibreYOLO auto-downloads when you pass the bare filename:

```bash
--model LibreYOLOXs.pt
```

Weights land in `weights/LibreYOLOXs.pt` (~69 MB). The CLI default `./models/LibreYOLOXs.pt` will **not** auto-download unless you copy or symlink weights into `models/`.

### Test video

`videos/` is gitignored. For cloud demos, create a short MP4 locally (e.g. from the upstream parkour sample image) or use your own file under `videos/`.

### Outputs

Runs write to `output/` (also gitignored): `detections.json`, optional `snapshots/`, optional `annotated/` MP4.

### GPU

PyTorch installs with CUDA wheels via `libreyolo`; inference also runs on CPU if no GPU is present (slower but functional).
