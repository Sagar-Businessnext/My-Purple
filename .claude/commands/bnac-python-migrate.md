Invoke the **python-migrator** agent to upgrade legacy Python 2 or pre-typed Python 3 code to modern typed Python 3.11+.

**Agent:** `python-migrator`
**Target:** `$ARGUMENTS` (directory path or file path to migrate)

## What to do

1. Delegate to the `python-migrator` agent with these instructions:
   - If `$ARGUMENTS` is a directory path → migrate all Python files in that directory
   - If `$ARGUMENTS` is a file path → migrate the specific file
   - If no arguments → audit the entire project and produce a migration plan before making any changes

2. The `python-migrator` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - **Glob** all `.py` files and **Grep** for Python 2 constructs and missing type annotations
   - Run automated fixers: `pyupgrade --py311-plus` and `ruff check --fix`
   - Manually add type annotations to all public functions not covered by automated tools
   - Run `mypy .` and `pytest` to confirm no regressions
   - Commit in logical chunks (one commit per file or logical group)

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-python-migrate src/legacy/
/bnac-python-migrate src/users/old_user_service.py
/bnac-python-migrate                              → full project audit with migration plan
```

## Next step

After migration, run `/bnac-python-verify` to confirm ruff/mypy compliance and `/bnac-python-compliance-check` for structural conventions.
