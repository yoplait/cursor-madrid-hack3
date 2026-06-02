# DetectoMon — Detected Object Visual Marking Update

## Goal

Update the DetectoMon specification so that every detected object is clearly marked in the live camera viewer.

The user must be able to visually identify:

- what object was detected
- where it is in the camera frame
- confidence score
- whether the object is selected
- whether the object already has a generated card

## Required Behaviour

When LibreYOLO detects an object, the frontend must draw a visual overlay on top of the live video.

The overlay must include:

1. Bounding box around the detected object.
2. Object label.
3. Confidence score.
4. Optional status badge.
5. Selection highlight when the user clicks the object.
6. Existing-card indicator if the object was already discovered.

## Example Overlay

```text
┌─────────────────────────────┐
│ cup 96%                     │
│ Already discovered          │
│                             │
│      detected object        │
│                             │
└─────────────────────────────┘
```

## Visual States

### 1. Normal Detection

A detected object should show:

```text
cup 0.96
```

### 2. Selected Detection

When the user clicks a detected object, it should be visually emphasized.

Use:

- thicker border
- glowing outline
- selected badge
- linked preview panel update

Example label:

```text
cup 0.96 — selected
```

### 3. Existing Object / Existing Card

If the detected object matches a previously generated card, show a badge:

```text
Already discovered
```

or:

```text
Card exists
```

### 4. New Object

If the detected object has no card yet, show:

```text
New object
```

or:

```text
Generate card
```

## Frontend Implementation

Use a canvas overlay above the video.

The camera viewer should use this structure:

```tsx
<div className="viewer">
  <video ref={videoRef} autoPlay muted playsInline />
  <canvas ref={overlayCanvasRef} />
  <canvas ref={captureCanvasRef} hidden />
</div>
```

CSS should position the overlay canvas directly above the video:

```css
.viewer {
  position: relative;
  width: 100%;
  max-width: 960px;
}

.viewer video,
.viewer canvas {
  width: 100%;
  height: auto;
  display: block;
}

.viewer canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: auto;
}
```

## Coordinate Mapping Requirement

The backend returns bounding boxes in the coordinate system of the submitted frame.

The frontend must correctly map backend coordinates to the displayed video size.

Required logic:

```text
scaleX = displayedVideoWidth / sourceFrameWidth
scaleY = displayedVideoHeight / sourceFrameHeight

displayX1 = x1 * scaleX
displayY1 = y1 * scaleY
displayX2 = x2 * scaleX
displayY2 = y2 * scaleY
```

Do not assume the displayed video size is the same as the captured frame size.

## Clickable Detections

The overlay must allow the user to click on a detected object.

When clicked:

1. Find the bounding box under the cursor.
2. Mark that detection as selected.
3. Show its cropped preview in the detected object panel.
4. Enable the `Generate Card` or `Show Existing Card` button.

If multiple boxes overlap, select the highest-confidence detection.

## Detection Data Model

Each detection should contain:

```ts
type Detection = {
  id: string;
  className: string;
  confidence: number;
  box: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  sourceFrameWidth: number;
  sourceFrameHeight: number;
  selected?: boolean;
  knownObject?: boolean;
  cardId?: string | null;
};
```

The backend WebSocket response should include the source frame dimensions:

```json
{
  "frameId": 1,
  "sourceFrameWidth": 640,
  "sourceFrameHeight": 480,
  "detections": [
    {
      "id": "frame-1-det-1",
      "className": "cup",
      "confidence": 0.96,
      "box": {
        "x1": 120,
        "y1": 80,
        "x2": 420,
        "y2": 360
      },
      "knownObject": true,
      "cardId": "card-123"
    }
  ]
}
```

## Detection Panel Sync

When an object is selected in the video overlay, the side panel must update:

```text
Selected Object
Class: cup
Confidence: 96%
Status: Already discovered
Card: Tazamon
[ Show Card ]
```

If the object is new:

```text
Selected Object
Class: cup
Confidence: 96%
Status: New object
[ Generate Card ]
```

## Card Generation Integration

When the user clicks `Generate Card`, the selected detection must remain marked while the card is being generated.

Show a temporary badge:

```text
Generating card...
```

After generation:

- if new card was generated:
  ```text
  New card generated
  ```
- if existing card was reused:
  ```text
  Existing card found
  ```

## Acceptance Criteria

This update is complete when:

1. Detected objects are marked with bounding boxes on the live video.
2. Each box shows class name and confidence score.
3. The overlay scales correctly to the visible video size.
4. The user can click a detected object.
5. The clicked object is visually highlighted.
6. The detected object panel updates with the selected object.
7. Known objects show an existing-card badge.
8. New objects show a generate-card action.
9. The selected object remains marked during card generation.
10. The UI clearly distinguishes normal, selected, known, and new detections.
