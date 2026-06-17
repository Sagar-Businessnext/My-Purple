# mypy Strictness Reference

## Strictness Levels

| Level | pyproject.toml | What it enforces |
|-------|---------------|-----------------|
| Lenient | `strict = false` (default) | Only type errors where types are given |
| Recommended | Selected flags (see below) | Most useful checks without `Any` bans |
| Strict | `strict = true` | All checks including `disallow_any_generics`, `warn_return_any` |

## Recommended Flags (New Projects)

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

`strict = true` is equivalent to enabling all of:

```toml
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_return_any = true
no_implicit_reexport = true
strict_equality = true
```

## Gradual Adoption Strategy

For migrating a legacy codebase to strict typing, enable flags module by module using overrides.

**Phase 1 — Baseline:** Start with `disallow_untyped_defs = true` only to catch all unannotated functions.

```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true

# Silence third-party packages without stubs for now
[[tool.mypy.overrides]]
module = ["sqlalchemy.*", "fastapi.*", "pydantic.*"]
ignore_missing_imports = true
```

**Phase 2 — Per-module strict:** Annotate one module fully, then enable strict for just that module.

```toml
[[tool.mypy.overrides]]
module = ["my_service.services.*", "my_service.repositories.*"]
strict = true

[[tool.mypy.overrides]]
module = ["my_service.legacy.*"]
ignore_errors = true  # temporary; remove as legacy is migrated
```

**Phase 3 — Full strict:** Once all modules pass, move `strict = true` to the root `[tool.mypy]` section and remove overrides.

## Common mypy Errors and Fixes

### `error: Function is missing a return type annotation`
```python
# WRONG
def get_name():
    return "Alice"

# CORRECT
def get_name() -> str:
    return "Alice"
```

### `error: Returning Any from function declared to return "str"`
```python
# WRONG — json.loads returns Any; mypy doesn't know it's str
import json
def load_name(raw: str) -> str:
    data = json.loads(raw)
    return data["name"]  # Any

# CORRECT — assert or cast the type
def load_name(raw: str) -> str:
    data: dict[str, str] = json.loads(raw)
    return data["name"]
```

### `error: Need type annotation for "items" (hint: "items: list[<type>] = ...")`
```python
# WRONG
items = []  # mypy cannot infer the element type

# CORRECT
items: list[str] = []
```

### `error: Item "None" of "X | None" has no attribute "y"`
```python
# WRONG
user: User | None = find_user(1)
print(user.name)  # user might be None

# CORRECT — narrow before use
user = find_user(1)
if user is None:
    raise ValueError("User not found")
print(user.name)  # mypy knows user is User here
```

## Checking Without the `strict` Flag Breaking Everything

Run mypy in report-only mode to see all issues before committing to strict:

```bash
mypy src/ --strict --no-error-summary 2>&1 | wc -l
# Count the errors; tackle in order of highest-traffic modules first
```
