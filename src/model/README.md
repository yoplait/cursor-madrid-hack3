# model

Capa de visión con [LibreYOLO](https://www.libreyolo.com/docs).

Scripts de ejemplo:

- `service.py` — capa reutilizable (`detect`, `result_to_dict`)
- `detect.py` — smoke test detección
- `segment.py` — segmentación RF-DETR

```bash
# desde la raíz del repo
make detect
make segment
```

Los pesos se resuelven con cwd en `vendor/libreyolo/` (ver `Makefile`).
