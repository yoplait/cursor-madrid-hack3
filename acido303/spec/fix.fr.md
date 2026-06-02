Corriger l'erreur de chargement du modèle LibreYOLO.

Erreur actuelle :

LibreYOLO() missing 1 required positional argument: 'model\_path'

L'application ne doit pas appeler LibreYOLO() sans arguments.

Ajouter un argument CLI obligatoire ou avec valeur par défaut :

\--model

Valeur par défaut :

LibreYOLOXs.pt

Puis initialiser le modèle ainsi :

```python
from libreyolo import LibreYOLO

model = LibreYOLO(args.model)
```

Le README doit montrer des exemples PowerShell utilisant :

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

Améliorer aussi le message d'erreur lorsque le modèle ne peut pas être chargé. Il doit indiquer :

« Échec du chargement du modèle LibreYOLO. Veuillez fournir un chemin de modèle valide avec --model. »

Ne pas revenir silencieusement à LibreYOLO() sans modèle.
