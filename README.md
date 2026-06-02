# Cursor Madrid Hackathon #3

Repositorio para el Hackathon #3 de Cursor en Madrid (track LibreYOLO).

## Estructura

Como [cursor-madrid-hack3](https://github.com/yoplait/cursor-madrid-hack3), más el código del equipo bajo `src/`:

```
hack3/
├── ejemplos/          # recursos YOLO del hackathon
├── libreria/          # enlaces LibreYOLO
├── linkedin/
├── src/
│   ├── frontend/      # UI / visualización
│   ├── backend/       # API / servicios
│   ├── infra/         # Docker, despliegue, CI
│   └── model/         # inferencia LibreYOLO (detect, segment)
├── vendor/libreyolo/  # LibreYOLO desde source (no commitear)
└── .venv/             # entorno virtual
```

## Setup (primera vez)

Requisitos: Python 3.10+, git.

```bash
chmod +x scripts/setup_libreyolo.sh
./scripts/setup_libreyolo.sh
```

O manualmente:

```bash
git clone -b dev https://github.com/Libre-YOLO/libreyolo.git vendor/libreyolo
make setup
make verify   # debe imprimir: LibreYOLO ready
```

## Uso

Activa el venv:

```bash
source .venv/bin/activate
```

Ejecuta los ejemplos (los pesos se resuelven desde `vendor/libreyolo/`):

```bash
make detect
make segment
make dev          # backend :8000 + frontend :8080
```

También puedes importar desde cualquier script en la raíz del repo:

```bash
python -c "from libreyolo import LibreYOLO; print('LibreYOLO ready')"
```

## Notas

- LibreYOLO vive en `vendor/libreyolo/` para evitar conflictos de import con una carpeta `libreyolo/` en la raíz.
- `segment.py` necesita el extra `[rfdetr]`; `make setup` ya lo instala.
- En macOS, PyTorch usa CPU + MPS (Apple Silicon) automáticamente.

## Enlaces

- [Visión del Hackathon](<Cursor Madrid Hackathon #3 - Visión.webloc>)
- [Luma Event](<Cursor Madrid Hackathon #3 - Luma.webloc>)
- [LibreYOLO docs](https://www.libreyolo.com/docs)
