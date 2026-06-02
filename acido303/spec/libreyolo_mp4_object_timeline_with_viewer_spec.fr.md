# Chronologie d'objets MP4 LibreYOLO avec visionneuse vidéo annotée — Spécification MVP

## 1. Objectif du projet

Construire une application locale de preuve de concept qui analyse un fichier vidéo `.mp4` local avec [LibreYOLO](https://github.com/LibreYOLO/libreyolo), détecte des objets et fournit une visionneuse vidéo simple où l'utilisateur peut regarder la vidéo avec les objets détectés encadrés par des boîtes englobantes.

L'application doit également générer une chronologie de détection d'objets, enregistrer des instantanés optionnels et écrire un rapport JSON structuré.

La première version doit être une application Python locale. Prioriser un pipeline de vision par ordinateur fonctionnel et une visionneuse annotée plutôt qu'une architecture web.

## 2. Cas d'usage principal

L'utilisateur télécharge manuellement une vidéo YouTube au format `.mp4` et souhaite l'inspecter localement.

L'application doit permettre d'exécuter :

```bash
python analyze_video.py --video ./videos/test.mp4 --classes person car dog laptop "cell phone" --confidence 0.45 --sample-rate 5 --viewer --save-annotated-video
```

L'application doit :

1. Ouvrir le fichier MP4 local.
2. Lire les métadonnées : IPS, nombre d'images, largeur, hauteur et durée.
3. Exécuter la détection d'objets LibreYOLO sur les images.
4. Dessiner les boîtes englobantes, les étiquettes et les scores de confiance sur la vidéo.
5. Afficher une fenêtre de visionneuse locale avec la vidéo annotée.
6. Enregistrer optionnellement un fichier MP4 annoté en sortie.
7. Enregistrer des instantanés pour les détections pertinentes.
8. Générer un rapport `detections.json`.
9. Afficher un résumé lisible dans la console.

## 3. Périmètre MVP

### 3.1 Dans le périmètre

Implémenter les éléments suivants :

- Application CLI Python.
- Entrée vidéo MP4 locale.
- Lecture vidéo basée sur OpenCV.
- Fenêtre de visionneuse locale basée sur OpenCV.
- Détection d'objets avec LibreYOLO.
- Rendu des boîtes englobantes sur les images vidéo.
- Rendu des étiquettes et de la confiance.
- Seuil de confiance configurable.
- Filtrage optionnel par classe d'objet.
- Fréquence de traitement des images configurable.
- Export MP4 annoté optionnel.
- Génération de chronologie d'événements.
- Enregistrement d'instantanés.
- Sortie JSON.
- Journalisation console de base.
- Structure de projet claire.
- Gestion d'erreurs de base.
- README avec instructions d'installation et d'utilisation.

### 3.2 Hors périmètre MVP

Ne pas implémenter pour l'instant :

- Téléchargement YouTube.
- Entrée webcam.
- Flux RTSP.
- Backend FastAPI.
- Frontend React/Next.js.
- Progression en direct via WebSocket.
- Stockage en base de données.
- Authentification utilisateur.
- Déploiement Docker.
- Déploiement cloud.
- Entraînement de modèles personnalisés.
- Suivi multi-objets avancé.
- Traitement par lots de plusieurs vidéos.

## 4. Structure de projet recommandée

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

## 5. Dépendances

Utiliser Python 3.11+.

Créer un `requirements.txt` contenant au minimum :

```txt
libreyolo
opencv-python
numpy
pydantic
pytest
```

Si LibreYOLO nécessite des dépendances d'exécution supplémentaires, les ajouter explicitement après validation du premier lancement.

## 6. Exigences CLI

Le point d'entrée principal doit être :

```bash
python analyze_video.py
```

Arguments pris en charge :

```bash
--video                 Obligatoire. Chemin vers le fichier MP4 local.
--output-dir            Optionnel. Par défaut : ./output
--classes               Optionnel. Un ou plusieurs noms de classes à conserver.
--confidence            Optionnel. Par défaut : 0.45
--sample-rate           Optionnel. Fréquence de détection en images par seconde. Par défaut : 5
--viewer                Option booléenne. Afficher une fenêtre OpenCV locale. Par défaut : false
--save-annotated-video  Option booléenne. Enregistrer le MP4 annoté. Par défaut : false
--save-snapshots        Option booléenne. Par défaut : true
--annotate-snapshots    Option booléenne. Instantanés avec boîtes englobantes. Par défaut : true
--max-events            Optionnel. Arrêter après N événements. Utile pour les tests.
--max-frames            Optionnel. Arrêter après N images traitées. Utile pour les tests.
```

Exemple :

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

## 7. Exigences fonctionnelles

### 7.1 Lecture vidéo

Utiliser OpenCV pour ouvrir le fichier vidéo.

L'application doit extraire :

- Chemin du fichier.
- IPS.
- Nombre total d'images.
- Largeur.
- Hauteur.
- Durée en secondes.

Si la vidéo ne peut pas être ouverte, échouer avec un message d'erreur clair.

### 7.2 Stratégie de traitement des images

Pour la visionneuse annotée, l'application doit afficher la vidéo dans l'ordre.

Cependant, la détection d'objets n'a pas besoin de s'exécuter sur chaque image par défaut.

Utiliser la valeur `--sample-rate` pour décider de la fréquence d'inférence.

Exemple :

- IPS vidéo : 30.
- `--sample-rate 5` signifie environ 5 détections par seconde.
- Les images de détection seraient environ toutes les 6 images.

Pour garder la visionneuse fluide, réutiliser les détections les plus récentes pour les images entre les inférences.

Cela signifie :

```text
Image 0 : exécuter la détection
Images 1-5 : réutiliser les détections de l'image 0
Image 6 : exécuter la détection
Images 7-11 : réutiliser les détections de l'image 6
```

C'est acceptable pour le MVP.

### 7.3 Détection d'objets

Créer une classe wrapper autour de LibreYOLO.

Interface suggérée :

```python
class ObjectDetector:
    def __init__(self, confidence_threshold: float):
        ...

    def detect(self, frame) -> list[Detection]:
        ...
```

Créer un modèle `Detection` avec :

```python
class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]  # [x1, y1, x2, y2]
```

L'implémentation doit être isolée pour pouvoir changer l'intégration LibreYOLO plus tard sans réécrire toute l'application.

### 7.4 Filtrage par classe

Si l'utilisateur fournit `--classes`, ne conserver que les détections dont le nom de classe correspond à une des classes demandées.

La correspondance doit être insensible à la casse.

Exemple :

```bash
--classes person dog "cell phone"
```

Si aucune classe n'est fournie, conserver toutes les classes.

### 7.5 Rendu des boîtes englobantes

Implémenter le rendu dans `src/renderer.py`.

Le renderer doit :

- Dessiner un rectangle autour de chaque détection acceptée.
- Dessiner le nom de la classe.
- Dessiner la confiance avec deux décimales.
- Garder le texte lisible.
- Limiter les boîtes englobantes aux bords de l'image.
- Éviter les plantages sur des boîtes mal formées.

Interface suggérée :

```python
class FrameRenderer:
    def render(self, frame, detections: list[Detection], timestamp: str | None = None):
        ...
```

L'image rendue peut inclure optionnellement :

- Horodatage dans le coin supérieur gauche.
- Nombre de détections actuelles.
- Indicateur IPS / traitement si facilement disponible.

### 7.6 Visionneuse vidéo locale

Implémenter une visionneuse OpenCV locale dans `src/viewer.py`.

Lorsque `--viewer` est activé :

- Ouvrir une fenêtre nommée `Visionneuse vidéo LibreYOLO`.
- Afficher l'image annotée courante.
- Conserver approximativement la vitesse de lecture d'origine si possible.
- La touche `q` doit quitter.
- La barre d'espace doit mettre en pause / reprendre.
- La touche `s` doit enregistrer un instantané de l'image annotée courante.

La visionneuse n'a pas besoin d'une interface complexe. Une fenêtre OpenCV suffit pour le MVP.

### 7.7 Export vidéo annotée

Lorsque `--save-annotated-video` est activé, écrire un MP4 annoté vers :

```text
output/annotated/annotated_test.mp4
```

Utiliser `VideoWriter` d'OpenCV.

La vidéo de sortie doit :

- Conserver la résolution d'origine.
- Utiliser les IPS d'origine si possible.
- Contenir les boîtes englobantes et les étiquettes.
- Être lisible dans VLC ou un lecteur standard.

Si le codec n'est pas disponible, échouer proprement et afficher un message utile.

### 7.8 Création d'événements

Chaque détection valide sur une image d'inférence doit devenir un événement.

Ne pas créer d'événements en double pour chaque image affichée lorsque les détections sont réutilisées entre les inférences.

Modèle d'événement :

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

Format d'horodatage :

```text
HH:MM:SS
```

Exemple d'événement :

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

### 7.9 Enregistrement d'instantanés

Lorsqu'une détection passe le filtrage :

- Enregistrer une image instantanée.
- Utiliser l'horodatage et le nom de classe dans le nom de fichier.
- Éviter les caractères invalides dans les noms de fichier.
- Si plusieurs objets de la même classe sont détectés au même horodatage, ajouter un compteur.

Exemples de noms de fichier :

```text
output/snapshots/000003_person.jpg
output/snapshots/000014_car.jpg
output/snapshots/000074_dog.jpg
output/snapshots/000074_person_2.jpg
```

Si `--annotate-snapshots` est activé, dessiner les boîtes englobantes et les étiquettes sur l'instantané.

### 7.10 Rapport JSON

Créer :

```text
output/detections.json
```

Le JSON doit contenir les métadonnées vidéo, les paramètres d'analyse, les chemins de sortie, le résumé et les événements.

Exemple :

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

### 7.11 Sortie console

L'application doit afficher des informations de progression utiles :

```text
Analyse de la vidéo : ./videos/test.mp4
FPS: 30.0
Résolution : 1920x1080
Durée : 00:02:30
Fréquence d'échantillonnage : 5 images/s
Seuil de confiance : 0.45
Classes : person, car, dog, laptop, cell phone
Visionneuse : activée
Export vidéo annotée : activé

[00:00:03] person détecté, confiance 0.91
[00:00:14] car détecté, confiance 0.84
[00:01:14] dog détecté, confiance 0.82

Terminé.
Nombre total d'événements : 3
Rapport enregistré dans : ./output/detections.json
Instantanés enregistrés dans : ./output/snapshots
Vidéo annotée enregistrée dans : ./output/annotated/annotated_test.mp4
```

## 8. Exigences non fonctionnelles

### 8.1 Simplicité

Garder le MVP simple. Prioriser un pipeline local fonctionnel plutôt que la complexité architecturale.

### 8.2 Extensibilité

Concevoir le code pour pouvoir ajouter plus tard :

- Point de terminaison d'upload FastAPI.
- Chronologie dans l'interface web.
- Lecteur vidéo dans le navigateur.
- Entrée webcam.
- Entrée RTSP.
- Suivi d'objets.
- Déduplication d'événements.
- Recherche par classe d'objet.
- Export CSV.

### 8.3 Performances

Par défaut, ne pas exécuter la détection sur chaque image sauf configuration explicite.

La visionneuse doit réutiliser les détections récentes entre les images d'inférence.

L'application doit supporter les longues vidéos en évitant l'utilisation mémoire inutile. Ne pas charger toute la vidéo en mémoire.

### 8.4 Gestion des erreurs

Gérer au minimum :

- Fichier vidéo introuvable.
- Vidéo impossible à ouvrir.
- Fréquence d'échantillonnage invalide.
- Valeur de confiance invalide.
- Impossible de créer le répertoire de sortie.
- Erreurs de chargement ou d'inférence du modèle LibreYOLO.
- Impossible d'ouvrir la visionneuse OpenCV.
- Codec VideoWriter indisponible.

### 8.5 Sécurité

Outil local. Ne pas télécharger de contenu externe dans le MVP.

L'utilisateur est responsable de fournir un fichier MP4 local qu'il a le droit d'analyser.

Ne pas ajouter de services réseau ni ouvrir de ports dans le MVP.

## 9. Notes d'implémentation

### 9.1 Isoler LibreYOLO

Implémenter le code spécifique à LibreYOLO uniquement dans :

```text
src/detector.py
```

Le reste de l'application doit utiliser des objets `Detection` internes.

### 9.2 Isoler le rendu

Implémenter toute la logique de dessin uniquement dans :

```text
src/renderer.py
```

Cela sépare la détection de la présentation visuelle.

### 9.3 Éviter la sur-ingénierie

Ne pas ajouter :

- Celery.
- Kafka.
- RabbitMQ.
- Databases.
- Docker Compose.
- Authentication.
- Frontend frameworks.

Il s'agit d'une preuve de concept locale.

### 9.4 Déduplication d'événements optionnelle

Pour le MVP, il est acceptable que le même objet soit détecté plusieurs fois sur des horodatages proches.

Amélioration optionnelle :

- Ajouter `--dedupe-window 3` pour éviter de répéter la même classe trop souvent.
- Exemple : si `person` apparaît à 00:03, 00:04 et 00:05, ne garder que le premier événement dans une fenêtre de 3 secondes.

Ne pas implémenter cela tant que le pipeline de base et la visionneuse ne fonctionnent pas.

## 10. Exigences de tests

Ajouter des tests légers pour les fonctions pures.

Exemples de tests :

### 10.1 Formatage du temps

Entrée :

```python
format_seconds(74)
```

Résultat attendu :

```text
00:01:14
```

### 10.2 Filtrage par classe

Classes données :

```python
["person", "dog"]
```

Une détection avec la classe `Person` doit être acceptée.

Une détection avec la classe `car` doit être rejetée.

### 10.3 Résumé des événements

Événements donnés :

```text
person, person, dog
```

Le résumé doit retourner :

```json
{
  "person": 2,
  "dog": 1
}
```

### 10.4 Limitation des boîtes englobantes

Pour une détection avec des coordonnées hors de l'image, le renderer doit limiter les coordonnées pour éviter un plantage au dessin.

Ne pas tester unitairement l'inférence LibreYOLO dans les tests MVP.

## 11. Exigences README

Créer un `README.md` avec :

- Description du projet.
- Prérequis.
- Étapes d'installation.
- Comment placer une vidéo dans `./videos`.
- Exemples de commandes.
- Contrôles de la visionneuse.
- Explication des sorties.
- Limitations connues.
- Améliorations futures.

Exemple de commande README :

```bash
python analyze_video.py --video ./videos/test.mp4 --classes person dog car --confidence 0.45 --sample-rate 5 --viewer --save-annotated-video
```

Contrôles de la visionneuse :

```text
q      quitter
espace pause/reprise
s      enregistrer l'image annotée courante
```

## 12. Critères d'acceptation

Le MVP est terminé lorsque :

1. Un utilisateur peut placer un fichier MP4 dans `./videos`.
2. L'utilisateur peut exécuter `python analyze_video.py --video ./videos/test.mp4 --viewer`.
3. Une visionneuse locale s'ouvre et lit la vidéo.
4. Les objets détectés sont encadrés par des boîtes englobantes.
5. Les étiquettes et valeurs de confiance sont visibles.
6. La visionneuse prend en charge quitter, pause/reprise et enregistrement d'image.
7. L'application enregistre optionnellement un MP4 annoté lorsque `--save-annotated-video` est activé.
8. L'application enregistre des instantanés pour les détections.
9. L'application écrit `output/detections.json`.
10. Le JSON contient métadonnées, paramètres, chemins, résumé et événements.
11. La console affiche clairement la progression et l'emplacement des résultats.
12. Les tests de base passent avec `pytest`.
13. Le README explique comment lancer l'application et utiliser la visionneuse.

## 13. Idées de phases futures

Une fois le MVP fonctionnel, envisager :

### Phase 2 — Meilleure visionneuse locale

- Curseur de chronologie.
- Saut vers la détection suivante.
- Activer/désactiver les boîtes englobantes.
- Filtrer les classes pendant la lecture.
- Panneau latéral avec les détections courantes.

### Phase 3 — Meilleurs rapports

- Export CSV.
- Fenêtre de déduplication.
- Traiter uniquement une plage horaire.
- Générer une planche-contact d'instantanés.
- Générer un rapport HTML.

### Phase 4 — Application web

- Backend FastAPI.
- Upload MP4.
- Tâche d'analyse en arrière-plan.
- Mises à jour de progression WebSocket.
- Lecteur vidéo dans le navigateur.
- Interface de chronologie.
- Galerie d'instantanés.
- Filtrer les détections par classe.

### Phase 5 — Sources en temps réel

- Entrée webcam.
- Flux RTSP.
- Flux d'événements en direct.
- Règles d'alerte.

### Phase 6 — Orientation produit

- Rechercher dans les vidéos par classe d'objet.
- Analyser de longues vidéos et créer des chronologies d'objets.
- Générer des résumés automatiques.
- Combiner détection d'objets avec OCR ou transcription audio.

## 14. Instructions de développement pour Claude

Veuillez implémenter ce projet de manière incrémentale.

Ordre recommandé :

1. Créer la structure du projet.
2. Ajouter les dépendances.
3. Implémenter les modèles de données.
4. Implémenter les utilitaires temporels.
5. Implémenter la lecture des métadonnées vidéo.
6. Implémenter la boucle d'échantillonnage des images.
7. Stub du détecteur si nécessaire.
8. Intégrer LibreYOLO dans `src/detector.py`.
9. Implémenter le filtrage et la création d'événements.
10. Implémenter le renderer pour les boîtes englobantes.
11. Implémenter la visionneuse OpenCV.
12. Implémenter l'écriture vidéo annotée optionnelle.
13. Implémenter l'écriture d'instantanés.
14. Implémenter l'écriture du rapport JSON.
15. Ajouter les arguments CLI.
16. Ajouter le README.
17. Ajouter les tests de base.

Garder les étapes d'implémentation petites et faciles à revoir.

Ne pas introduire de framework web tant que le MVP de visionneuse annotée locale n'est pas validé.
