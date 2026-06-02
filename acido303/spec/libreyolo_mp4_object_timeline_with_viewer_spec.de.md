> Deutsche Übersetzung — siehe auch [libreyolo_mp4_object_timeline_with_viewer_spec.md](libreyolo_mp4_object_timeline_with_viewer_spec.md) (Englisch)

# LibreYOLO MP4-Objektzeitleiste mit kommentiertem Video-Viewer – MVP-Spezifikation

## 1. Projektziel

Erstellen Sie eine lokale Proof-of-Concept-Anwendung, die eine lokale „.mp4“-Videodatei mit [LibreYOLO](https://github.com/LibreYOLO/libreyolo) analysiert, Objekte erkennt und einen einfachen Video-Viewer bereitstellt, in dem der Benutzer das Video mit erkannten Objekten ansehen kann, die durch Begrenzungsrahmen eingerahmt sind.

Die Anwendung sollte außerdem eine Zeitleiste für die Objekterkennung generieren, optionale Snapshots speichern und einen strukturierten JSON-Bericht schreiben.

Die erste Version sollte eine lokale Python-Anwendung sein. Priorisieren Sie eine funktionierende Computer-Vision-Pipeline und einen kommentierten Viewer gegenüber der Webarchitektur.

## 2. Kernanwendungsfall

Der Benutzer lädt manuell ein YouTube-Video als „.mp4“-Datei herunter und möchte es lokal überprüfen.

Die App sollte das Ausführen von Folgendem ermöglichen:```bash
python analyze_video.py --video ./videos/test.mp4 --classes person car dog laptop "cell phone" --confidence 0.45 --sample-rate 5 --viewer --save-annotated-video
```Die App sollte:

1. Öffnen Sie die lokale MP4-Datei.
2. Lesen Sie Metadaten wie FPS, Bildanzahl, Breite, Höhe und Dauer.
3. Führen Sie die LibreYOLO-Objekterkennung für Frames aus.
4. Zeichnen Sie Begrenzungsrahmen, Beschriftungen und Konfidenzwerte über das Video.
5. Zeigen Sie ein lokales Viewer-Fenster mit dem kommentierten Video an.
6. Speichern Sie optional eine kommentierte MP4-Ausgabedatei.
7. Speichern Sie Schnappschüsse für relevante Erkennungen.
8. Erstellen Sie einen „detections.json“-Bericht.
9. Drucken Sie eine für Menschen lesbare Zusammenfassung auf der Konsole.

## 3. MVP-Bereich

### 3.1 Im Geltungsbereich

Implementieren Sie Folgendes:

- Python-CLI-Anwendung.
- Lokaler MP4-Videoeingang.
- OpenCV-basiertes Lesen von Videos.
- OpenCV-basiertes lokales Viewer-Fenster.
- Objekterkennung mit LibreYOLO.
- Bounding-Box-Rendering über Videobilder.
- Etiketten- und Vertrauensdarstellung.
- Konfigurierbarer Vertrauensschwellenwert.
- Optionale Filterung nach Objektklasse.
- Konfigurierbare Bildverarbeitungsrate.
- Optionaler kommentierter MP4-Export.
- Generierung der Ereigniszeitleiste.
- Snapshot-Speicherung.
- JSON-Ausgabe.
- Grundlegende Konsolenprotokollierung.
- Klare Projektstruktur.
- Grundlegende Fehlerbehandlung.
- README mit Einrichtungs- und Nutzungsanweisungen.

### 3.2 Außerhalb des MVP-Bereichs

Implementieren Sie diese noch nicht:

- YouTube-Download.
- Webcam-Eingabe.
- RTSP-Streams.
- FastAPI-Backend.
- React/Next.js-Frontend.
- WebSocket-Live-Fortschritt.
- Datenbankspeicher.
- Benutzerauthentifizierung.
- Docker-Bereitstellung.
- Cloud-Bereitstellung.
- Schulung benutzerdefinierter Modelle.
- Erweiterte Multiobjektverfolgung.
- Multi-Video-Stapelverarbeitung.

## 4. Empfohlene Projektstruktur```text
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
```## 5. Abhängigkeiten

Verwenden Sie Python 3.11+.

Erstellen Sie eine „requirements.txt“ mit mindestens:```txt
libreyolo
opencv-python
numpy
pydantic
pytest
```Wenn LibreYOLO zusätzliche Laufzeitabhängigkeiten erfordert, fügen Sie diese nach der Validierung der ersten Ausführung explizit hinzu.

## 6. CLI-Anforderungen

Der Haupteinstiegspunkt sollte sein:```bash
python analyze_video.py
```Unterstützte Argumente:```bash
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
```Beispiel:```bash
python analyze_video.py \
  --video ./videos/test.mp4 \
  --classes person car dog laptop "cell phone" \
  --confidence 0.45 \
  --sample-rate 5 \
  --viewer \
  --save-annotated-video \
  --output-dir ./output
```## 7. Funktionale Anforderungen

### 7.1 Videolesung

Verwenden Sie OpenCV, um die Videodatei zu öffnen.

Die App muss Folgendes extrahieren:

- Dateipfad.
- FPS.
- Gesamtzahl der Frames.
- Breite.
- Höhe.
- Dauer in Sekunden.

Wenn das Video nicht geöffnet werden kann, scheitern Sie mit einer eindeutigen Fehlermeldung.

### 7.2 Frame-Verarbeitungsstrategie

Für den kommentierten Betrachter sollte die App das Video der Reihe nach anzeigen.

Die Objekterkennung muss jedoch nicht standardmäßig in jedem Frame ausgeführt werden.

Verwenden Sie den Wert „--sample-rate“, um zu entscheiden, wie oft die Inferenz ausgeführt wird.

Beispiel:

- Video-FPS: 30.
- „--sample-rate 5“ bedeutet, dass die Erkennung etwa fünfmal pro Sekunde erfolgt.
- Erkennungsbilder würden ungefähr alle 6 Bilder stattfinden.

Um den Viewer reibungslos zu halten, verwenden Sie die neuesten Erkennungen für Frames zwischen Inferenzläufen wieder.

Das heisst:```text
Frame 0: run detection
Frame 1-5: reuse frame 0 detections
Frame 6: run detection
Frame 7-11: reuse frame 6 detections
```Dies ist für den MVP akzeptabel.

### 7.3 Objekterkennung

Erstellen Sie eine Wrapper-Klasse um LibreYOLO.

Empfohlene Schnittstelle:```python
class ObjectDetector:
    def __init__(self, confidence_threshold: float):
        ...

    def detect(self, frame) -> list[Detection]:
        ...
```Erstellen Sie ein „Erkennungs“-Modell mit:```python
class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]
```Die Implementierung sollte isoliert sein, damit die LibreYOLO-Integration später geändert werden kann, ohne die gesamte App neu zu schreiben.

### 7.4 Klassenfilterung

Wenn der Benutzer „--classes“ angibt, behalten Sie nur Erkennungen bei, deren Klassenname mit einer der angeforderten Klassen übereinstimmt.

Beim Matching sollte die Groß-/Kleinschreibung nicht beachtet werden.

Beispiel:```bash
--classes person dog "cell phone"
```Wenn keine Klassen bereitgestellt werden, behalten Sie alle Klassen bei.

### 7.5 Begrenzungsrahmen-Rendering

Implementieren Sie das Rendering in „src/renderer.py“.

Der Renderer sollte:

- Zeichnen Sie ein Rechteck um jede akzeptierte Erkennung.
- Zeichnen Sie den Klassennamen.
- Zeichnen Sie den Konfidenzwert mit zwei Dezimalstellen ein.
- Halten Sie den Text lesbar.
- Begrenzungsrahmen an Rahmengrenzen festklemmen.
- Vermeiden Sie Abstürze bei fehlerhaften Begrenzungsrahmen.

Empfohlene Schnittstelle:```python
class FrameRenderer:
    def render(self, frame, detections: list[Detection], timestamp: str | None = None):
        ...
```Der gerenderte Frame sollte optional Folgendes enthalten:

- Zeitstempel in der oberen linken Ecke.
- Anzahl der aktuellen Erkennungen.
- FPS-/Verarbeitungsanzeige, sofern leicht verfügbar.

### 7.6 Lokaler Videobetrachter

Implementieren Sie einen lokalen OpenCV-Viewer in „src/viewer.py“.

Wenn „--viewer“ aktiviert ist:

- Öffnen Sie ein Fenster namens „LibreYOLO Video Viewer“.
- Zeigt den aktuellen kommentierten Frame an.
- Behalten Sie nach Möglichkeit ungefähr die ursprüngliche Videowiedergabegeschwindigkeit bei.
- Das Drücken von „q“ sollte beendet werden.
- Durch Drücken der „Leertaste“ sollte die Wiedergabe angehalten/fortgesetzt werden.
- Durch Drücken von „s“ sollte ein Schnappschuss des aktuellen kommentierten Frames gespeichert werden.

Der Viewer benötigt keine komplexe GUI. Für den MVP reicht ein OpenCV-Fenster.

### 7.7 Annotierter Videoexport

Wenn „--save-annotated-video“ aktiviert ist, schreiben Sie eine kommentierte MP4-Datei an:```text
output/annotated/annotated_test.mp4
```Verwenden Sie OpenCV „VideoWriter“.

Das Ausgabevideo sollte:

- Behalten Sie die ursprüngliche Auflösung bei.
- Verwenden Sie nach Möglichkeit die Original-FPS.
- Begrenzungsrahmen und Beschriftungen enthalten.
- In VLC oder einem Standard-Videoplayer abspielbar sein.

Wenn der Codec nicht verfügbar ist, schlagen Sie ordnungsgemäß fehl und geben Sie eine hilfreiche Meldung aus.

### 7.8 Ereigniserstellung

Jede gültige Erkennung in einem Inferenzrahmen sollte zu einem Ereignis werden.

Erstellen Sie keine doppelten Ereignisse für jeden angezeigten Frame, wenn Erkennungen zwischen Inferenzläufen wiederverwendet werden.

Veranstaltungsmodell:```python
class DetectionEvent(BaseModel):
    timestamp: str
    seconds: float
    frame_index: int
    class_name: str
    confidence: float
    bbox: list[float]
    snapshot_path: str | None
```Zeitstempelformat:```text
HH:MM:SS
```Beispielveranstaltung:```json
{
  "timestamp": "00:01:14",
  "seconds": 74.0,
  "frame_index": 2220,
  "class_name": "dog",
  "confidence": 0.82,
  "bbox": [120.0, 55.0, 310.0, 280.0],
  "snapshot_path": "output/snapshots/000074_dog.jpg"
}
```### 7.9 Snapshot-Speicherung

Wenn eine Erkennung die Filterung besteht:

- Speichern Sie ein Schnappschussbild.
- Verwenden Sie den Zeitstempel und den Klassennamen im Dateinamen.
- Vermeiden Sie ungültige Dateinamenzeichen.
- Wenn mehrere Objekte derselben Klasse zum gleichen Zeitstempel erkannt werden, fügen Sie einen Zähler hinzu.

Beispieldateinamen:```text
output/snapshots/000003_person.jpg
output/snapshots/000014_car.jpg
output/snapshots/000074_dog.jpg
output/snapshots/000074_person_2.jpg
```Wenn „--annotate-snapshots“ aktiviert ist, zeichnen Sie Begrenzungsrahmen und Beschriftungen auf dem Schnappschuss.

### 7.10 JSON-Bericht

Erstellen:```text
output/detections.json
```Der JSON sollte Videometadaten, Analyseeinstellungen, Ausgabepfade, Zusammenfassungen und Ereignisse enthalten.

Beispiel:```json
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
```### 7.11 Konsolenausgabe

Die App sollte nützliche Fortschrittsinformationen ausdrucken:```text
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
```## 8. Nichtfunktionale Anforderungen

### 8.1 Einfachheit

Halten Sie den MVP einfach. Priorisieren Sie eine funktionierende lokale Pipeline gegenüber der Komplexität der Architektur.

### 8.2 Erweiterbarkeit

Entwerfen Sie den Code so, dass später Folgendes hinzugefügt werden kann:

- FastAPI-Upload-Endpunkt.
- Web-UI-Zeitleiste.
- Browserbasierter Videoplayer.
- Webcam-Eingabe.
- RTSP-Eingang.
- Objektverfolgung.
- Ereignisdeduplizierung.
- Suche nach Objektklasse.
- Export nach CSV.

### 8.3 Leistung

Die Standardverarbeitung sollte nicht bei jedem Frame eine Erkennung durchführen, es sei denn, dies ist explizit konfiguriert.

Der Viewer sollte aktuelle Erkennungen zwischen Inferenzrahmen wiederverwenden.

Die App sollte lange Videos unterstützen, indem sie unnötigen Speicherverbrauch vermeidet. Laden Sie nicht das gesamte Video in den Speicher.

### 8.4 Fehlerbehandlung

Behandeln Sie mindestens:

- Videodatei nicht gefunden.
- Video kann nicht geöffnet werden.
- Ungültige Abtastrate.
- Ungültiger Konfidenzwert.
- Ausgabeverzeichnis kann nicht erstellt werden.
- LibreYOLO-Modelllade- oder Inferenzfehler.
- OpenCV-Viewer kann nicht geöffnet werden.
- Der VideoWriter-Codec ist nicht verfügbar.

### 8.5 Sicherheit und Schutz

Dies ist ein lokales Tool. Laden Sie keine externen Inhalte im MVP herunter.

Der Benutzer ist dafür verantwortlich, eine lokale MP4-Datei bereitzustellen, zu deren Analyse er berechtigt ist.

Fügen Sie im MVP keine Netzwerkdienste hinzu und öffnen Sie keine Ports.

## 9. Implementierungshinweise

### 9.1 LibreYOLO isoliert halten

Implementieren Sie LibreYOLO-spezifischen Code nur in:```text
src/detector.py
```Der Rest der App sollte mit internen „Erkennungs“-Objekten funktionieren.

### 9.2 Rendering isoliert halten

Implementieren Sie die gesamte Zeichnungslogik nur in:```text
src/renderer.py
```Dadurch wird die Erkennung von der visuellen Darstellung getrennt.

### 9.3 Vermeiden Sie Overengineering

Nicht hinzufügen:

- Sellerie.
- Kafka.
- RabbitMQ.
- Datenbanken.
- Docker Compose.
- Authentifizierung.
- Frontend-Frameworks.

Dies ist ein lokaler Proof-of-Concept.

### 9.4 Ereignisdeduplizierung optional

Für MVP ist es akzeptabel, wenn dasselbe Objekt über benachbarte Zeitstempel hinweg mehrmals erkannt wird.

Optionale Verbesserung:

- Fügen Sie „--dedupe-window 3“ hinzu, um zu vermeiden, dass dieselbe Klasse zu oft wiederholt wird.
- Beispiel: Wenn „Person“ um 00:03, 00:04 und 00:05 erscheint, behalten Sie nur das erste Ereignis innerhalb eines 3-Sekunden-Fensters bei.

Implementieren Sie dies nur, wenn die Basispipeline und der Viewer bereits funktionieren.

## 10. Testanforderungen

Fügen Sie leichte Tests für reine Funktionen hinzu.

Testbeispiele:

### 10.1 Zeitformatierung

Eingang:```python
format_seconds(74)
```Erwartet:```text
00:01:14
```### 10.2 Klassenfilterung

Gegebene Klassen:```python
["person", "dog"]
```Eine Erkennung mit der Klasse „Person“ sollte akzeptiert werden.

Eine Erkennung mit der Klasse „Auto“ sollte abgelehnt werden.

### 10.3 Ereigniszusammenfassung

Gegebene Ereignisse:```text
person, person, dog
```Die Zusammenfassung sollte Folgendes zurückgeben:```json
{
  "person": 2,
  "dog": 1
}
```### 10.4 Bounding-Box-Klemmung

Bei einer Erkennung mit Koordinaten außerhalb der Rahmengrenzen sollte der Renderer die Koordinaten festhalten, damit das Zeichnen nicht abstürzt.

Versuchen Sie nicht, die LibreYOLO-Inferenz in MVP-Tests einem Unit-Test zu unterziehen.

## 11. README-Anforderungen

Erstellen Sie eine „README.md“ mit:

- Projektbeschreibung.
- Anforderungen.
- Installationsschritte.
- So platzieren Sie ein Video in „./videos“.
- Beispielbefehle.
- Viewer-Steuerelemente.
- Erklärung zur Ausgabe.
- Bekannte Einschränkungen.
- Zukünftige Verbesserungen.

Beispiel für einen README-Befehl:```bash
python analyze_video.py --video ./videos/test.mp4 --classes person dog car --confidence 0.45 --sample-rate 5 --viewer --save-annotated-video
```Viewer-Steuerelemente:```text
q      quit
space  pause/resume
s      save current annotated frame
```## 12. Akzeptanzkriterien

Das MVP ist abgeschlossen, wenn:

1. Ein Benutzer kann eine MP4-Datei in „./videos“ platzieren.
2. Der Benutzer kann „pythonanalysate_video.py --video ./videos/test.mp4 --viewer“ ausführen.
3. Ein lokaler Viewer öffnet und spielt das Video ab.
4. Erkannte Objekte werden mit Begrenzungsrahmen eingerahmt.
5. Beschriftungen und Konfidenzwerte sind sichtbar.
6. Der Viewer unterstützt die Steuerelemente „Beenden“, „Pause/Fortsetzen“ und „Bild speichern“.
7. Die App speichert optional eine kommentierte MP4-Datei, wenn „--save-annotated-video“ aktiviert ist.
8. Die App speichert Schnappschüsse für Erkennungen.
9. Die App schreibt „output/detections.json“.
10. Der JSON enthält Videometadaten, Analyseeinstellungen, Ausgabepfade, Zusammenfassungen und Ereignisse.
11. Die Konsolenausgabe zeigt deutlich den Fortschritt und die Position des Endergebnisses.
12. Grundlegende Tests bestehen mit „pytest“.
13. In der README-Datei wird erklärt, wie die App ausgeführt und der Viewer verwendet wird.

## 13. Ideen für die zukünftige Phase

Nachdem das MVP funktioniert, sollten Sie Folgendes in Betracht ziehen:

### Phase 2 – Besserer lokaler Viewer

- Timeline-Scrubber.
- Zur nächsten Erkennung springen.
- Begrenzungsrahmen ein-/ausschalten.
- Filtern Sie Klassen während der Anzeige.
- Seitenwand mit aktuellen Erkennungen.

### Phase 3 – Bessere Berichte

- CSV-Export.
- Deduplizierungsfenster.
- Nur einen Zeitbereich verarbeiten.
- Erstellen Sie einen Kontaktabzug mit Schnappschüssen.
- HTML-Bericht erstellen.

### Phase 4 – Webanwendung

- FastAPI-Backend.
- MP4 hochladen.
- Hintergrundanalyseauftrag.
- WebSocket-Fortschrittsaktualisierungen.
- Browserbasierter Videoplayer.
- Timeline-Benutzeroberfläche.
- Schnappschuss-Galerie.
- Filtern Sie Erkennungen nach Klasse.

### Phase 5 – Echtzeitquellen

- Webcam-Eingabe.
- RTSP-Streams.
- Live-Event-Feed.
- Alarmregeln.

### Phase 6 – Produktausrichtung

- Suchen Sie in Videos nach Objektklasse.
- Analysieren Sie lange Videos und erstellen Sie Objektzeitleisten.
- Generieren Sie automatische Zusammenfassungen.
- Kombinieren Sie Objekterkennung mit OCR oder Audiotranskription.

## 14. Entwicklungsanweisungen für Claude

Bitte setzen Sie dieses Projekt schrittweise um.

Empfohlene Reihenfolge:

1. Projektstruktur erstellen.
2. Fügen Sie Anforderungen hinzu.
3. Implementieren Sie Datenmodelle.
4. Implementieren Sie Zeitprogramme.
5. Implementieren Sie das Lesen von Videometadaten.
6. Implementieren Sie eine Frame-Sampling-Schleife.
7. Stub-Detektor, falls erforderlich.
8. Integrieren Sie LibreYOLO in „src/detector.py“.
9. Implementieren Sie Filterung und Ereigniserstellung.
10. Implementieren Sie einen Renderer für Begrenzungsrahmen.
11. Implementieren Sie den OpenCV-Viewer.
12. Implementieren Sie einen optionalen Video-Writer mit Anmerkungen.
13. Implementieren Sie den Snapshot-Writer.
14. Implementieren Sie den JSON-Berichtsersteller.
15. CLI-Argumente hinzufügen.
16. README hinzufügen.
17. Fügen Sie grundlegende Tests hinzu.

Halten Sie die Implementierungsschritte klein und leicht zu überprüfen.

Führen Sie kein Web-Framework ein, bis bestätigt wurde, dass der MVP des lokalen kommentierten Viewers funktioniert.