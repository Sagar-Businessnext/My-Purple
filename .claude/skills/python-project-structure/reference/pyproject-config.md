# pyproject.toml Configuration Reference

## Minimal Required `pyproject.toml`

Every BusinessNext Python service must have these four tool sections configured.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-service"
version = "0.1.0"
description = "Brief description of the service"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110",
    "pydantic>=2.0",
    "sqlalchemy>=2.0",
    "uvicorn[standard]>=0.28",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",          # async test client for FastAPI
    "mypy>=1.9",
    "ruff>=0.4",
    "factory-boy>=3.3",
]

[tool.hatch.build.targets.wheel]
packages = ["src/my_service"]

# ─── Ruff ────────────────────────────────────────────────────────────────────

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long — handled by formatter
]

[tool.ruff.lint.isort]
known-first-party = ["my_service"]

[tool.ruff.format]
quote-style = "double"

# ─── mypy ────────────────────────────────────────────────────────────────────

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = false

# Per-module overrides for third-party packages without stubs:
[[tool.mypy.overrides]]
module = ["some_untyped_library.*"]
ignore_missing_imports = true

# ─── pytest ──────────────────────────────────────────────────────────────────

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"          # required by pytest-asyncio
addopts = "--strict-markers -q"
markers = [
    "unit: pure unit tests",
    "integration: tests requiring external resources",
    "slow: tests that take > 5 seconds",
]

# ─── coverage ────────────────────────────────────────────────────────────────

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Key Decisions Explained

### Why `hatchling` over `setuptools`?

`hatchling` reads `pyproject.toml` natively with zero additional config files. It does not require a `MANIFEST.in` or a `setup.cfg`. Any PEP 517-compatible build frontend (pip, build) works.

### Why `strict = true` in mypy?

Strict mode enables:
- `disallow_untyped_defs` — all functions must be annotated
- `disallow_any_generics` — `List` must be `list[str]`, not bare `List`
- `warn_return_any` — functions cannot return untyped `Any` silently

Start strict. Suppressing individual files with `# type: ignore` on a module-by-module basis when gradually adopting is acceptable; widening to `strict = false` project-wide is not.

### Why `asyncio_mode = "auto"`?

Without this, every async test function needs `@pytest.mark.asyncio`. With `"auto"`, pytest-asyncio detects coroutines automatically. This reduces boilerplate in FastAPI test suites where most tests are async.

## Installing for Development

```bash
# Create virtualenv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install project + dev dependencies
pip install -e ".[dev]"

# Verify tools are available
ruff --version
mypy --version
pytest --version
```
