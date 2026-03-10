# GitHub Workflow

## Modelo de ramas
- `main`: rama estable de producción.
- `staging`: rama de integración y validación.
- `feature/*`: nuevas funcionalidades.
- `bugfix/*`: correcciones.
- `chore/*`: tareas técnicas e infraestructura.

## Flujo de trabajo
1. Crear rama de trabajo desde `staging`.
2. Desarrollar y abrir PR hacia `staging`.
3. Ejecutar CI y pruebas funcionales en `staging`.
4. Cuando `staging` esté estable, abrir PR de `staging` hacia `main`.
5. Hacer release desde `main` (tag recomendado).

## Reglas recomendadas en GitHub
- Protección de `main` y `staging`.
- Merge vía Pull Request únicamente.
- 1 aprobación mínima por PR.
- Checks obligatorios de CI.
- Squash merge para historial limpio.

## Convención de commits
Usar Conventional Commits:
- `feat:`
- `fix:`
- `chore:`
- `refactor:`
- `docs:`

## Labels recomendados
- `type:feature`
- `type:bug`
- `type:chore`
- `priority:p1`
- `priority:p2`
- `priority:p3`
- `priority:p4`
- `area:frontend`
- `area:backend`
- `area:worker`
- `area:infra`

## Board sugerido
- Backlog
- Ready
- In Progress
- In Review
- Done

