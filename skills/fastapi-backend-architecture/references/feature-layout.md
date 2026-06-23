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
- `app/{feature}/endpoints.py`: `APIRouter`, path/query/body declarations, response models, HTTP status codes, dependency declarations.
- `app/{feature}/service.py`: business workflow, policy checks, coordination across repositories and integrations.
- `app/{feature}/repository.py`: SQLAlchemy persistence logic, filtering, pagination, commits, refreshes, deletes.
- `app/{feature}/models.py`: SQLAlchemy ORM tables and relationships.
- `app/{feature}/schemas.py`: Pydantic create/read/update/request/response models.
- `app/{feature}/exceptions.py`: domain exceptions such as `ProjectNotFoundError`.
- `database/`: engine/session factories, metadata base, migration integration, database setup helpers.
- `config/`: settings objects, environment mapping, secrets.
- `cli.py`: operational commands such as run, setup, migrate, generate OpenAPI.

## Adding A Feature

1. Create the feature package with `schemas.py`, `models.py`, `repository.py`, `service.py`, `endpoints.py`, and `exceptions.py` as needed.
2. Add or update shared infrastructure only when the feature needs a new resource.
3. Register dependencies in the existing dependency layer.
4. Include the feature router from the app entry point.
5. Add tests for the layer where behavior lives.
