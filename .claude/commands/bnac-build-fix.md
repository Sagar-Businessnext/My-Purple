Invoke the **bnac-developer** agent to diagnose and fix build, type, and lint errors.

**Agent:** `bnac-developer`
**Target:** `$ARGUMENTS` (file or folder path, optional — defaults to full project)

## What to do

1. Delegate to the `bnac-developer` agent with these instructions:
   - If `$ARGUMENTS` is a file path → focus on errors in that file
   - If `$ARGUMENTS` is a folder path → focus on errors in that directory
   - If no arguments → fix all project build errors

2. The bnac-developer agent will:
   - Run the build command via **Bash**
   - **Read** failing files to understand the errors
   - **Edit** files to apply fixes
   - Re-run build to verify
   - Repeat until clean

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-build-fix                          → fix all build errors
/bnac-build-fix src/components/Auth/     → fix errors in Auth component
/bnac-build-fix src/utils/formatDate.ts  → fix errors in specific file
```
