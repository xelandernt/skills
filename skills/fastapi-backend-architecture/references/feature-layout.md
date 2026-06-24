# Feature Layout

Use a feature-oriented layout so related endpoint, service, repository, model, schema, and exception code stays close together.

```text
src/my_app/
  main.py
  config/
    settings.py
  database/
    postgresql.py
  app/
    schemas.py
    projects/
      endpoints.py
      service.py
      repository.py
      models.py
      schemas.py
      exceptions.py
  cli.py
```

## Module Responsibilities

- `main.py`: FastAPI app creation, lifespan, middleware, router registration, OpenAPI customization, health checks.
- `app/{feature}/endpoints.py`: `APIRouter`, path/query/body declarations, response models, HTTP status codes, auth/request dependencies, and domain-exception-to-HTTP translation.
- `app/{feature}/service.py`: business workflow, policy checks, coordination across repositories and integrations, plus `get_<feature>_service`.
- `app/{feature}/repository.py`: SQLAlchemy persistence logic, filtering, pagination, commits, refreshes, deletes, plus `get_<feature>_repository`.
- `app/{feature}/models.py`: SQLAlchemy ORM tables and relationships.
- `app/{feature}/schemas.py`: Pydantic create/read/update/request/response models.
- `app/{feature}/exceptions.py`: domain exceptions such as `ProjectNotFoundException`.
- `database/`: engine/session factories, metadata base, migration integration, database setup helpers.
- `config/`: settings objects, environment mapping, secrets.
- `cli.py`: operational commands such as run, setup, migrate, generate OpenAPI.

## Adding A Feature

1. Create the feature package with `schemas.py`, `models.py`, `repository.py`, `service.py`, `endpoints.py`, and `exceptions.py` as needed.
2. Add `get_<feature>_repository` in `repository.py`, depending on the shared session provider.
3. Add `get_<feature>_service` in `service.py`, depending on the feature repository provider and any integration-client providers the service owns.
4. Include the feature router from the app entry point.
5. Add tests for the layer where behavior lives.

## Example Slice

```text
app/projects/
  exceptions.py      # ProjectException, ProjectNotFoundException, ProjectAlreadyExistsException
  repository.py      # get_project_repository(session=Depends(get_async_session))
  service.py         # get_project_service(repository=Depends(get_project_repository))
  endpoints.py       # service=Depends(get_project_service), raises HTTPException at route boundary
```
