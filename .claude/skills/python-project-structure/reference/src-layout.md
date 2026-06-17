# Python src/ Layout Reference

## Standard Directory Tree

```
my-service/
├── pyproject.toml            ← single source of project metadata and tool config
├── README.md
├── .gitignore                ← must include .venv/, __pycache__/, *.egg-info/
├── .venv/                    ← local virtualenv (not committed)
├── src/
│   └── my_service/           ← the importable package (snake_case)
│       ├── __init__.py       ← re-exports only; version string if needed
│       ├── main.py           ← app factory or entry point
│       ├── config.py         ← settings via pydantic-settings or python-decouple
│       ├── models/           ← ORM models (SQLAlchemy, Django ORM)
│       │   └── __init__.py
│       ├── schemas/          ← Pydantic request/response models
│       │   └── __init__.py
│       ├── routers/          ← FastAPI/Flask route handlers (thin — delegate to services)
│       │   └── __init__.py
│       ├── services/         ← business logic (no direct ORM, no HTTP concerns)
│       │   └── __init__.py
│       ├── repositories/     ← database access layer (ORM queries live here)
│       │   └── __init__.py
│       └── exceptions.py     ← domain-specific exception classes
└── tests/
    ├── conftest.py           ← shared fixtures: db session, test client, factories
    ├── unit/                 ← pure unit tests (no I/O)
    │   ├── conftest.py       ← unit-specific fixtures (mocks, stubs)
    │   └── test_user_service.py
    └── integration/          ← tests that hit a real (test) database or HTTP
        ├── conftest.py
        └── test_user_router.py
```

## What Goes Where

| Layer | Directory | Allowed Imports |
|-------|-----------|-----------------|
| Router | `routers/` | `schemas/`, `services/`, `exceptions.py` |
| Service | `services/` | `repositories/`, `models/`, `exceptions.py`, external SDKs |
| Repository | `repositories/` | `models/` only |
| Schema | `schemas/` | stdlib, Pydantic — **no** `models/` imports |
| Model | `models/` | ORM only — **no** `schemas/` or `services/` |
| Config | `config.py` | stdlib, pydantic-settings only |

**Import direction must be one-way.** Circular imports indicate a layering violation.

## Naming Conventions

- **Package directory:** `snake_case` matching the PyPI distribution name with underscores
- **Module files:** `snake_case.py` — `user_service.py`, `order_repository.py`
- **No hyphens** in any directory or file name under `src/`
- **Test files:** prefixed `test_` — `test_user_service.py`

## Anti-Patterns to Avoid

```
# WRONG — flat layout (no src/)
my-service/
├── my_service.py    ← importable from dev directory accidentally
├── tests/
└── pyproject.toml

# WRONG — package name with hyphen
src/
└── my-service/      ← not importable (hyphens invalid in Python identifiers)

# WRONG — logic in __init__.py
# src/my_service/__init__.py
def create_user(...):    ← business logic does not belong here
    ...
```

## `__init__.py` Barrel Pattern

```python
# src/my_service/services/__init__.py
# Correct: only re-export the public API
from .user_service import UserService
from .order_service import OrderService

__all__ = ["UserService", "OrderService"]
```

## `.gitignore` Required Entries

```
.venv/
venv/
__pycache__/
*.egg-info/
.mypy_cache/
.ruff_cache/
.pytest_cache/
dist/
build/
*.pyc
.env
```
