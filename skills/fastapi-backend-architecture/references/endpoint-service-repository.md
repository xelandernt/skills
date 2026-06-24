# Endpoint -> Service -> Repository Patterns

Use these patterns to decide where code belongs:

```text
Endpoint
  - HTTP routing, path/query/body parameters, status codes, response models
  - FastAPI dependencies such as auth, pagination, request context, and DI
  - Translation from domain exceptions to HTTP errors

Service
  - Business workflow and policy
  - Coordination across repositories, external APIs, queues, storage, or email
  - Permission checks that need domain data
  - ORM-to-schema conversion when that keeps endpoints thin

Repository
  - SQLAlchemy statements and persistence details
  - Session add/commit/refresh/delete
  - Filtering, pagination, locking, eager loading, and aggregate queries
  - Returns ORM objects or persistence-oriented values, not HTTP responses
```

## Dependency Providers

Prefer feature-local provider functions. Put the repository provider in `repository.py`, the service provider in `service.py`, and inject only the service from endpoints. Shared resources such as database sessions remain in infrastructure modules.

```python
# repository.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from my_app.database.postgresql import get_async_session


async def get_project_repository(
    session: AsyncSession = Depends(get_async_session),
) -> "ProjectRepository":
    return ProjectRepository(session)


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
```

```python
# service.py
from fastapi import Depends

from my_app.app.projects.repository import ProjectRepository, get_project_repository


async def get_project_service(
    project_repository: ProjectRepository = Depends(get_project_repository),
) -> "ProjectService":
    return ProjectService(project_repository)


class ProjectService:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self.project_repository = project_repository
```

For a synchronous SQLAlchemy project, use the same provider shape with `Session` and a sync repository/service body.

## Pattern: Simple Create

Endpoint accepts a create schema and delegates. Service enforces business rules. Repository persists.

```python
# endpoints.py
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    return await service.create_project(project)


# service.py
async def create_project(self, project: ProjectCreate) -> ProjectRead:
    if await self._repository.exists_by_name(project.name):
        raise ProjectAlreadyExistsException(project.name)
    project_db = await self._repository.create(project)
    return ProjectRead.model_validate(project_db)


# repository.py
async def create(self, project: ProjectCreate) -> ProjectDB:
    project_db = ProjectDB(**project.model_dump())
    self._session.add(project_db)
    await self._session.commit()
    await self._session.refresh(project_db)
    return project_db
```

## Pattern: Read By ID With 404

Keep the not-found rule in the service. The endpoint translates it to `HTTPException` at the HTTP boundary.

```python
# endpoints.py
@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    try:
        return await service.get_project(project_id)
    except ProjectNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


# service.py
async def get_project(self, project_id: UUID) -> ProjectRead:
    project_db = await self._repository.get_by_id(project_id)
    if project_db is None:
        raise ProjectNotFoundException(f"Project {project_id} not found")
    return ProjectRead.model_validate(project_db)


# repository.py
async def get_by_id(self, project_id: UUID) -> ProjectDB | None:
    result = await self._session.execute(
        select(ProjectDB).where(ProjectDB.id == project_id)
    )
    return result.scalar_one_or_none()
```

## Pattern: User-Scoped Query

Endpoint obtains the authenticated user. Service passes the user or tenant context into repository methods so ownership filtering stays close to persistence.

```python
# endpoints.py
@router.get("/")
async def list_projects(
    user: CurrentUser = Depends(get_current_user),
    pagination: Pagination = Depends(),
    service: ProjectService = Depends(get_project_service),
) -> Page[ProjectRead]:
    return await service.list_projects(user_id=user.id, pagination=pagination)


# service.py
async def list_projects(self, user_id: UUID, pagination: Pagination) -> Page[ProjectRead]:
    projects, total = await self._repository.list_for_user(
        user_id=user_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return Page(
        items=[ProjectRead.model_validate(project) for project in projects],
        total=total,
        limit=pagination.limit,
        offset=pagination.offset,
    )


# repository.py
async def list_for_user(
    self, user_id: UUID, limit: int, offset: int
) -> tuple[list[ProjectDB], int]:
    statement = select(ProjectDB).where(ProjectDB.owner_id == user_id)
    total = await self._count(statement)
    result = await self._session.execute(statement.offset(offset).limit(limit))
    return list(result.scalars().all()), total
```

## Pattern: Multi-Step Workflow

When a request touches multiple systems, the endpoint still calls one service method. The service coordinates repositories and integrations.

```python
# endpoints.py
@router.post("/{project_id}/archive", status_code=status.HTTP_202_ACCEPTED)
async def archive_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    return await service.archive_project(project_id)


# service.py
async def archive_project(self, project_id: UUID) -> ProjectRead:
    project = await self._repository.get_by_id(project_id)
    if project is None:
        raise ProjectNotFoundException(f"Project {project_id} not found")
    if project.status == ProjectStatus.ARCHIVED:
        return ProjectRead.model_validate(project)

    project.status = ProjectStatus.ARCHIVED
    await self._repository.save(project)
    await self._audit_log.record("project_archived", project_id=project.id)
    await self._queue.publish(ProjectArchived(project_id=project.id))
    return ProjectRead.model_validate(project)
```

## Pattern: Transaction Boundary

Use one transaction for a unit of work. Prefer keeping commit control in one layer for a given app. If repositories commit per method, services cannot easily make multi-repository operations atomic. For complex workflows, prefer repository methods that mutate the session and a service or unit-of-work layer that commits once.

```python
# service.py
async def transfer_project(self, project_id: UUID, new_owner_id: UUID) -> ProjectRead:
    async with self._unit_of_work:
        project = await self._project_repository.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundException(f"Project {project_id} not found")
        await self._user_repository.require_exists(new_owner_id)
        project.owner_id = new_owner_id
        await self._project_repository.save(project, commit=False)
        await self._unit_of_work.commit()
    return ProjectRead.model_validate(project)
```

## Anti-Pattern: Everything In The Endpoint

Avoid mixing all layers in an endpoint:

```python
@router.post("/")
async def create_project(
    project: ProjectCreate,
    session: AsyncSession = Depends(get_session),
):
    project_db = ProjectDB(**project.model_dump())
    session.add(project_db)
    await session.commit()
    await session.refresh(project_db)
    await queue.publish({"project_id": str(project_db.id)})
    return project_db
```

This couples HTTP, persistence, queueing, transaction behavior, and response shape in one function. Split it into endpoint, service, repository, and integration dependencies.
