# Models And Schemas

Keep SQLAlchemy ORM models and Pydantic schemas separate.

- ORM models represent persistence, relationships, indexes, constraints, and query helpers.
- Pydantic schemas represent API input/output contracts and validation.
- Convert ORM objects to response schemas with `model_validate` when using `ConfigDict(from_attributes=True)`.

## Pydantic Schemas

```python
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
```

## SQLAlchemy Model

```python
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from my_app.database.postgresql import Base


class ProjectDB(Base):
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
```

## Repository

```python
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from my_app.app.projects.models import ProjectDB
from my_app.app.projects.schemas import ProjectCreate


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, project: ProjectCreate) -> ProjectDB:
        project_db = ProjectDB(**project.model_dump())
        self._session.add(project_db)
        await self._session.commit()
        await self._session.refresh(project_db)
        return project_db

    async def get_by_id(self, project_id: UUID) -> ProjectDB | None:
        result = await self._session.execute(
            select(ProjectDB).where(ProjectDB.id == project_id)
        )
        return result.scalar_one_or_none()
```

## Service Conversion

```python
from uuid import UUID

from my_app.app.projects.exceptions import ProjectNotFoundException
from my_app.app.projects.repository import ProjectRepository
from my_app.app.projects.schemas import ProjectCreate, ProjectRead


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def create_project(self, project: ProjectCreate) -> ProjectRead:
        project_db = await self._repository.create(project)
        return ProjectRead.model_validate(project_db)

    async def get_project(self, project_id: UUID) -> ProjectRead:
        project_db = await self._repository.get_by_id(project_id)
        if project_db is None:
            raise ProjectNotFoundException(f"Project {project_id} not found")
        return ProjectRead.model_validate(project_db)
```
