# model

Capa de visión con [LibreYOLO](https://www.libreyolo.com/docs).

Scripts de ejemplo:

- `detect.py` — detección con YOLO9t
- `segment.py` — segmentación con RF-DETR

```bash
# desde la raíz del repo
make detect
make segment
```

Los pesos se resuelven con cwd en `vendor/libreyolo/` (ver `Makefile`).
