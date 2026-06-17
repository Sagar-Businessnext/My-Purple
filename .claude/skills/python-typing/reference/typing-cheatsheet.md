# Python Typing Cheatsheet

## Built-in Generics (Python 3.9+)

```python
# Use built-in types directly — no imports needed
x: list[int] = [1, 2, 3]
y: dict[str, float] = {"rate": 0.5}
z: tuple[int, str, bool] = (1, "a", True)
s: set[str] = {"a", "b"}
f: frozenset[int] = frozenset({1, 2})

# Variable-length tuple
coords: tuple[float, ...] = (1.0, 2.0, 3.0)
```

## Union and Optional

```python
# Python 3.10+ union syntax (preferred)
def find_user(user_id: int) -> User | None: ...

# Multiple types
def parse(value: str | int | float) -> str: ...

# Old syntax (avoid in new code)
from typing import Optional, Union
def find_user(user_id: int) -> Optional[User]: ...  # equivalent but verbose
```

## Callable Types

```python
from collections.abc import Callable, Awaitable

# Sync callable: (arg1_type, arg2_type) -> return_type
handler: Callable[[str, int], bool]

# Async callable
async_handler: Callable[[str], Awaitable[bool]]

# No-arg callable
factory: Callable[[], User]
```

## TypeVar for Generic Functions

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None

# With bound — T must be a subtype of Comparable
from typing import Protocol
class Comparable(Protocol):
    def __lt__(self, other: "Comparable") -> bool: ...

C = TypeVar("C", bound=Comparable)
def maximum(items: list[C]) -> C: ...
```

## Protocol for Structural Interfaces

```python
from typing import Protocol, runtime_checkable

class Repository(Protocol):
    async def get(self, id: int) -> dict | None: ...
    async def save(self, data: dict) -> int: ...

# runtime_checkable allows isinstance() checks
@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

# Any class with a close() method satisfies Closeable
# — no inheritance required
```

## TypedDict

```python
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    email: str
    role: str

# Partial TypedDict — all keys optional
class UpdateUserDict(TypedDict, total=False):
    email: str
    role: str

# Mixed required/optional
class CreateOrderDict(TypedDict):
    product_id: int       # required
    quantity: int         # required

class CreateOrderWithMetaDict(CreateOrderDict, total=False):
    notes: str            # optional
```

## Literal Types

```python
from typing import Literal

Role = Literal["admin", "manager", "viewer", "guest"]

def set_role(user_id: int, role: Role) -> None: ...

# mypy will error if you call set_role(1, "superuser")
```

## ClassVar and Final

```python
from typing import ClassVar, Final
from dataclasses import dataclass

@dataclass
class Config:
    MAX_RETRIES: ClassVar[int] = 3  # class-level, not instance field

API_VERSION: Final = "v1"  # cannot be reassigned
```

## Type Narrowing

```python
def process(value: str | int) -> str:
    if isinstance(value, int):
        # mypy knows value is int here
        return str(value * 2)
    # mypy knows value is str here
    return value.upper()

# TypeGuard for custom narrowing functions
from typing import TypeGuard

def is_string_list(items: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in items)

def process_strings(items: list[object]) -> None:
    if is_string_list(items):
        # mypy knows items is list[str] here
        print(", ".join(items))
```

## Generator and Iterator Types

```python
from collections.abc import Generator, Iterator, AsyncGenerator, AsyncIterator

def count_up(limit: int) -> Generator[int, None, None]:
    for i in range(limit):
        yield i

async def stream_users() -> AsyncGenerator[User, None]:
    async for row in db.stream(select(User)):
        yield User.model_validate(row)
```
