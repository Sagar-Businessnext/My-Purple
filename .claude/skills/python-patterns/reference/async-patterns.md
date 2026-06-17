# Async/Await Patterns Reference

## Core Rules

1. Async functions must only `await` other awaitables — do not call blocking sync I/O inside `async def`
2. Use `asyncio.to_thread()` to run blocking code off the event loop
3. Use `asyncio.gather()` for concurrent independent tasks; use sequential `await` for dependent tasks
4. FastAPI route handlers are always `async def` when using async database drivers or async HTTP clients

## FastAPI Route with Async Database Access

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from my_service.dependencies import get_db_session
from my_service.repositories.user_repository import UserRepository
from my_service.schemas.user import CreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    repo = UserRepository(db)
    existing = await repo.find_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = await repo.create(body)
    return UserResponse.model_validate(user)
```

## Concurrent Independent Tasks

```python
import asyncio
from my_service.clients import analytics_client, notification_client

async def process_order(order_id: int) -> None:
    # Both calls are independent — run them concurrently
    analytics_result, notification_result = await asyncio.gather(
        analytics_client.track_order(order_id),
        notification_client.send_confirmation(order_id),
        return_exceptions=True,  # don't cancel the other if one fails
    )
    # Handle partial failures
    if isinstance(analytics_result, Exception):
        logger.warning("Analytics tracking failed", exc_info=analytics_result)
```

## Running Blocking Code Off the Event Loop

```python
import asyncio
from pathlib import Path

async def read_large_file(path: Path) -> str:
    # Path.read_text() is blocking — run it in a thread pool
    content = await asyncio.to_thread(path.read_text, encoding="utf-8")
    return content


async def run_cpu_intensive(data: list[int]) -> int:
    # CPU-bound work also blocks the event loop — offload to thread
    result = await asyncio.to_thread(sum, data)
    return result
```

## Async Context Manager for Database Sessions

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://...")
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# FastAPI Depends version
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session
```

## Anti-Patterns

```python
# WRONG — blocking call inside async function
async def get_user(user_id: int) -> User:
    result = requests.get(f"https://api.example.com/users/{user_id}")  # blocks event loop
    return result.json()

# CORRECT — use httpx async client
async def get_user(user_id: int) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
    return User(**response.json())


# WRONG — creating a new event loop in a service function
def sync_wrapper(data: dict) -> str:
    return asyncio.run(async_process(data))  # never in library code

# CORRECT — accept that the caller is async; don't wrap
async def process(data: dict) -> str:
    return await async_process(data)


# WRONG — sequential await when tasks are independent
async def load_dashboard(user_id: int) -> Dashboard:
    orders = await order_service.get_recent(user_id)    # waits 100ms
    alerts = await alert_service.get_active(user_id)   # then waits 80ms

# CORRECT — concurrent
async def load_dashboard(user_id: int) -> Dashboard:
    orders, alerts = await asyncio.gather(
        order_service.get_recent(user_id),
        alert_service.get_active(user_id),
    )
```
