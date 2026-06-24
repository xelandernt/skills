# Dependencies And Exceptions

Use dependencies to assemble request-scoped objects. Use exceptions to report domain failures without coupling services and repositories to HTTP.

## Provider Placement

Put each provider beside the object it constructs.

```python
# database/postgresql.py
from collections.abc import AsyncIterator
from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from my_app.config import CONFIG

Base: Final = declarative_base()
_ENGINE = create_async_engine(CONFIG.postgresql.connection_url)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(_ENGINE, expire_on_commit=False, autoflush=True) as session:
        yield session
```

```python
# app/projects/repository.py
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
# app/projects/service.py
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

Endpoint code depends on the service provider, not on the repository or session.

```python
# app/projects/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status

from my_app.app.projects.exceptions import ProjectNotFoundException
from my_app.app.projects.schema import ProjectResponse
from my_app.app.projects.service import ProjectService, get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        return await project_service.get_project(project_id)
    except ProjectNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
```

For a synchronous SQLAlchemy project, use the same provider shape with `Session` and a sync repository/service body.

```python
# database/d1.py
from collections.abc import Iterator
from typing import Final

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from my_app.config import CONFIG

Base: Final = declarative_base()
_ENGINE = create_engine(CONFIG.database.connection_url)


def get_session(request: Request) -> Iterator[Session]:
    engine = getattr(request.app.state, "engine", _ENGINE)
    with Session(engine, expire_on_commit=False, autoflush=True) as session:
        yield session
```

```python
# app/projects/repository.py
from fastapi import Depends
from sqlalchemy.orm import Session

from my_app.database.d1 import get_session


async def get_project_repository(
    session: Session = Depends(get_session),
) -> "ProjectRepository":
    return ProjectRepository(session)
```

## Multi-Dependency Service

When a service needs another repository or an external client, add it to the service provider. Keep construction out of route functions.

```python
# app/membership/service.py
from fastapi import Depends

from my_app.app.membership.repository import (
    MembershipRepository,
    get_membership_repository,
)
from my_app.clients.email import EmailClient
from my_app.config import CONFIG


async def get_email_client() -> EmailClient:
    return EmailClient(
        client_id=CONFIG.email.client_id,
        client_secret=CONFIG.email.client_secret,
    )


async def get_membership_service(
    membership_repository: MembershipRepository = Depends(get_membership_repository),
    email_client: EmailClient = Depends(get_email_client),
) -> "MembershipService":
    return MembershipService(membership_repository, email_client)
```

```python
# app/membership/endpoints.py
@router.post("/apply")
async def apply_for_membership(
    application_data: MembershipApplicationCreate,
    membership_service: MembershipService = Depends(get_membership_service),
) -> MembershipApplicationResponse:
    try:
        application = await membership_service.create_application(application_data)
    except MembershipApplicationAlreadyExistsException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    return MembershipApplicationResponse.model_validate(application)
```

## Auth Dependencies

Authentication and authorization dependencies belong at the HTTP boundary because they interpret request state.

```python
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


async def get_token_from_cookie_or_header(
    request: Request,
    token: HTTPAuthorizationCredentials | None = Depends(security),
) -> str | None:
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token
    if token:
        return token.credentials
    return None


async def get_current_user(
    token: str | None = Depends(get_token_from_cookie_or_header),
    user_service: UserService = Depends(get_user_service),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    user = await user_service.get_user_from_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return user


async def admin_required(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action",
        )
    return current_user
```

Use auth dependencies either as parameters when the endpoint needs the user, or as route dependencies when only access control is needed.

```python
@router.post("/", dependencies=[Depends(admin_required)])
async def create_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    return await project_service.create_project(project)
```

## Domain Exceptions

Feature exceptions are plain Python exceptions. They live in `exceptions.py`, are raised by services for business failures, and are translated to HTTP by endpoints.

```python
# app/projects/exceptions.py
class ProjectException(Exception):
    """Base exception for project-related errors."""


class ProjectNotFoundException(ProjectException):
    """Raised when a project is not found."""


class ProjectAlreadyExistsException(ProjectException):
    """Raised when a project already exists."""
```

```python
# app/projects/service.py
async def get_project(self, project_id: str) -> ProjectResponse:
    project = await self.project_repository.get_by_id(project_id)
    if not project:
        raise ProjectNotFoundException(f"Project with id '{project_id}' not found")
    return ProjectResponse.model_validate(project)
```

```python
# app/projects/endpoints.py
@router.get("/{project_id}")
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    try:
        return await project_service.get_project(project_id)
    except ProjectNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
```

## Anti-Patterns

Do not construct the dependency chain inside endpoints.

```python
@router.get("/{project_id}")
async def get_project(project_id: str, session: AsyncSession = Depends(get_async_session)):
    repository = ProjectRepository(session)
    service = ProjectService(repository)
    return await service.get_project(project_id)
```

Do not raise `HTTPException` from repositories or services.

```python
class ProjectService:
    async def get_project(self, project_id: str) -> ProjectResponse:
        project = await self.project_repository.get_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return ProjectResponse.model_validate(project)
```

Do not put domain rules in repository providers. Providers should construct objects; services enforce rules.

```python
async def get_project_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ProjectRepository:
    if not await project_feature_enabled():
        raise HTTPException(status_code=403)
    return ProjectRepository(session)
```
