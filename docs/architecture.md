# Arquitectura Hexagonal

## Objetivo
Separar reglas de negocio de frameworks e infraestructura para facilitar cambios, pruebas y escalabilidad.

## Backend (FastAPI)
Estructura base en `backend/src/converto`:

- `domain/`: entidades y contratos del dominio.
- `application/`: casos de uso y puertos.
- `adapters/`: implementaciones concretas (web, repositorios SQL, cola Celery, etc).

Flujo de creación de job:
1. Adaptador web (`POST /v1/jobs`) recibe request.
2. Caso de uso `CreateConversionJobUseCase` valida y crea entidad.
3. Repositorio (adaptador SQLAlchemy) persiste en Postgres.
4. Puerto de despacho (adaptador Celery) encola procesamiento en worker.

## Worker (Celery)
Estructura base en `worker/src/converto_worker`:

- `application/`: caso de uso de procesamiento.
- `adapters/`: convertidor concreto.
- `config/`: settings.
- `tasks.py`: entrypoint de tareas Celery.

Estado actual:
- Se implementó un convertidor mock para validar el flujo asíncrono.
- El siguiente paso es integrar convertidores reales por tipo de archivo.

## Frontend (Vue + Vite)
- Cliente SPA ligero para carga de archivos, selección de formato y consulta de estado.
- Consumirá endpoints del backend (`/v1/jobs` y futuros endpoints de upload/download).

## Principios de implementación
- El dominio no depende de FastAPI, SQLAlchemy o Celery.
- Los casos de uso dependen de puertos, no de implementaciones.
- Los adaptadores conectan tecnologías concretas al núcleo.
- Cambios de infraestructura deben impactar mínimo al dominio.

