# Converto

Converto es una aplicacion web para convertir archivos con arquitectura hexagonal.

## Stack
- Frontend: Vue 3 + Vite + TypeScript
- Backend API: FastAPI + Python
- Worker: Celery + Python
- DB: PostgreSQL
- Cola: Redis
- Storage: MinIO (S3 compatible)
- Orquestacion local: Docker Compose

## Estructura
```text
.
├─ frontend/
├─ backend/
├─ worker/
├─ .github/
├─ docker-compose.yml
└─ docs/
```

## Arquitectura
- `frontend` consume la API.
- `backend` orquesta casos de uso y crea jobs.
- `worker` procesa conversiones asincronas.
- `postgres` guarda metadata de jobs.
- `redis` actua como broker/result backend de Celery.
- `minio` guarda archivos fuente y resultado.

Detalle: [Arquitectura Hexagonal](./docs/architecture.md)

## Flujo de ramas actual
Para este equipo (tu y yo), el flujo operativo es simple:
1. Crear rama `feature/*` desde la base actual.
2. Hacer commits y `git push` directo de la rama.
3. Integrar por merge directo cuando la feature este validada.

## Arranque local
1. Crear `.env` opcional si quieres customizar variables:
   ```bash
   cp .env.example .env
   ```
2. Levantar stack:
   ```bash
   docker compose --env-file .env.example up --build
   ```

## URLs
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Endpoints MVP
- `GET /v1/capabilities/formats`
- `POST /v1/jobs/upload` (multipart: `file`, `target_format`)
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/download`

## Estado actual
- Pipeline end-to-end de upload y procesamiento habilitado.
- Conversiones reales activas con motor multi-engine:
  - LibreOffice para documentos/ofimatica.
  - FFmpeg para audio/video.
  - Pillow para imagenes.
- Pares no soportados devuelven error claro en API.
