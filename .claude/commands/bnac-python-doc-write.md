Invoke the **python-doc-writer** agent to write or improve docstrings, README files, and API reference documentation for a Python service.

**Agent:** `python-doc-writer`
**Target:** `$ARGUMENTS` (module path, `readme`, `api`, or directory path)

## What to do

1. Delegate to the `python-doc-writer` agent with these instructions:
   - If `$ARGUMENTS` is a module path (e.g., `src/users/service.py`) → add docstrings to all undocumented public functions and classes in that file
   - If `$ARGUMENTS` is a directory path → document all Python files in that directory
   - If `$ARGUMENTS` is `readme` → write or update the project `README.md` using the `python-readme-template` skill
   - If `$ARGUMENTS` is `api` → generate an API reference docs page from existing docstrings
   - If no arguments → ask the user what to document

2. The `python-doc-writer` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - Determine the docstring style from `pyproject.toml` (Google style default)
   - **Read** source files before writing any documentation
   - Add or improve docstrings without modifying any business logic
   - Apply `python-docstrings` skill for style, `python-readme-template` for README structure
   - Log documentation targets and coverage delta to `project/.claude/log.md`

3. The agent does not run code or change logic — only documentation changes are made

## Examples

```
/bnac-python-doc-write src/users/service.py
/bnac-python-doc-write src/orders/
/bnac-python-doc-write readme
/bnac-python-doc-write api
```

## Next step

After writing documentation, run `/bnac-python-verify` to confirm the documented code still passes ruff and mypy (doc changes occasionally introduce whitespace issues).
