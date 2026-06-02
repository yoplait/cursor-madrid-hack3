# LibreYOLO-Modellladefehler beheben

> Deutsche Übersetzung — siehe auch [fix.md](fix.md) (Englisch)

Beheben Sie den Fehler beim Laden des LibreYOLO-Modells.

Aktueller Fehler:

```
LibreYOLO() missing 1 required positional argument: 'model_path'
```

Die Anwendung darf `LibreYOLO()` nicht ohne Argumente aufrufen.

Fügen Sie ein erforderliches oder standardmäßiges CLI-Argument hinzu:

```
--model
```

Standardwert:

```
LibreYOLOXs.pt
```

Initialisieren Sie das Modell wie folgt:

```python
from libreyolo import LibreYOLO

model = LibreYOLO(args.model)
```

Die README muss PowerShell-Beispiele mit folgendem Muster zeigen:

```powershell
python .\analyze_video.py `
  --video ".\videos\Fortnite_20260124123317.mp4" `
  --model "LibreYOLOXs.pt" `
  --classes person car weapon `
  --confidence 0.45 `
  --sample-rate 5 `
  --viewer `
  --save-annotated-video
```

Verbessern Sie außerdem die Fehlermeldung, wenn das Modell nicht geladen werden kann. Sie sollte lauten:

> „LibreYOLO-Modell konnte nicht geladen werden. Bitte einen gültigen Modellpfad mit --model angeben.“

Führen Sie keinen stillen Fallback auf `LibreYOLO()` ohne Modell durch.
