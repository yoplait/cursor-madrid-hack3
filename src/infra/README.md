# infra

## Local (recomendado)

```bash
make dev
```

## Docker (backend sin LibreYOLO embebido)

Requiere pesos montados en `vendor/libreyolo/weights/`:

```bash
docker compose -f src/infra/docker-compose.yml up --build
```

Frontend: http://localhost:8080 · API: http://localhost:8000

**Nota:** la imagen Docker no incluye `pip install libreyolo`; para producción conviene extender el Dockerfile o montar un venv preparado.
