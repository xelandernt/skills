# Testcontainers Python and Pytest Guide

Use this guide after activating the `testcontainers-python` skill. Keep it focused on Testcontainers patterns: container lifetime, mapped ports, readiness checks, fixture scope, and debugging Docker-backed tests.

## Source Anchors

- Upstream docs: https://testcontainers-python.readthedocs.io/en/latest/
- Upstream repository: https://github.com/testcontainers/testcontainers-python
- Core docs: https://testcontainers-python.readthedocs.io/en/latest/core/README.html

## What Testcontainers Provides

Testcontainers Python starts real Docker containers from tests and gives Python code safe access to the running service through generated connection details. Use it when a test needs behavior from a real external service instead of an in-process fake.

The core pattern is:

1. Create a container object.
2. Configure image, exposed ports, environment variables, commands, volumes, or network settings.
3. Start the container with a context manager or explicit `start()`.
4. Wait until the service is ready.
5. Read mapped host/port or module-specific connection details from the container.
6. Run the test.
7. Stop the container automatically at fixture or context-manager teardown.

## Pytest Fixture Shape

Prefer separating container lifetime from test isolation:

```python
import typing

import pytest
from testcontainers.core.container import DockerContainer


@pytest.fixture(scope="session")
def service_container() -> typing.Iterator[DockerContainer]:
    with (
        DockerContainer("vendor/service:tag")
        .with_exposed_ports(8080)
    ) as container:
        yield container


@pytest.fixture(scope="function")
def service_endpoint(service_container: DockerContainer) -> str:
    host = service_container.get_container_host_ip()
    port = service_container.get_exposed_port(8080)
    return f"http://{host}:{port}"
```

Use `session` scope for containers that are expensive to start. Use `function` scope for state reset, data cleanup, test-specific configuration, and endpoint handoff. Only make the container fixture function-scoped when the service cannot be reset reliably between tests.

For async pytest projects, keep async work in async fixtures, but the Testcontainers container object itself can still be managed with its normal synchronous context manager:

```python
@pytest.fixture(scope="session")
async def service_container() -> typing.AsyncIterator[DockerContainer]:
    with DockerContainer("vendor/service:tag").with_exposed_ports(8080) as container:
        yield container
```

## Module-Specific Containers

Testcontainers Python includes many module-specific containers. Prefer a module-specific container when it exposes useful helpers such as connection URLs, credentials, or service-specific defaults. Prefer `DockerContainer` when there is no module for the service or when the test needs custom startup behavior.

Generic example:

```python
@pytest.fixture(scope="session")
def module_container() -> typing.Iterator[object]:
    with ModuleSpecificContainer("vendor/service:tag") as container:
        yield container
```

When using a module-specific container, get connection details from the container API instead of rebuilding URLs manually. The important principle is to trust Testcontainers for mapped host, mapped port, credentials, and generated connection strings.

## Custom DockerContainer Classes

Create a custom container class when a service needs repeated setup details or a clearer endpoint helper:

```python
from typing import Self

from testcontainers.core.container import DockerContainer


class ServiceContainer(DockerContainer):
    def __init__(self, image: str = "vendor/service:tag", port: int = 8080, **kwargs):
        super().__init__(image, **kwargs)
        self.port = port
        self.with_exposed_ports(self.port)

    def get_endpoint_url(self) -> str:
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"http://{host}:{port}"

    def start(self) -> Self:
        super().start()
        # Add readiness checks here before returning.
        return self
```

Keep custom classes small. They should encapsulate reusable Testcontainers setup, not unrelated application configuration.

## Readiness Checks

Do not rely on arbitrary sleeps. A container being started is not the same as the service being ready.

Prefer structured wait strategies for new code when supported by the installed Testcontainers version:

```python
from testcontainers.core.container import DockerContainer
from testcontainers.core.wait_strategies import (
    CompositeWaitStrategy,
    HttpWaitStrategy,
    LogMessageWaitStrategy,
    PortWaitStrategy,
)

container = (
    DockerContainer("vendor/service:tag")
    .with_exposed_ports(8080)
    .waiting_for(
        CompositeWaitStrategy(
            PortWaitStrategy(8080),
            LogMessageWaitStrategy("ready"),
            HttpWaitStrategy(8080, "/health").for_status_code(200),
        )
    )
)
```

Good readiness signals include:

- A mapped port accepting connections.
- A stable startup log line.
- A successful HTTP health response.
- A successful command executed inside the container.
- A composite wait strategy when one signal alone is not enough.

Existing code may use legacy helpers such as `wait_container_is_ready` and `wait_for_logs`. Preserve those when making minimal edits, but prefer structured wait strategies for new containers.

## Ports and Endpoints

Never assume a container port is published on the same host port. Testcontainers maps ports dynamically to avoid collisions.

Use:

```python
host = container.get_container_host_ip()
port = container.get_exposed_port(container_port)
endpoint = f"http://{host}:{port}"
```

Avoid:

```python
endpoint = "http://localhost:8080"
```

Hard-coded host ports make tests flaky on developer machines and CI runners.

## Configuration Surface

Use Testcontainers methods for container setup:

```python
container = (
    DockerContainer("vendor/service:tag")
    .with_exposed_ports(8080)
    .with_env("SERVICE_MODE", "test")
    .with_command("serve --test")
)
```

Keep these concerns in the container fixture or custom container class:

- Docker image and tag.
- Exposed container ports.
- Environment variables passed into the container.
- Startup command.
- Volumes and bind mounts.
- Wait strategy.
- Endpoint helper methods.

Keep app-specific configuration outside this guide. The Testcontainers skill should describe how to run and access containers, not how an individual application wires those endpoints into its own settings.

## Debugging Failures

Check these in order:

1. Is Docker running and reachable from the test process?
2. Did the image pull successfully?
3. Did the container start and stay running?
4. Is the service actually ready, or only the container process?
5. Does the wait strategy match the service's real ready signal?
6. Is the test using `get_container_host_ip()` and `get_exposed_port(...)` instead of hard-coded ports?
7. Are logs showing startup errors inside the container?

Useful commands:

```bash
uv run pytest tests/integration -q -s
docker ps
docker logs <container-id>
```

If startup fails around readiness checks, inspect actual container logs before changing predicates. Do not weaken readiness to a sleep; make the wait condition match the service's real ready signal.

## Validation Checklist

Before finishing a change that touches Testcontainers integration:

- Docker-backed tests pass with Docker running.
- Container fixtures use context managers or otherwise stop containers reliably.
- Expensive containers are not restarted per test unless required.
- Test isolation is handled separately from container startup.
- Endpoint construction uses Testcontainers mapped host/port helpers.
- Readiness checks use real service signals.
- No new hard-coded host ports were introduced.
