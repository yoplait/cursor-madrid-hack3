# LibreYOLO Video Viewer

> Deutsche Übersetzung — siehe auch [README.md](README.md) (Englisch)

Eine lokale Python-CLI, die [LibreYOLO](https://github.com/LibreYOLO/libreyolo)-Objekterkennung auf einer lokalen MP4-Datei ausführt und das Video mit annotierten Begrenzungsrahmen in einem OpenCV-Fenster abspielt.

## Voraussetzungen

- Python 3.11+
- Eine lokale MP4-Datei, die Sie analysieren möchten

## Installation

```bash
# Projekt klonen oder kopieren
cd libreyolo-video-viewer

# Virtuelle Umgebung erstellen und aktivieren (empfohlen)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Video ablegen

Kopieren Sie Ihre `.mp4`-Datei in das Verzeichnis `videos/`:

```
videos/
  test.mp4
```

## Verwendung

### Einfacher Lauf mit Viewer

```powershell
python .\analyze_video.py --video ".\videos\test.mp4" --model ".\models\LibreYOLOXs.pt" --viewer
```

### Vollständiges Beispiel

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

### Alle Optionen

| Option | Standard | Beschreibung |
|---|---|---|
| `--video` | erforderlich | Pfad zur MP4-Datei |
| `--model` | `.\models\LibreYOLOXs.pt` | Pfad zur LibreYOLO-Modelldatei |
| `--output-dir` | `./output` | Ausgabeverzeichnis |
| `--classes` | alle | Nur diese Klassennamen (leergetrennt) |
| `--confidence` | `0.45` | Mindest-Konfidenz der Erkennung (0–1) |
| `--sample-rate` | `5` | Erkennungen pro Sekunde |
| `--viewer` | aus | OpenCV-Viewer-Fenster öffnen |
| `--save-annotated-video` | aus | Annotiertes MP4 nach `output/annotated/` speichern |
| `--save-snapshots` / `--no-save-snapshots` | an | Snapshot-JPEGs pro Erkennung |
| `--annotate-snapshots` / `--no-annotate-snapshots` | an | Begrenzungsrahmen auf Snapshots zeichnen |
| `--max-events` | keine | Nach N Ereignissen stoppen (Tests) |
| `--max-frames` | keine | Nach N verarbeiteten Frames stoppen (Tests) |

## Viewer-Steuerung

| Taste | Aktion |
|---|---|
| `q` | Beenden |
| `Leertaste` | Pause / Fortsetzen |
| `s` | Aktuellen annotierten Frame als Snapshot speichern |

## Ausgabe

```
output/
  detections.json          — vollständiger JSON-Bericht
  snapshots/
    000003_person.jpg      — Snapshot pro Erkennungsereignis
    000014_car.jpg
  annotated/
    annotated_test.mp4     — vollständiges annotiertes Video (mit --save-annotated-video)
```

### Struktur von detections.json

```json
{
  "video": { "path", "fps", "frame_count", "width", "height", "duration_seconds" },
  "analysis": { "confidence_threshold", "sample_rate", "classes", ... },
  "outputs": { "json_report", "snapshot_dir", "annotated_video" },
  "summary": { "total_events", "classes_detected": { "person": 2, "dog": 1 } },
  "events": [ { "timestamp", "seconds", "frame_index", "class_name", "confidence", "bbox", "snapshot_path" } ]
}
```

## Tests ausführen

```bash
pytest tests/
```

## Bekannte Einschränkungen

- Die Erkennung läuft standardmäßig nicht auf jedem Frame (`--sample-rate 5` bedeutet bei 30 fps etwa jeden 6. Frame). Begrenzungsrahmen zwischen Inferenz-Frames werden vom letzten Lauf wiederverwendet.
- Keine Deduplizierung: dasselbe Objekt kann in nahen Zeitstempeln als mehrere Ereignisse erscheinen.
- Der OpenCV-Viewer spielt in etwa Originalgeschwindigkeit ab; sehr hochauflösende Videos können ruckeln.
- Annotiertes Video nutzt Codec `mp4v` mit Fallback `avc1`; in manchen Playern ist VLC nötig.

## Geplante Verbesserungen

- Phase 2: Timeline-Scrubber, Sprung zur Erkennung, Klassenfilter-Overlay
- Phase 3: CSV-Export, HTML-Bericht, Deduplizierungsfenster
- Phase 4: FastAPI-Backend + Browser-UI
- Phase 5: Webcam- / RTSP-Liveeingabe
