Invoke the **bnac-developer** agent to implement a feature end-to-end.

**Agent:** `bnac-developer`
**Target:** `$ARGUMENTS` (feature description, with optional file/folder path)

## What to do

1. Delegate to the `bnac-developer` agent with these instructions:
   - `$ARGUMENTS` describes what to build — a feature, enhancement, or task
   - If a path is included → scope implementation to that area
   - If no path → determine scope from the feature description and project context

2. The bnac-developer agent will:
   - **Read** context chain (CLAUDE.md, SUMMARY.md, milestone-status.md)
   - Check if a plan exists — if not, request one from `/bnac-task-plan --lens feature` first
   - **Glob** + **Read** existing code to understand patterns
   - **Write** / **Edit** code following project conventions
   - **Bash** to run build and verify after each task
   - Commit with conventional format via **Bash**
   - Log work to `project/.claude/log.md`

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-feature-dev add login page                          → implement login feature
/bnac-feature-dev add date picker src/components/          → implement date picker in components
/bnac-feature-dev refactor API error handling src/api/     → refactor scoped to api folder
```
