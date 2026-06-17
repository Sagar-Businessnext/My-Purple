# Python Code Review Checklist

## Severity Key

| Severity | Meaning |
|----------|---------|
| High | Bug risk or architecture violation — must fix before merge |
| Medium | Quality gap — should fix; document if deferred |
| Low | Style issue — fix when convenient |

## Checklist

### Typing

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| T1 | All public functions have return type annotations | Medium | `def \w+\([^)]*\)\s*:` (missing `->`) |
| T2 | No `Any` without a justification comment | High | `:\s*Any\b` |
| T3 | No untyped `dict` or `list` (use `dict[str, int]` etc.) | Medium | `:\s*dict\b`, `:\s*list\b` |
| T4 | No `Optional[X]` — use `X \| None` (Python 3.10+) | Low | `Optional\[` |
| T5 | Generic types use `list[X]` not `List[X]` | Low | `from typing import.*List` |

### Exception Handling

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| E1 | No bare `except:` | High | `except\s*:` |
| E2 | `except Exception:` must log or re-raise | High | `except Exception` (then read body) |
| E3 | No `pass` inside an except block | High | `except.*:\s*\n\s*pass` |
| E4 | Domain exceptions inherit from a base class | Medium | Manual — check `exceptions.py` |
| E5 | `raise X from e` used when re-raising with chaining | Low | `raise \w+\(` inside except (missing `from e`) |

### Mutable Defaults

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| M1 | No mutable default arguments (`[]`, `{}`, `set()`) | High | `def .*=\s*[\[\{]` |
| M2 | No default value referencing a mutable class attribute | High | Manual — read `__init__` defaults |

### Comprehensions and Loops

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| C1 | No side effects inside list/set/dict comprehensions | Medium | `\[.* for .* if .*\(` (calls inside comprehension) |
| C2 | Comprehensions not used where a plain `for` loop is clearer | Low | judgment call |
| C3 | Generator expressions used instead of list where only iteration needed | Low | `sum(\[`, `any(\[`, `all(\[` — should be generator |

### Architecture and Layering

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| A1 | No ORM queries in router files | High | In `routers/` files: `db.query(`, `session.execute(` |
| A2 | No business logic in router handlers (> 5 lines in handler) | High | manual review |
| A3 | No HTTP client calls in repository files | High | In `repositories/` files: `httpx`, `requests` |
| A4 | Services do not import from routers | High | In `services/`: `from.*routers` |

### Resource Management

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| R1 | File opens use `with open(...)` | High | `open\(` not preceded by `with ` |
| R2 | Database sessions used as context managers | High | manual — check session lifecycle |
| R3 | HTTP clients created with `async with httpx.AsyncClient()` | High | `httpx.AsyncClient()` not in `async with` |

### General Quality

| # | Check | Severity | Grep Pattern |
|---|-------|----------|-------------|
| Q1 | Functions ≤ 40 lines of logic | Low | manual — count lines |
| Q2 | No magic numbers | Medium | `== \d{2,}`, `> \d{2,}` (unexplained literals) |
| Q3 | No commented-out code | Low | `#\s+\w+\(`, `#.*=.*` (patterns suggesting code) |
| Q4 | No `print()` in production code (use logging) | Medium | `print\(` |
| Q5 | `logger = logging.getLogger(__name__)` at module level | Low | manual — check logger setup |
