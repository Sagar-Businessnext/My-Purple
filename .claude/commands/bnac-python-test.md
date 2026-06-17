Invoke the **python-unit-test-developer** agent to write pytest test suites for a module or feature.

**Agent:** `python-unit-test-developer`
**Target:** `$ARGUMENTS` (module path or feature description)

## What to do

1. Delegate to the `python-unit-test-developer` agent with these instructions:
   - If `$ARGUMENTS` is a module path (e.g., `src/users/service.py`) → write unit tests for all public functions in that module
   - If `$ARGUMENTS` is a feature description → write tests covering the described behavior
   - If `$ARGUMENTS` is a test file path → extend the existing test file with additional coverage
   - If no arguments → ask the user which module or feature to test

2. The `python-unit-test-developer` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - **Read** the module under test to identify all public functions and edge cases
   - **Read** `tests/conftest.py` to reuse existing fixtures before creating new ones
   - Write tests following the AAA pattern (Arrange, Act, Assert)
   - Use `@pytest.mark.parametrize` for equivalence classes and boundary conditions
   - Run `pytest tests/<module>/ -v` to confirm all tests pass
   - Run `pytest --cov=src/<module> --cov-report=term-missing` to check coverage

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-python-test src/users/service.py
/bnac-python-test add tests for the discount calculation feature
/bnac-python-test tests/unit/test_order_service.py
```

## Next step

After writing tests, run `/bnac-python-verify` to ensure the tested code also passes linting and type checks.
