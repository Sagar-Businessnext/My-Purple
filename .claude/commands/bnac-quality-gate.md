Invoke the **bnac-quality-gate** agent to run full verification: build, type check, lint, and tests.

**Agent:** `bnac-quality-gate`
**Target:** `$ARGUMENTS` (file or folder path, optional — defaults to full project)

## What to do

1. Delegate to the `bnac-quality-gate` agent with these instructions:
   - If `$ARGUMENTS` is a folder path → scope test run to that path (if tooling supports it)
   - If no arguments → run all checks on the full project

2. The bnac-quality-gate agent will:
   - **Read** project config to detect the stack and available commands
   - **Bash** — Run checks in order: Build → Type Check → Lint → Test
   - Capture output from each step
   - Report results with ✅ PASS / ❌ FAIL / ⚠️ WARN / ⏭️ SKIP per check
   - Output overall verdict

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-quality-gate                           → run full quality gate on entire project
/bnac-quality-gate src/components/Auth/      → run checks scoped to Auth component
/bnac-quality-gate tests/                    → run tests in specific directory
```
