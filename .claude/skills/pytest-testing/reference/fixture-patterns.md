# pytest Fixture Patterns Reference

## Fixture Scope Levels

| Scope | Created | Destroyed | When to Use |
|-------|---------|-----------|-------------|
| `function` (default) | Each test | After each test | Most fixtures — ensures isolation |
| `class` | First test in class | After last test in class | Rarely needed |
| `module` | First test in file | After last test in file | Expensive but file-local setup |
| `session` | Once for entire run | After all tests | Database engine, shared HTTP client |

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Session-scoped — engine is created once for the entire test run
@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    yield engine
    await engine.dispose()

# Function-scoped — each test gets a fresh session with rollback
@pytest.fixture
async def db(engine) -> AsyncSession:
    async with engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn)
        yield session
        await conn.rollback()
```

## Factory Fixtures

Factory fixtures return a callable so tests can create multiple objects with controlled attributes.

```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    role: str = "viewer"

@pytest.fixture
def make_user():
    counter = 0
    def _make(email: str | None = None, role: str = "viewer") -> User:
        nonlocal counter
        counter += 1
        return User(
            id=counter,
            email=email or f"user{counter}@example.com",
            role=role,
        )
    return _make


def test_admin_can_delete_user(make_user):
    admin = make_user(role="admin")
    target = make_user()
    assert can_delete(actor=admin, target=target) is True

def test_viewer_cannot_delete_user(make_user):
    viewer = make_user(role="viewer")
    target = make_user()
    assert can_delete(actor=viewer, target=target) is False
```

## Async Fixtures

Requires `pytest-asyncio` with `asyncio_mode = "auto"` in `pyproject.toml`.

```python
import pytest
import httpx
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from my_service.main import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
async def async_client(app) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
```

## Fixture Composition

Fixtures can request other fixtures — this is how setup is layered without duplication.

```python
@pytest.fixture
async def authenticated_client(async_client: AsyncClient, make_user) -> AsyncClient:
    """Returns an HTTP client with a valid auth token pre-set."""
    user = make_user(role="admin")
    token = create_test_token(user.id)
    async_client.headers["Authorization"] = f"Bearer {token}"
    return async_client


async def test_delete_user_as_admin(authenticated_client: AsyncClient, make_user):
    target = make_user()
    response = await authenticated_client.delete(f"/users/{target.id}")
    assert response.status_code == 204
```

## Monkeypatching

```python
from my_service.clients import send_email  # module-level function

async def test_create_user_sends_welcome_email(monkeypatch, async_client):
    sent: list[str] = []

    def mock_send_email(to: str, subject: str, body: str) -> None:
        sent.append(to)

    monkeypatch.setattr("my_service.services.user_service.send_email", mock_send_email)

    response = await async_client.post("/users", json={"email": "new@example.com"})
    assert response.status_code == 201
    assert "new@example.com" in sent
```
