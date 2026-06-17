Invoke the **bnac-developer** agent to update project documentation after milestone changes or significant code changes.

**Agent:** `bnac-developer`
**Target:** `$ARGUMENTS` (optional — specific doc file to update, or omit to update all project context files)

## What to do

1. Read the current project context files:
   - `project/.claude/CLAUDE.md` — project structure, build commands, conventions
   - `project/.claude/SUMMARY.md` — project overview, tech stack, architecture
   - `project/.claude/milestone-status.md` — milestone progress

2. Scan the actual project state:
   - **Glob** the project structure to detect changes (new directories, new files)
   - **Read** `package.json` / `*.csproj` / `pyproject.toml` for dependency changes
   - **Grep** for new exports, new routes, new components

3. Update each context file to reflect reality:

   **CLAUDE.md updates:**
   - Project structure tree (new directories/files)
   - Build commands (if changed)
   - Conventions (if new patterns emerged)
   - Design system status

   **SUMMARY.md updates:**
   - Architecture changes
   - New tech stack additions
   - Key decisions made during milestone

   **milestone-status.md updates:**
   - Verify task completion status matches actual state
   - Update progress counts

4. Output a diff summary showing what was updated and why

5. Log to `project/.claude/log.md`

## When to run

- After completing a milestone (`/bnac-milestone complete`)
- After significant refactoring
- After adding new dependencies or tools
- When context files feel out of date

## Examples

```
/bnac-update-docs                            → update all project context files
/bnac-update-docs project/.claude/CLAUDE.md  → update only project CLAUDE.md
/bnac-update-docs project/.claude/SUMMARY.md → update only SUMMARY.md
```
