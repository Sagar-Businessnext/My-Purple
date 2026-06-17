# Ruff Configuration Reference

## Standard BusinessNext ruff Configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
# src layout tells ruff which paths are first-party for isort
src = ["src"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors (PEP 8)
    "W",    # pycodestyle warnings
    "F",    # pyflakes (unused imports, undefined names)
    "I",    # isort (import ordering)
    "B",    # flake8-bugbear (common bugs)
    "C4",   # flake8-comprehensions (unnecessary list/dict/set calls)
    "UP",   # pyupgrade (use modern Python syntax)
    "SIM",  # flake8-simplify (simplifiable code patterns)
    "RUF",  # ruff-specific rules
    "PTH",  # flake8-use-pathlib (prefer pathlib over os.path)
    "N",    # pep8-naming (naming convention enforcement)
    "ANN",  # flake8-annotations (annotation presence checks)
]
ignore = [
    "E501",    # line too long — handled by formatter, not linter
    "ANN101",  # missing type annotation for `self` — redundant
    "ANN102",  # missing type annotation for `cls` — redundant
    "ANN401",  # dynamically typed expressions (Any) — mypy handles this
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "ANN",   # annotations in tests are optional
    "S101",  # assert in tests is expected
]
"**/migrations/**/*.py" = [
    "ALL",   # generated migration files — do not lint
]

[tool.ruff.lint.isort]
known-first-party = ["my_service"]
force-sort-within-sections = true

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
magic-trailing-comma = true   # preserves trailing commas in multi-line structures
```

## Import Order Rules (isort via ruff)

```python
# 1. Standard library
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypeVar

# 2. Third-party packages (blank line separating from stdlib)
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# 3. First-party (your package — blank line separating from third-party)
from my_service.config import settings
from my_service.models.user import User
from my_service.repositories.user_repository import UserRepository
from my_service.schemas.user import CreateUserRequest, UserResponse
```

## Running ruff

```bash
# Check for all violations
ruff check .

# Auto-fix safe violations (import order, unused imports, etc.)
ruff check --fix .

# Check only import order
ruff check --select I .

# Format all files
ruff format .

# Check formatting without changing files (CI mode)
ruff format --check .

# Show which rules are triggered
ruff check . --show-source
```

## Useful Rule Codes to Know

| Code | Rule | Example Violation |
|------|------|-------------------|
| `F401` | Unused import | `import os` (unused) |
| `F841` | Unused variable | `result = f(); # result never used` |
| `E711` | Comparison to None | `if x == None:` (use `is None`) |
| `E712` | Comparison to bool | `if x == True:` (use `if x:`) |
| `B006` | Mutable default argument | `def f(x=[]):` |
| `B007` | Loop variable not used | `for i in range(n): do()` (use `_`) |
| `B008` | Function call in default | `def f(x=datetime.now()):` |
| `C401` | Set literal | `set([1, 2, 3])` → `{1, 2, 3}` |
| `C416` | Unnecessary comprehension | `[x for x in items]` → `list(items)` |
| `UP006` | Use `list` instead of `List` | `from typing import List` |
| `UP007` | Use `X \| Y` instead of `Union` | `Union[str, int]` → `str \| int` |
| `SIM108` | Ternary instead of if-else | `if c: x = a; else: x = b` → `x = a if c else b` |
| `N802` | Function name not lowercase | `def GetUser():` |
| `N803` | Argument name not lowercase | `def f(UserID: int):` |
| `PTH123` | Use `Path.open()` | `open("file.txt")` → `Path("file.txt").open()` |
