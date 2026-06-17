# Dataclasses vs Pydantic Reference

## Decision Table

| Criteria | Use `@dataclass` | Use `pydantic.BaseModel` |
|----------|-----------------|--------------------------|
| Data source | Internal (stays in service layer) | External (API input, config, file) |
| Validation needed | No | Yes |
| JSON serialization needed | Rarely | Yes (`model.model_dump()`) |
| Immutability needed | `@dataclass(frozen=True)` | `model_config = ConfigDict(frozen=True)` |
| Performance critical (no I/O) | Preferred | Fine but heavier |
| ORM row representation | `@dataclass` or plain class | Not recommended |

## `@dataclass` Patterns

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass
class UserContext:
    """Carries the authenticated user through the request lifecycle."""
    user_id: int
    role: str
    tenant_id: str

    # ClassVar is not included in __init__ or __repr__
    ADMIN_ROLE: ClassVar[str] = "admin"

    def is_admin(self) -> bool:
        return self.role == self.ADMIN_ROLE


@dataclass(frozen=True)  # immutable value object
class Money:
    amount: int          # stored in cents to avoid float precision issues
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")
        return Money(amount=self.amount + other.amount, currency=self.currency)


@dataclass
class PaginatedResult[T]:  # generic dataclass (Python 3.12+ syntax)
    items: list[T]
    total: int
    page: int
    page_size: int
```

## Pydantic BaseModel Patterns

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CreateUserRequest(BaseModel):
    """Request body for POST /users."""
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(..., min_length=3, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default="viewer")

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("must be a valid email address")
        return v.lower()


class UserResponse(BaseModel):
    """Response shape for user endpoints."""
    model_config = ConfigDict(from_attributes=True)  # allows ORM model → Pydantic

    id: int
    email: str
    full_name: str
    role: str
```

## Converting Between Layers

```python
# ORM model → Pydantic response (with from_attributes=True)
user_orm = await db.get(UserORM, user_id)
response = UserResponse.model_validate(user_orm)

# Pydantic request → dataclass internal object
request: CreateUserRequest = ...
context = UserCreationContext(
    email=request.email,
    full_name=request.full_name,
    role=request.role,
)

# Pydantic model → dict (for ORM insert)
data = request.model_dump(exclude_unset=True)
```

## Anti-Patterns

```python
# WRONG — Pydantic model used as internal service object with no validation benefit
class OrderCalculation(BaseModel):  # just use @dataclass
    subtotal: float
    tax: float
    total: float

# WRONG — @dataclass used for API input without validation
@dataclass
class CreateOrderRequest:  # use pydantic.BaseModel
    items: list  # no type safety, no validation

# WRONG — mutable default in dataclass
@dataclass
class Cart:
    items: list = []  # shared across all instances! use field(default_factory=list)

# CORRECT
@dataclass
class Cart:
    items: list[str] = field(default_factory=list)
```
