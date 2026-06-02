# src

Código del proyecto del hackathon. Misma idea que los equipos en [cursor-madrid-hack3](https://github.com/yoplait/cursor-madrid-hack3), pero con capas separadas:

| Carpeta | Responsabilidad |
|---------|-----------------|
| [`frontend/`](frontend/) | UI, visualización, cliente web o desktop |
| [`backend/`](backend/) | API, orquestación, lógica de negocio |
| [`infra/`](infra/) | Docker, despliegue, CI, scripts de entorno |
| [`model/`](model/) | Inferencia LibreYOLO, pipelines de visión |

## Quick start (modelo)

Desde la raíz del repo:

```bash
source .venv/bin/activate
make detect
make segment
```
