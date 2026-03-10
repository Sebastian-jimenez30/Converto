# Converto

Converto es una aplicación web para convertir archivos con una arquitectura hexagonal.

## Stack
- Frontend: Vue 3 + Vite + TypeScript
- Backend API: FastAPI + Python
- Worker: Celery + Python
- DB: PostgreSQL
- Cola: Redis
- Storage: MinIO (S3 compatible)
- Orquestación local: Docker Compose

## Estructura del repositorio
```text
.
├─ frontend/
├─ backend/
├─ worker/
├─ .github/
├─ docker-compose.yml
└─ docs/
```

## Arquitectura (alto nivel)
- `frontend` es el cliente web.
- `backend` expone API HTTP y orquesta casos de uso.
- `worker` procesa trabajos asíncronos.
- `postgres` guarda metadata de jobs.
- `redis` sirve como broker/backend para Celery.
- `minio` almacena archivos de entrada y salida.

Más detalle: [Arquitectura Hexagonal](./docs/architecture.md)

## Estrategia de ramas
- `main`: producción.
- `staging`: integración y pruebas previas.
- Ramas cortas: `feature/*`, `bugfix/*`, `chore/*`.
- Flujo:
  1. Crear rama desde `staging`.
  2. PR hacia `staging`.
  3. Validar en `staging`.
  4. PR `staging -> main` para release.

Más detalle: [GitHub Workflow](./docs/github-workflow.md)

## Arranque local
1. Copiar variables:
   ```bash
   cp .env.example .env
   ```
2. Levantar stack:
   ```bash
   docker compose up --build
   ```
3. URLs:
- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- MinIO console: http://localhost:9001

## Estado actual
- Base inicial del monorepo y servicios creada.
- Backend y worker ya separados por capas hexagonales.
- Templates de GitHub y CI incluidos.
- Falta implementar conversión real de formatos (por ahora worker mock).

