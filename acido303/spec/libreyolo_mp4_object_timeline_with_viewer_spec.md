# LibreYOLO MP4 Object Timeline with Annotated Video Viewer — MVP Specification

## 1. Project Goal

Build a local proof-of-concept application that analyses a local `.mp4` video file using [LibreYOLO](https://github.com/LibreYOLO/libreyolo), detects objects, and provides a simple video viewer where the user can watch the video with detected objects framed using bounding boxes.

The application should also generate an object-detection timeline, save optional snapshots, and write a structured JSON report.

The first version should be a Python local application. Prioritise a working computer-vision pipeline and an annotated viewer over web architecture.

## 2. Core Use Case

The user manually downloads a YouTube video as an `.mp4` file and wants to inspect it locally.

The app should allow running:

```bash
python analyze_video.py --video ./videos/test.mp4 --classes person car dog laptop "cell phone" --confidence 0.45 --sample-rate 5 --viewer --save-annotated-video
```

The app should:

1. Open the local MP4 file.
2. Read metadata such as FPS, frame count, width, height, and duration.
3. Run LibreYOLO object detection on frames.
4. Draw bounding boxes, labels, and confidence scores over the video.
5. Display a local viewer window showing the annotated video.
6. Optionally save an annotated MP4 output file.
7. Save snapshots for relevant detections.
8. Generate a `detections.json` report.
9. Print a human-readable summary to the console.

## 3. MVP Scope

### 3.1 In Scope

Implement the following:

- Python CLI application.
- Local MP4 video input.
- OpenCV-based video reading.
- OpenCV-based local viewer window.
- Object detection using LibreYOLO.
- Bounding box rendering over video frames.
- Label and confidence rendering.
- Configurable confidence threshold.
- Optional filtering by object class.
- Configurable frame processing rate.
- Optional annotated MP4 export.
- Event timeline generation.
- Snapshot saving.
- JSON output.
- Basic console logging.
- Clear project structure.
- Basic error handling.
- README with setup and usage instructions.

### 3.2 Out of Scope for MVP

Do not implement these yet:

- YouTube downloading.
- Webcam input.
- RTSP streams.
- FastAPI backend.
- React/Next.js frontend.
- WebSocket live progress.
- Database storage.
- User authentication.
- Docker deployment.
- Cloud deployment.
- Training custom models.
- Advanced multi-object tracking.
- Multi-video batch processing.

## 4. Recommended Project Structure

```text
libreyolo-video-viewer/
  README.md
  requirements.txt
  analyze_video.py
  src/
    __init__.py
    config.py
    models.py
    video_reader.py
    detector.py
    renderer.py
    viewer.py
    event_builder.py
    snapshot_writer.py
    report_writer.py
    time_utils.py
  videos/
    .gitkeep
  output/
    .gitkeep
    snapshots/
      .gitkeep
    annotated/
      .gitkeep
  tests/
    __init__.py
    test_time_utils.py
    test_event_builder.py
    test_renderer.py
```

## 5. Dependencies

Use Python 3.11+.

Create a `requirements.txt` containing at least:

```txt
libreyolo
opencv-python
numpy
pydantic
pytest
```

If LibreYOLO requires additional runtime dependencies, add them explicitly after validating the first run.

## 6. CLI Requirements

The main entrypoint should be:

```bash
python analyze_video.py
```

Supported arguments:

```bash
--video                 Required. Path to local MP4 file.
--output-dir            Optional. Default: ./output
--classes               Optional. One or more class names to keep.
--confidence            Optional. Default: 0.45
--sample-rate           Optional. Detection frequency in frames per second. Default: 5
--viewer                Optional boolean flag. Show a local OpenCV viewer window. Default: false
--save-annotated-video  Optional boolean flag. Save annotated MP4. Default: false
--save-snapshots        Optional boolean flag. Default: true
--annotate-snapshots    Optional boolean flag. Save snapshots with bounding boxes. Default: true
--max-events            Optional. Stop after N events. Useful for testing.
--max-frames            Optional. Stop after N processed frames. Useful for testing.
```

Example:

```bash
python analyze_video.py \
  --video ./videos/test.mp4 \
  --classes person car dog laptop "cell phone" \
  --confidence 0.45 \
  --sample-rate 5 \
  --viewer \
  --save-annotated-video \
  --output-dir ./output
```

## 7. Functional Requirements

### 7.1 Video Reading

Use OpenCV to open the video file.

The app must extract:

- File path.
- FPS.
- Total frame count.
- Width.
- Height.
- Duration in seconds.

If the video cannot be opened, fail with a clear error message.

### 7.2 Frame Processing Strategy

For the annotated viewer, the app should display the video in order.

However, object detection does not need to run on every frame by default.

Use the `--sample-rate` value to decide how often inference runs.

Example:

- Video FPS: 30.
- `--sample-rate 5` means run detection around 5 times per second.
- Detection frames would approximately be every 6 frames.

To keep the viewer smooth, reuse the most recent detections for frames between inference runs.

This means:

```text
Frame 0: run detection
Frame 1-5: reuse frame 0 detections
Frame 6: run detection
Frame 7-11: reuse frame 6 detections
```

This is acceptable for the MVP.

### 7.3 Object Detection

Create a wrapper class around LibreYOLO.

Suggested interface:

```python
class ObjectDetector:
    def __init__(self, confidence_threshold: float):
        ...

    def detect(self, frame) -> list[Detection]:
        ...
```

Create a `Detection` model with:

```python
class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]
```

The implementation should be isolated so the LibreYOLO integration can be changed later without rewriting the full app.

### 7.4 Class Filtering

If the user provides `--classes`, only keep detections whose class name matches one of the requested classes.

Matching should be case-insensitive.

Example:

```bash
--classes person dog "cell phone"
```

If no classes are provided, keep all classes.

### 7.5 Bounding Box Rendering

Implement rendering in `src/renderer.py`.

The renderer should:

- Draw a rectangle around every accepted detection.
- Draw the class name.
- Draw the confidence value with two decimal places.
- Keep text readable.
- Clamp bounding boxes to frame boundaries.
- Avoid crashing on malformed bounding boxes.

Suggested interface:

```python
class FrameRenderer:
    def render(self, frame, detections: list[Detection], timestamp: str | None = None):
        ...
```

The rendered frame should optionally include:

- Timestamp in the top-left corner.
- Number of current detections.
- FPS / processing indicator if easily available.

### 7.6 Local Video Viewer

Implement a local OpenCV viewer in `src/viewer.py`.

When `--viewer` is enabled:

- Open a window called `LibreYOLO Video Viewer`.
- Show the current annotated frame.
- Keep roughly the original video playback speed where possible.
- Pressing `q` should quit.
- Pressing `space` should pause/resume playback.
- Pressing `s` should save a snapshot of the current annotated frame.

The viewer does not need a complex GUI. An OpenCV window is enough for the MVP.

### 7.7 Annotated Video Export

When `--save-annotated-video` is enabled, write an annotated MP4 to:

```text
output/annotated/annotated_test.mp4
```

Use OpenCV `VideoWriter`.

The output video should:

- Preserve the original resolution.
- Use the original FPS where possible.
- Contain bounding boxes and labels.
- Be playable in VLC or a standard video player.

If the codec is not available, fail gracefully and print a helpful message.

### 7.8 Event Creation

Every valid detection on an inference frame should become an event.

Do not create duplicate events for every displayed frame when detections are reused between inference runs.

Event model:

```python
class DetectionEvent(BaseModel):
    timestamp: str
    seconds: float
    frame_index: int
    class_name: str
    confidence: float
    bbox: list[float]
    snapshot_path: str | None
```

Timestamp format:

```text
HH:MM:SS
```

Example event:

```json
{
  "timestamp": "00:01:14",
  "seconds": 74.0,
  "frame_index": 2220,
  "class_name": "dog",
  "confidence": 0.82,
  "bbox": [120.0, 55.0, 310.0, 280.0],
  "snapshot_path": "output/snapshots/000074_dog.jpg"
}
```

### 7.9 Snapshot Saving

When a detection passes filtering:

- Save a snapshot image.
- Use the timestamp and class name in the filename.
- Avoid invalid filename characters.
- If multiple objects of the same class are detected at the same timestamp, append a counter.

Example filenames:

```text
output/snapshots/000003_person.jpg
output/snapshots/000014_car.jpg
output/snapshots/000074_dog.jpg
output/snapshots/000074_person_2.jpg
```

If `--annotate-snapshots` is enabled, draw bounding boxes and labels on the snapshot.

### 7.10 JSON Report

Create:

```text
output/detections.json
```

The JSON should contain video metadata, analysis settings, output paths, summary, and events.

Example:

```json
{
  "video": {
    "path": "./videos/test.mp4",
    "fps": 30.0,
    "frame_count": 4500,
    "width": 1920,
    "height": 1080,
    "duration_seconds": 150.0
  },
  "analysis": {
    "confidence_threshold": 0.45,
    "sample_rate": 5,
    "classes": ["person", "car", "dog", "laptop", "cell phone"],
    "viewer_enabled": true,
    "annotated_video_enabled": true
  },
  "outputs": {
    "json_report": "output/detections.json",
    "snapshot_dir": "output/snapshots",
    "annotated_video": "output/annotated/annotated_test.mp4"
  },
  "summary": {
    "total_events": 4,
    "classes_detected": {
      "person": 2,
      "car": 1,
      "dog": 1
    }
  },
  "events": [
    {
      "timestamp": "00:00:03",
      "seconds": 3.0,
      "frame_index": 90,
      "class_name": "person",
      "confidence": 0.91,
      "bbox": [100.0, 120.0, 350.0, 600.0],
      "snapshot_path": "output/snapshots/000003_person.jpg"
    }
  ]
}
```

### 7.11 Console Output

The app should print useful progress information:

```text
Analyzing video: ./videos/test.mp4
FPS: 30.0
Resolution: 1920x1080
Duration: 00:02:30
Detection sample rate: 5 frames/sec
Confidence threshold: 0.45
Classes: person, car, dog, laptop, cell phone
Viewer: enabled
Annotated video export: enabled

[00:00:03] person detected, confidence 0.91
[00:00:14] car detected, confidence 0.84
[00:01:14] dog detected, confidence 0.82

Done.
Total events: 3
Report saved to: ./output/detections.json
Snapshots saved to: ./output/snapshots
Annotated video saved to: ./output/annotated/annotated_test.mp4
```

## 8. Non-Functional Requirements

### 8.1 Simplicity

Keep the MVP simple. Prioritise a working local pipeline over architecture complexity.

### 8.2 Extensibility

Design the code so the following can be added later:

- FastAPI upload endpoint.
- Web UI timeline.
- Browser-based video player.
- Webcam input.
- RTSP input.
- Object tracking.
- Event deduplication.
- Search by object class.
- Export to CSV.

### 8.3 Performance

Default processing should not run detection on every frame unless explicitly configured.

The viewer should reuse recent detections between inference frames.

The app should support long videos by avoiding unnecessary memory usage. Do not load the whole video into memory.

### 8.4 Error Handling

Handle at least:

- Video file not found.
- Video cannot be opened.
- Invalid sample rate.
- Invalid confidence value.
- Output directory cannot be created.
- LibreYOLO model loading or inference errors.
- OpenCV viewer cannot be opened.
- VideoWriter codec is unavailable.

### 8.5 Security and Safety

This is a local tool. Do not download external content in the MVP.

The user is responsible for providing a local MP4 file they have permission to analyse.

Do not add network services or open ports in the MVP.

## 9. Implementation Notes

### 9.1 Keep LibreYOLO Isolated

Implement LibreYOLO-specific code only in:

```text
src/detector.py
```

The rest of the app should work with internal `Detection` objects.

### 9.2 Keep Rendering Isolated

Implement all drawing logic only in:

```text
src/renderer.py
```

This keeps detection separate from visual presentation.

### 9.3 Avoid Overengineering

Do not add:

- Celery.
- Kafka.
- RabbitMQ.
- Databases.
- Docker Compose.
- Authentication.
- Frontend frameworks.

This is a local proof-of-concept.

### 9.4 Event Deduplication Optional

For MVP, it is acceptable if the same object is detected multiple times across nearby timestamps.

Optional improvement:

- Add `--dedupe-window 3` to avoid repeating the same class too often.
- Example: if `person` appears at 00:03, 00:04, and 00:05, keep only the first event within a 3-second window.

Do not implement this unless the basic pipeline and viewer are already working.

## 10. Testing Requirements

Add lightweight tests for pure functions.

Test examples:

### 10.1 Time Formatting

Input:

```python
format_seconds(74)
```

Expected:

```text
00:01:14
```

### 10.2 Class Filtering

Given classes:

```python
["person", "dog"]
```

A detection with class `Person` should be accepted.

A detection with class `car` should be rejected.

### 10.3 Event Summary

Given events:

```text
person, person, dog
```

Summary should return:

```json
{
  "person": 2,
  "dog": 1
}
```

### 10.4 Bounding Box Clamping

Given a detection with coordinates outside the frame boundaries, the renderer should clamp the coordinates so drawing does not crash.

Do not try to unit test LibreYOLO inference in MVP tests.

## 11. README Requirements

Create a `README.md` with:

- Project description.
- Requirements.
- Installation steps.
- How to place a video in `./videos`.
- Example commands.
- Viewer controls.
- Output explanation.
- Known limitations.
- Future improvements.

Example README command:

```bash
python analyze_video.py --video ./videos/test.mp4 --classes person dog car --confidence 0.45 --sample-rate 5 --viewer --save-annotated-video
```

Viewer controls:

```text
q      quit
space  pause/resume
s      save current annotated frame
```

## 12. Acceptance Criteria

The MVP is complete when:

1. A user can place an MP4 file in `./videos`.
2. The user can run `python analyze_video.py --video ./videos/test.mp4 --viewer`.
3. A local viewer opens and plays the video.
4. Detected objects are framed with bounding boxes.
5. Labels and confidence values are visible.
6. The viewer supports quit, pause/resume, and save-frame controls.
7. The app optionally saves an annotated MP4 when `--save-annotated-video` is enabled.
8. The app saves snapshots for detections.
9. The app writes `output/detections.json`.
10. The JSON contains video metadata, analysis settings, output paths, summary, and events.
11. The console output clearly shows progress and final result location.
12. Basic tests pass with `pytest`.
13. The README explains how to run the app and use the viewer.

## 13. Future Phase Ideas

After the MVP works, consider building:

### Phase 2 — Better Local Viewer

- Timeline scrubber.
- Jump to next detection.
- Toggle bounding boxes on/off.
- Filter classes while viewing.
- Side panel with current detections.

### Phase 3 — Better Reports

- CSV export.
- Deduplication window.
- Process only a time range.
- Generate contact sheet of snapshots.
- Generate HTML report.

### Phase 4 — Web Application

- FastAPI backend.
- Upload MP4.
- Background analysis job.
- WebSocket progress updates.
- Browser-based video player.
- Timeline UI.
- Snapshot gallery.
- Filter detections by class.

### Phase 5 — Real-Time Sources

- Webcam input.
- RTSP streams.
- Live event feed.
- Alert rules.

### Phase 6 — Product Direction

- Search inside videos by object class.
- Analyse long videos and create object timelines.
- Generate automatic summaries.
- Combine object detection with OCR or audio transcription.

## 14. Development Instructions for Claude

Please implement this project incrementally.

Recommended order:

1. Create project structure.
2. Add requirements.
3. Implement data models.
4. Implement time utilities.
5. Implement video metadata reading.
6. Implement frame sampling loop.
7. Stub detector if needed.
8. Integrate LibreYOLO in `src/detector.py`.
9. Implement filtering and event creation.
10. Implement renderer for bounding boxes.
11. Implement OpenCV viewer.
12. Implement optional annotated video writer.
13. Implement snapshot writer.
14. Implement JSON report writer.
15. Add CLI arguments.
16. Add README.
17. Add basic tests.

Keep implementation steps small and easy to review.

Do not introduce a web framework until the local annotated viewer MVP is confirmed working.
