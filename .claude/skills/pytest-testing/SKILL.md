---
name: pytest-testing
description: pytest fundamentals for BusinessNext Python services — fixtures, parametrize, monkeypatch, conftest organization, and AAA pattern. Used by python-unit-test-developer.
user-invocable: false
argument-hint: ""
---

Practical pytest patterns used across BusinessNext Python services. This skill covers how to structure fixtures for reuse, write parametrized tests for equivalence classes, patch external dependencies with `monkeypatch` or `pytest-mock`, and organize `conftest.py` at the right scope level.

## Additional Resources

- [reference/fixture-patterns.md](reference/fixture-patterns.md) — scoped fixtures, factory fixtures, async fixtures, fixture composition
- [reference/parametrize-recipes.md](reference/parametrize-recipes.md) — parametrize with IDs, indirect fixtures, matrix parameters, marking specific cases

## Steps

1. **Identify the boundary** — determine if the test is unit (no I/O) or integration (database, HTTP); place in `tests/unit/` or `tests/integration/`
2. **Write the test name** — `test_<function>_<scenario>_<expected_outcome>` (three parts, underscore-separated)
3. **Arrange** — set up all inputs and mocks; this is the largest block in most tests
4. **Act** — call the single function or endpoint under test; one `await` or one call
5. **Assert** — make one or more assertions about the single outcome; each assertion tests one aspect
6. **Extract fixtures** — if arrange code is used in more than one test, extract it to a fixture at the appropriate conftest scope
7. **Parametrize equivalence classes** — identify boundary values and error paths; parametrize rather than duplicate test bodies
8. **Patch external dependencies** — use `monkeypatch.setattr` for module-level patching; use `pytest-mock`'s `mocker.patch` for method-level patching

## Rules

- **One behavior per test** — a test that verifies two unrelated behaviors should be two tests
- **Deterministic** — no `time.sleep`, no random data without a fixed seed, no dependency on test execution order
- **Fixtures return values, not mutable containers** — return the object the test needs; do not return dicts with many keys
- **`conftest.py` at the lowest applicable scope** — a fixture used only in `tests/unit/` does not belong in `tests/conftest.py`
- **Parametrize IDs are mandatory for > 3 cases** — use `ids=` or `pytest.param(..., id="")` so failure output is readable
- **No assertions in fixtures** — fixtures set up; tests assert
