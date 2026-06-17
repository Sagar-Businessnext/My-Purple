---
name: python-patterns
description: Modern Python 3.11+ structural patterns — context managers, generators, dataclasses vs Pydantic, Protocol-based interfaces, async/await, and dependency injection. Applied by python-developer and python-migrator.
user-invocable: false
argument-hint: ""
---

Core Python patterns used across BusinessNext Python services. These patterns are idiomatic Python 3.11+ — they leverage the standard library where possible and avoid over-engineering. Each pattern has a specific context where it is the right choice.

## Additional Resources

- [reference/dataclasses-vs-pydantic.md](reference/dataclasses-vs-pydantic.md) — when to use `@dataclass` vs `pydantic.BaseModel`; conversion patterns
- [reference/async-patterns.md](reference/async-patterns.md) — async/await correctly, avoiding blocking calls, structured concurrency

## Steps

1. **Context managers** — use `contextlib.contextmanager` or `__enter__`/`__exit__` for any resource that needs guaranteed cleanup (database sessions, file handles, temporary directories)
2. **Generators** — use generator functions for sequences that should not be fully materialized in memory; prefer `yield from` for delegation
3. **Dataclasses** — use `@dataclass` for internal value objects with no validation; use `pydantic.BaseModel` for any data crossing a trust boundary (API input/output, config)
4. **Protocol** — define interfaces with `typing.Protocol` instead of ABC when structural subtyping is sufficient; this keeps implementations decoupled from the interface definition
5. **Async/await** — all FastAPI route handlers are `async def`; all database access using SQLAlchemy async engine uses `await`; never call blocking I/O inside an async context without `asyncio.to_thread`
6. **Dependency injection** — inject dependencies (repositories, external clients, settings) as constructor parameters or FastAPI `Depends()`; never instantiate them inside service functions

## Rules

- **Context managers over try/finally** — if resource cleanup can be expressed as a context manager, use one
- **No bare generators as public API** — wrap generators in a class or use `list()` at the boundary if the caller expects a sequence
- **Dataclass for internal; Pydantic for external** — data that enters from HTTP, files, or env vars uses Pydantic; data that stays inside the service layer uses `@dataclass`
- **Protocol over ABC for duck-typed interfaces** — avoids the inheritance hierarchy; allows third-party classes to satisfy the interface without modification
- **Async all the way** — do not mix `async def` and synchronous blocking database calls; an async route calling a sync repository defeats the async benefit
- **No `asyncio.run()` inside service code** — that is the entry point's job; service code is always called from within an event loop
