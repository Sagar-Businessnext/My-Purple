Invoke the **python-developer** agent to implement a Python feature end-to-end — models, schemas, services, routers, and tests.

**Agent:** `python-developer`
**Target:** `$ARGUMENTS` (feature description, optionally with a file or module path)

## What to do

1. Delegate to the `python-developer` agent with these instructions:
   - If `$ARGUMENTS` is a feature description → implement the feature across all affected layers (model, schema, service, router, test)
   - If `$ARGUMENTS` includes a file path → focus implementation in and around that file
   - If `$ARGUMENTS` includes a module path → work within that module's directory
   - If no arguments → ask the user for the feature description and the target module

2. The `python-developer` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`) and the milestone status
   - **Read** existing code in the target module before writing anything
   - Implement in dependency order: data layer first (models, schemas, repository), then service, then router
   - Run `ruff check .` and `mypy .` — fix all errors
   - Run `pytest` to confirm all tests pass
   - Commit using conventional commits: `feat(<scope>): <description>`
   - Update milestone task if this work matches an active task

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-python-feature-dev add email verification to user registration
/bnac-python-feature-dev implement order cancellation endpoint  src/orders/
/bnac-python-feature-dev add pagination to the product listing API
```

## Next step

After the feature is implemented, run `/bnac-python-verify` to check code quality and `/bnac-python-test` if additional test coverage is needed.
