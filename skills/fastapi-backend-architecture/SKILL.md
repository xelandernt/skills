---
name: fastapi-backend-architecture
description: Guide FastAPI backend architecture design and implementation. Use when adding or reviewing app modules, endpoints, async endpoint-service-repository logic, SQLAlchemy models, Pydantic schemas, configuration, Typer CLI commands, dependency injection, or database setup.
---

# FastAPI Backend Architecture

## When To Use

Use this skill when adding, changing, or reviewing FastAPI backend code that touches:

- Feature modules, file structure, routers, or app startup.
- Endpoint -> service -> repository design.
- Async SQLAlchemy repositories, transactions, migrations, or database setup.
- Pydantic schemas, SQLAlchemy models, and API response contracts.
- Configuration, dependency injection, CLI commands, or infrastructure clients.

## Orientation

Before changing architecture-sensitive code, inspect the application's existing conventions:

- The FastAPI app factory or main app module for lifespan, middleware, router registration, and OpenAPI customization.
- The shared infrastructure providers for sessions, settings, clients, and request-scoped state, plus feature-local repository and service providers.
- The configuration module for Pydantic settings, environment naming, secrets, and deployment-specific overrides.
- The database module for async engine/session setup, migrations, metadata, and test database wiring.
- The most complete existing feature module for the preferred endpoint -> service -> repository -> model/schema pattern.
- The CLI entry point, if one exists, for operational commands such as running the app, setup, migrations, or schema generation.

## Reference Map

Open only the references needed for the task:

- `references/feature-layout.md` for package structure and feature-module organization.
- `references/endpoint-service-repository.md` for common endpoint -> service -> repository patterns.
- `references/dependencies-and-exceptions.md` for dependency-provider and domain-exception patterns.
- `references/models-and-schemas.md` for SQLAlchemy model and Pydantic schema examples.
- `references/infrastructure.md` for dependency wiring, database sessions, settings, CLI, and app entry points.

## Architecture Rules

1. Use a feature-oriented source layout. Keep API features under an application package, shared infrastructure under dedicated packages, and process-specific entry points in clearly named modules.
2. Keep endpoints thin. They should parse HTTP inputs, declare dependencies, call services, and return response schemas.
3. Put business rules and multi-step workflows in services. Services coordinate repositories, integrations, queues, storage, permission checks, and schema conversion.
4. Keep repositories persistence-focused. They own SQLAlchemy statements, session interaction, filtering, pagination, and persistence return values. They should not know about HTTP.
5. Use async consistently through endpoints, services, repositories, database sessions, clients, and workers unless the dependency has only a synchronous API and the project already accepts that tradeoff.
6. Keep SQLAlchemy ORM models separate from Pydantic schemas. ORM models represent persistence; schemas represent API/domain input and output contracts.
7. Define dependency providers at the layer that owns the object. Put `get_<feature>_repository` beside the repository, `get_<feature>_service` beside the service, and shared resource providers such as database sessions in infrastructure modules.
8. Centralize startup and teardown in the FastAPI lifespan or app factory. Do not initialize long-lived resources in endpoint modules.
9. Inject services into endpoints with `Depends(get_<feature>_service)`. Do not construct repositories or services inside route handlers.
10. Keep domain exceptions as plain feature exceptions. Services raise them for business failures; endpoints translate them to `HTTPException`.
11. Add configuration through the central settings system, preferably Pydantic Settings. Use nested settings, environment overrides, and secret types for credentials.
12. Keep validation tied to the affected layer: schemas/helpers get focused unit tests; routing, DI, database, and transaction behavior need integration tests.

## Implementation Workflow

1. Identify the closest existing feature module and mirror its file structure before adding new abstractions.
2. Decide which layers are affected: schema, model, repository, service, endpoint, dependency wiring, config, CLI, or startup.
3. Define or update Pydantic schemas first, then ORM models, then repository methods, then service methods, then endpoint handlers.
4. Add provider functions next to new repositories and services before injecting them from endpoints or higher-level services.
5. Add routers to the app entry point or app factory after defining the route module.
6. Add configuration fields to the central settings model and consume them through the settings dependency or config object.
7. Add or update tests at the narrowest layer that proves the behavior.

## Validation

Run the narrowest useful checks available in the project, usually including:

```bash
<lint command>
<test command>
```

For API or schema changes, also regenerate or inspect OpenAPI output if the project publishes it:

```bash
<openapi generation command>
```

For database/infrastructure changes, verify migrations or setup still work in the relevant environment:

```bash
<migration or setup command>
```

If Docker-backed integration tests are relevant, make sure Docker is available before treating failures as application regressions.
