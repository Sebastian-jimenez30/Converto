# Arquitectura Hexagonal

## Objetivo
Separar reglas de negocio de frameworks e infraestructura para facilitar cambios, pruebas y escalabilidad.

## Backend (FastAPI)
Estructura base en `backend/src/converto`:

- `domain/`: entidades y contratos del dominio.
- `application/`: casos de uso y puertos.
- `adapters/`: implementaciones concretas (web, repositorios SQL, cola Celery, storage S3).

Flujo de conversion actual:
1. Adaptador web (`POST /v1/jobs/upload`) recibe `multipart/form-data`.
2. Caso de uso `CreateUploadConversionJobUseCase` valida archivo y formato destino.
3. Adaptador de storage sube la fuente a MinIO.
4. Repositorio SQLAlchemy persiste el job en Postgres con estado `queued`.
5. Puerto de despacho Celery encola procesamiento en worker.

## Worker (Celery)
Estructura base en `worker/src/converto_worker`:

- `application/`: caso de uso de procesamiento.
- `adapters/`: convertidor, acceso DB y storage.
- `config/`: settings.
- `tasks.py`: entrypoint de tareas Celery.

Flujo actual:
1. Lee job por `job_id` desde Postgres.
2. Actualiza estado a `processing`.
3. Descarga archivo fuente de MinIO.
4. Ejecuta convertidor multi-motor:
   - LibreOffice para formatos de ofimatica.
   - FFmpeg para audio/video.
   - Pillow para imagenes.
5. Sube resultado a `outputs/...` en MinIO.
6. Actualiza estado a `done` o `failed`.

## Frontend (Vue + Vite)
- Cliente SPA para subir archivos, elegir formato y consultar estado.
- Consume:
  - `GET /v1/capabilities/formats`
  - `POST /v1/jobs/upload`
  - `GET /v1/jobs/{job_id}`
  - `GET /v1/jobs/{job_id}/download`

## Principios
- El dominio no depende de FastAPI, SQLAlchemy o Celery.
- Los casos de uso dependen de puertos, no de implementaciones.
- Los adaptadores conectan tecnologias concretas al nucleo.
- Cambios de infraestructura deben impactar minimo al dominio.
