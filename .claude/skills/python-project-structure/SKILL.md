---
name: python-project-structure
description: Standard Python project layout for BusinessNext services — src/ layout, pyproject.toml configuration, package vs module conventions, and virtualenv setup.
user-invocable: false
argument-hint: ""
---

The canonical project layout for Python services at BusinessNext. All new Python projects follow the `src/` layout with a `pyproject.toml`-based configuration. This skill defines the expected directory tree, explains why each piece exists, and covers `pyproject.toml` required sections.

## Additional Resources

- [reference/src-layout.md](reference/src-layout.md) — directory tree, naming conventions, what belongs where
- [reference/pyproject-config.md](reference/pyproject-config.md) — required `pyproject.toml` sections and key settings

## Steps

1. **Verify the root layout** — confirm `src/`, `tests/`, `pyproject.toml` exist at the project root; no `setup.py`
2. **Verify `src/` layout** — the importable package lives at `src/<package_name>/`; no Python files in the root except `conftest.py`
3. **Verify `tests/` layout** — `tests/unit/`, `tests/integration/` subdirectories; `tests/conftest.py` for shared fixtures
4. **Check `pyproject.toml`** — must have `[project]`, `[tool.ruff]`, `[tool.mypy]`, `[tool.pytest.ini_options]` sections
5. **Virtualenv check** — `.venv` or `venv/` is in `.gitignore`; not committed to the repo
6. **`__init__.py` check** — every package directory has one; contains only re-exports, no business logic

## Rules

- **No `setup.py`** — all project metadata in `pyproject.toml` only
- **`src/` layout is mandatory** — prevents accidental imports of the development tree; enforces installability
- **Module names are `snake_case`** — no hyphens, no camelCase in directory or file names under `src/`
- **No business logic in `__init__.py`** — barrel re-exports only (e.g., `from .service import UserService`)
- **Tests mirror source** — `tests/unit/test_user_service.py` tests `src/<pkg>/user_service.py`
- **`conftest.py` at the right scope** — project-wide fixtures at `tests/conftest.py`; module-specific at `tests/<module>/conftest.py`
