---
name: python-typing
description: Python type hints reference — Generic, TypeVar, Protocol, TypedDict, mypy strictness levels, and gradual typing strategy. Applied by python-developer, python-migrator, and python-code-verifier.
user-invocable: false
argument-hint: ""
---

Practical type annotation patterns for Python 3.11+ in BusinessNext services. Covers the annotation syntax available in modern Python, how to use generics and protocols for reusable typed code, and how to approach mypy strictness when migrating a legacy codebase.

## Additional Resources

- [reference/typing-cheatsheet.md](reference/typing-cheatsheet.md) — quick reference for built-in, generic, and special-form types
- [reference/mypy-strictness.md](reference/mypy-strictness.md) — mypy configuration levels, per-module overrides, gradual adoption strategy

## Steps

1. **Annotate all public function signatures** — parameters and return type; `-> None` must be explicit
2. **Use built-in generics** — `list[str]`, `dict[str, int]`, `tuple[int, str]` (not `List`, `Dict`, `Tuple` from `typing`)
3. **Use `X | None` not `Optional[X]`** — the union syntax is cleaner and removes the `typing` import
4. **Use `TypeVar` for generic functions** — when a function returns the same type it receives, use `TypeVar` so the type is preserved
5. **Use `Protocol` for structural interfaces** — define what a dependency must support without requiring inheritance
6. **Use `TypedDict` for structured dicts** — when a `dict` has a known shape, define it as `TypedDict` instead of `dict[str, Any]`
7. **Run `mypy --strict`** — confirm zero errors before declaring annotations complete
8. **Gradual adoption** — for large existing codebases, enable mypy per-module using `[[tool.mypy.overrides]]` blocks

## Rules

- **No `Any` in new code** — if the type is genuinely unknown, use `object` and add a type guard, or use `TypeVar`
- **No `Union[X, Y]` — use `X | Y`** — the new union syntax applies to Python 3.10+
- **`TypeVar` must be bound or constrained** — bare `TypeVar` with no `bound=` or `constraints=` is usually wrong
- **`Protocol` methods must be annotated** — a Protocol with unannotated methods provides no type safety
- **`TypedDict` keys must be complete** — partial `TypedDict` (missing keys) must use `total=False` explicitly
