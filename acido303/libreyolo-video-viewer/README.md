# LibreYOLO Video Viewer

A local Python CLI that runs [LibreYOLO](https://github.com/LibreYOLO/libreyolo) object detection on a local MP4 file and plays back the video with annotated bounding boxes in an OpenCV window.

## Requirements

- Python 3.11+
- A local MP4 file you want to analyse

## Installation

```bash
# Clone or copy the project
cd libreyolo-video-viewer

# Create and activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Placing a Video

Copy your `.mp4` file into the `videos/` directory:

```
videos/
  test.mp4
```

## Usage

### Basic run with viewer

```powershell
python .\analyze_video.py --video ".\videos\test.mp4" --model ".\models\LibreYOLOXs.pt" --viewer
```

### Full example

```powershell
python .\analyze_video.py `
  --video ".\videos\Fortnite_20260124123317.mp4" `
  --model ".\models\LibreYOLOXs.pt" `
  --classes person car weapon `
  --confidence 0.45 `
  --sample-rate 5 `
  --viewer `
  --save-annotated-video
```

### All flags

| Flag | Default | Description |
|---|---|---|
| `--video` | required | Path to the MP4 file |
| `--model` | `.\models\LibreYOLOXs.pt` | Path to the LibreYOLO model file |
| `--output-dir` | `./output` | Where outputs are written |
| `--classes` | all | Filter to these class names (space-separated) |
| `--confidence` | `0.45` | Minimum detection confidence (0–1) |
| `--sample-rate` | `5` | Detection runs per second |
| `--viewer` | off | Open an OpenCV viewer window |
| `--save-annotated-video` | off | Save annotated MP4 to `output/annotated/` |
| `--save-snapshots` / `--no-save-snapshots` | on | Save snapshot JPEGs per detection |
| `--annotate-snapshots` / `--no-annotate-snapshots` | on | Draw bounding boxes on snapshots |
| `--max-events` | none | Stop after N events (useful for testing) |
| `--max-frames` | none | Stop after N processed frames (useful for testing) |

## Viewer Controls

| Key | Action |
|---|---|
| `q` | Quit |
| `space` | Pause / Resume |
| `s` | Save current annotated frame as a snapshot |

## Output

```
output/
  detections.json          — full JSON report
  snapshots/
    000003_person.jpg      — snapshot per detection event
    000014_car.jpg
  annotated/
    annotated_test.mp4     — full annotated video (if --save-annotated-video)
```

### detections.json structure

```json
{
  "video": { "path", "fps", "frame_count", "width", "height", "duration_seconds" },
  "analysis": { "confidence_threshold", "sample_rate", "classes", ... },
  "outputs": { "json_report", "snapshot_dir", "annotated_video" },
  "summary": { "total_events", "classes_detected": { "person": 2, "dog": 1 } },
  "events": [ { "timestamp", "seconds", "frame_index", "class_name", "confidence", "bbox", "snapshot_path" } ]
}
```

## Running Tests

```bash
pytest tests/
```

## Known Limitations

- Detection does not run on every frame by default (`--sample-rate 5` means ~every 6th frame at 30 fps). Bounding boxes between inference frames are reused from the previous run.
- No deduplication: the same object may appear as multiple events across nearby timestamps.
- The OpenCV viewer plays back at roughly original speed; very high-resolution videos may lag.
- Annotated video uses `mp4v` codec with `avc1` fallback; playback in some players may require VLC.

## Future Improvements

- Phase 2: timeline scrubber, jump-to-detection, class filter overlay
- Phase 3: CSV export, HTML report, deduplication window
- Phase 4: FastAPI backend + browser UI
- Phase 5: webcam / RTSP live input
