# LibreYOLO Video Viewer

Interface en ligne de commande Python locale qui exécute la [détection d'objets LibreYOLO](https://github.com/LibreYOLO/libreyolo) sur un fichier MP4 local et lit la vidéo avec des boîtes englobantes annotées dans une fenêtre OpenCV.

## Prérequis

- Python 3.11+
- Un fichier MP4 local à analyser

## Installation

```bash
# Cloner ou copier le projet
cd libreyolo-video-viewer

# Créer et activer un environnement virtuel (recommandé)
python -m venv .venv
# Windows :
.venv\Scripts\activate
# macOS / Linux :
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Placer une vidéo

Copiez votre fichier `.mp4` dans le répertoire `videos/` :

```
videos/
  test.mp4
```

## Utilisation

### Exécution de base avec la visionneuse

```powershell
python .\analyze_video.py --video ".\videos\test.mp4" --model ".\models\LibreYOLOXs.pt" --viewer
```

### Exemple complet

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

### Toutes les options

| Option | Par défaut | Description |
|---|---|---|
| `--video` | obligatoire | Chemin vers le fichier MP4 |
| `--model` | `.\models\LibreYOLOXs.pt` | Chemin vers le fichier modèle LibreYOLO |
| `--output-dir` | `./output` | Répertoire de sortie |
| `--classes` | toutes | Filtrer sur ces noms de classes (séparés par des espaces) |
| `--confidence` | `0.45` | Seuil de confiance minimal (0–1) |
| `--sample-rate` | `5` | Fréquence d'exécution de la détection (par seconde) |
| `--viewer` | désactivé | Ouvrir une fenêtre de visionneuse OpenCV |
| `--save-annotated-video` | désactivé | Enregistrer le MP4 annoté dans `output/annotated/` |
| `--save-snapshots` / `--no-save-snapshots` | activé | Enregistrer des instantanés JPEG par détection |
| `--annotate-snapshots` / `--no-annotate-snapshots` | activé | Dessiner les boîtes englobantes sur les instantanés |
| `--max-events` | aucune | Arrêter après N événements (utile pour les tests) |
| `--max-frames` | aucune | Arrêter après N images traitées (utile pour les tests) |

## Contrôles de la visionneuse

| Touche | Action |
|---|---|
| `q` | Quitter |
| `espace` | Pause / Reprise |
| `s` | Enregistrer l'image annotée courante comme instantané |

## Sorties

```
output/
  detections.json          — rapport JSON complet
  snapshots/
    000003_person.jpg      — instantané par événement de détection
    000014_car.jpg
  annotated/
    annotated_test.mp4     — vidéo annotée complète (si --save-annotated-video)
```

### Structure de detections.json

```json
{
  "video": { "path", "fps", "frame_count", "width", "height", "duration_seconds" },
  "analysis": { "confidence_threshold", "sample_rate", "classes", ... },
  "outputs": { "json_report", "snapshot_dir", "annotated_video" },
  "summary": { "total_events", "classes_detected": { "person": 2, "dog": 1 } },
  "events": [ { "timestamp", "seconds", "frame_index", "class_name", "confidence", "bbox", "snapshot_path" } ]
}
```

## Exécuter les tests

```bash
pytest tests/
```

## Limitations connues

- La détection ne s'exécute pas sur chaque image par défaut (`--sample-rate 5` signifie environ une image sur six à 30 ips). Les boîtes englobantes entre les images d'inférence sont réutilisées depuis la dernière exécution.
- Pas de déduplication : le même objet peut apparaître comme plusieurs événements sur des horodatages proches.
- La visionneuse OpenCV lit à peu près à la vitesse d'origine ; les vidéos très haute résolution peuvent ralentir.
- La vidéo annotée utilise le codec `mp4v` avec repli sur `avc1` ; la lecture dans certains lecteurs peut nécessiter VLC.

## Améliorations futures

- Phase 2 : curseur de timeline, saut vers la détection suivante, filtre de classes en superposition
- Phase 3 : export CSV, rapport HTML, fenêtre de déduplication
- Phase 4 : backend FastAPI + interface navigateur
- Phase 5 : entrée webcam / flux RTSP en direct
