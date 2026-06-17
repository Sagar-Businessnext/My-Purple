---
name: pep8-style
description: PEP 8 essentials for BusinessNext Python services — naming conventions, line length, import ordering, and ruff/black configuration. Applied by python-developer, python-compliance-checker, and python-code-verifier.
user-invocable: false
argument-hint: ""
---

PEP 8 is the Python style standard. This skill covers the rules most relevant to BusinessNext projects and how they are enforced automatically using `ruff` (linting) and `ruff format` (formatting). Where PEP 8 and `ruff` configuration differ, the project's `pyproject.toml` is the authority.

## Additional Resources

- [reference/naming-rules.md](reference/naming-rules.md) — naming conventions with examples for every element type
- [reference/ruff-config.md](reference/ruff-config.md) — standard ruff configuration, rule selection, and per-file ignores

## Steps

1. **Run ruff format** — `ruff format .` applies formatting (line length, quotes, trailing commas); review the diff
2. **Run ruff check** — `ruff check .` reports style and quality violations; `ruff check --fix .` auto-fixes safe ones
3. **Check imports** — stdlib first, then third-party, then local; `ruff --select I` checks isort order
4. **Check naming** — verify snake_case for variables/functions/modules, PascalCase for classes, UPPER_SNAKE_CASE for constants
5. **Check line length** — lines over 100 characters are violations (BusinessNext standard is 100; PEP 8 default is 79)
6. **Check blank lines** — 2 blank lines around top-level definitions; 1 inside class bodies

## Rules

- **`ruff format` is the formatter** — do not mix `black` and `ruff format`; choose one per project
- **Line length is 100 in `pyproject.toml`** — do not hard-wrap at 79; let the formatter handle it
- **Import order is enforced by `ruff --select I`** — do not order imports by hand
- **No wildcard imports** — `from module import *` is only permitted in `__init__.py` barrel files with `__all__` defined
- **Constants are `UPPER_SNAKE_CASE`** — a `MAX_RETRIES = 3` at module level is a constant; a `default_timeout = 30` (lowercase) inside a function is a local variable, not a constant
