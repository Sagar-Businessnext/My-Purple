# Python Naming Rules Reference

## Quick Reference Table

| Element | Convention | Example |
|---------|-----------|---------|
| Module / package | `snake_case` | `user_service.py`, `my_service/` |
| Function | `snake_case` | `get_user()`, `calculate_discount()` |
| Method | `snake_case` | `def save(self) -> None:` |
| Variable | `snake_case` | `user_id`, `order_total` |
| Parameter | `snake_case` | `def create(user_id: int):` |
| Class | `PascalCase` | `UserService`, `OrderRepository` |
| Exception | `PascalCase` + `Error` suffix | `UserNotFoundError`, `InsufficientFundsError` |
| Type alias | `PascalCase` | `UserId = int` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PAGE_SIZE` |
| Private function/method | `_single_leading_underscore` | `def _validate_email(...)` |
| Private attribute | `_single_leading_underscore` | `self._cache: dict[str, User]` |
| Name-mangled attribute | `__double_leading_underscore` | `self.__secret_key` (use sparingly) |
| Dunder method | `__dunder__` | `__init__`, `__repr__`, `__len__` |
| Test function | `test_` prefix | `test_create_user_returns_201` |
| Test class | `Test` prefix | `class TestUserService:` |
| Fixture | `snake_case` | `@pytest.fixture def make_user():` |

## Naming Conventions by Layer

### Models (ORM)

```python
# Class: PascalCase; table name: snake_case (usually auto-derived)
class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str] = mapped_column(unique=True)  # snake_case column
    is_active: Mapped[bool] = mapped_column(default=True)
```

### Schemas (Pydantic)

```python
# Request: PascalCase + Request suffix
class CreateUserRequest(BaseModel): ...

# Response: PascalCase + Response suffix
class UserResponse(BaseModel): ...

# Update (partial): PascalCase + Update suffix
class UpdateUserRequest(BaseModel): ...
```

### Services

```python
# Class: PascalCase + Service suffix
class UserService:
    # Methods: verb_noun pattern
    async def create_user(self, request: CreateUserRequest) -> UserResponse: ...
    async def get_user_by_id(self, user_id: int) -> User | None: ...
    async def update_user(self, user_id: int, updates: UpdateUserRequest) -> UserResponse: ...
    async def delete_user(self, user_id: int) -> None: ...
```

### Repositories

```python
# Class: PascalCase + Repository suffix
class UserRepository:
    async def find_by_id(self, user_id: int) -> User | None: ...
    async def find_by_email(self, email: str) -> User | None: ...
    async def create(self, data: dict[str, object]) -> User: ...
    async def update(self, user_id: int, data: dict[str, object]) -> User | None: ...
    async def delete(self, user_id: int) -> bool: ...
```

### Constants

```python
# Module-level constants: UPPER_SNAKE_CASE
MAX_LOGIN_ATTEMPTS: Final[int] = 5
DEFAULT_SESSION_TTL_SECONDS: Final[int] = 3600
SUPPORTED_CURRENCIES: Final[frozenset[str]] = frozenset({"USD", "EUR", "GBP", "INR"})
```

### Exceptions

```python
# Exceptions: PascalCase, always end in Error
class UserNotFoundError(ValueError):
    """Raised when a user lookup fails and the caller must handle the absence."""

class DuplicateEmailError(ValueError):
    """Raised when attempting to register an email that already exists."""

class InsufficientFundsError(RuntimeError):
    """Raised when a transaction would exceed the account balance."""
```

## Anti-Patterns

```python
# WRONG — camelCase for functions/variables (JavaScript style)
def getUser(userId):
    userEmail = ...

# WRONG — PascalCase for a function
def CreateUser():
    ...

# WRONG — lowercase for a class
class userservice:
    ...

# WRONG — inconsistent exception naming
class notFound(Exception):     # missing Error suffix, wrong case
class UserNotFoundException:   # Exception suffix, not Error

# WRONG — generic names that carry no meaning
data = get_data()
result = process(result)
```
