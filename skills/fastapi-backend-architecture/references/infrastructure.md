# Infrastructure Wiring

Use the project's existing dependency injection style. These examples use FastAPI dependency functions because they are broadly portable.

## Endpoint

```python
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from my_app.app.projects.exceptions import ProjectNotFoundError
from my_app.app.projects.schemas import ProjectCreate, ProjectRead
from my_app.app.projects.service import ProjectService
from my_app.dependencies import get_project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    return await service.create_project(project)


@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    try:
        return await service.get_project(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
```

## Dependency Wiring

```python
from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from my_app.app.projects.repository import ProjectRepository
from my_app.app.projects.service import ProjectService
from my_app.database.postgresql import async_session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_project_repository(
    session: AsyncSession = Depends(get_session),
) -> ProjectRepository:
    return ProjectRepository(session)


async def get_project_service(
    repository: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
    return ProjectService(repository)
```

## Database Session

```python
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from my_app.config.settings import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.postgresql_url, pool_pre_ping=True)
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False
)
```

## Configuration

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP__",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    postgresql_url: SecretStr
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
```

## CLI

```python
from pathlib import Path
from typing import Annotated

import typer

cli = typer.Typer(name="my-app")


@cli.command()
def run(
    host: Annotated[str, typer.Option("--host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port")] = 8000,
    reload: Annotated[bool, typer.Option("--reload")] = False,
) -> None:
    import uvicorn

    uvicorn.run("my_app.main:app", host=host, port=port, reload=reload)


@cli.command()
def generate_openapi(output_path: Path = Path("openapi.json")) -> None:
    import json

    from my_app.main import app

    output_path.write_text(json.dumps(app.openapi(), indent=2))
```

## App Entry Point

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from my_app.app.projects.endpoints import router as project_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Initialize shared resources here when the app owns their lifecycle.
    yield
    # Dispose shared resources here.


app = FastAPI(lifespan=lifespan)
app.include_router(project_router)


@app.get("/")
async def health() -> None:
    return None
```
