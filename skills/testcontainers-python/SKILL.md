---
name: testcontainers-python
description: Use this skill when adding, reviewing, or debugging pytest integration tests that use Testcontainers Python, Docker-backed services, module-specific containers, custom DockerContainer subclasses, readiness checks, mapped ports, or container fixture lifecycles.
---

# Testcontainers Python

## Workflow

1. Read the current fixture setup before changing tests:
   - `tests/conftest.py`
   - `tests/integration/conftest.py`
   - `pyproject.toml` pytest and dependency sections
2. For Testcontainers usage details, read [references/testcontainers-pytest-guide.md](references/testcontainers-pytest-guide.md). Use it when you need to add a container fixture, create a custom `DockerContainer`, expose ports, add readiness checks, or debug container startup.
3. Preserve the repository's broad pytest shape unless the task explicitly asks for a redesign:
   - `pytest-asyncio` runs with `asyncio_mode = "auto"`.
   - Expensive Docker containers should normally be session-scoped.
   - Per-test cleanup or data reset should normally be function-scoped.
4. When adding a Docker-backed service, prefer a session-scoped container fixture plus a function-scoped fixture for test isolation. Do not restart slow containers per test unless isolation cannot be achieved otherwise.
5. Use explicit readiness checks. For new custom containers, prefer Testcontainers structured wait strategies such as `LogMessageWaitStrategy`, `HttpWaitStrategy`, `PortWaitStrategy`, `ExecWaitStrategy`, or `CompositeWaitStrategy` when available. Existing code may still use legacy helpers like `wait_container_is_ready` and `wait_for_logs`; preserve them only when making minimal edits.
6. Validate with the narrowest relevant pytest command first, then broaden if the change affects shared fixtures:
   - `uv run pytest tests/integration -q`
   - `uv run pytest -q`

## Gotchas

- Docker must be available to run integration tests that start Testcontainers.
- Always use Testcontainers-provided mapped host and port helpers. Do not hard-code host ports.
- Container readiness should be based on a real ready signal: port, log line, HTTP check, command result, or a composite wait strategy.
- Keep container lifetime and test isolation separate: starting a container and resetting test state are different responsibilities.
