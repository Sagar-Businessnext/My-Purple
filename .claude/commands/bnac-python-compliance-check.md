Invoke the **python-compliance-checker** agent to verify BusinessNext-specific Python conventions — project structure, module naming, import ordering, and layering boundaries.

**Agent:** `python-compliance-checker`
**Target:** `$ARGUMENTS` (optional path to check; defaults to entire project)

## What to do

1. Delegate to the `python-compliance-checker` agent with these instructions:
   - If `$ARGUMENTS` is a path → restrict check to that directory or file
   - If no arguments → check the entire project

2. The `python-compliance-checker` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - Verify the project directory structure: `src/`, `tests/`, `pyproject.toml`
   - Check module and package naming: `snake_case` throughout
   - Run `ruff check --select I` for import ordering violations
   - Grep for wildcard imports outside barrel `__init__.py` files
   - Check layering: no ORM queries in routers, no router imports in services
   - Verify `pyproject.toml` completeness: required sections and key settings
   - Check `__init__.py` files for business logic
   - Produce a structured compliance report with blockers and warnings
   - Log the check summary to `project/.claude/log.md`

3. The agent does not modify code — findings are returned as a report

## Examples

```
/bnac-python-compliance-check
/bnac-python-compliance-check src/
/bnac-python-compliance-check src/orders/
```

## Next step

After reviewing findings, fix blockers before running `/bnac-python-pr-approve`. Warnings can be addressed in a follow-up.
