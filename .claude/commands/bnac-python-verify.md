Invoke the **python-code-verifier** agent to review Python code for typing completeness, idiomatic patterns, architectural layering, and ruff/mypy compliance.

**Agent:** `python-code-verifier`
**Target:** `$ARGUMENTS` (optional path to review; defaults to entire project)

## What to do

1. Delegate to the `python-code-verifier` agent with these instructions:
   - If `$ARGUMENTS` is a path → restrict review to that directory or file
   - If no arguments → review the entire project

2. The `python-code-verifier` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - Run `ruff check <path>` and `mypy <path>` and record all errors
   - Scan source files for patterns the tools miss: missing annotations, broad `except:`, mutable defaults, layering violations
   - Produce a structured findings table (file, line, severity, category, description)
   - Log the review summary to `project/.claude/log.md`

3. The agent does not modify code — findings are returned as a report for the developer to act on

## Examples

```
/bnac-python-verify
/bnac-python-verify src/orders/
/bnac-python-verify src/users/service.py
```

## Next step

After reviewing the findings, use `/bnac-python-feature-dev` to fix identified issues, then re-run `/bnac-python-verify` to confirm clean.
