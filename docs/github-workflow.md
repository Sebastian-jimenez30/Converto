# GitHub Workflow

## Modelo de ramas
- `main`: rama estable de produccion.
- `staging`: rama de validacion previa cuando la necesitemos.
- `feature/*`: nuevas funcionalidades.
- `bugfix/*`: correcciones.
- `chore/*`: tareas tecnicas e infraestructura.

## Flujo operativo actual
Como solo estamos desarrollando tu y yo:
1. Crear rama (`feature/*`, `bugfix/*`, `chore/*`).
2. Desarrollar y validar localmente.
3. Hacer `git push` directo de la rama.
4. Integrar por merge directo cuando este aprobada.

Nota:
- Podemos volver a flujo formal con PR a `staging` en cualquier momento.

## Convencion de commits
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

