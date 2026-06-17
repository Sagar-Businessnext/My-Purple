Invoke the **bnac-command-creator** agent to author a new slash-command `.md` file, wiring `command → agent → skill`.

**Agent:** `bnac-command-creator`
**Target:** `$ARGUMENTS` (slash-command slug without leading `/`, required — e.g., `bnac-pag-write`, `bnac-react-scaffold`, `bnac-flutter-scaffold`)

## What to do

1. Delegate to the `bnac-command-creator` agent with these instructions:
   - If `$ARGUMENTS` is a kebab-case slug starting with `bnac-` → infer the target profile from the slug (`bnac-react-*` → `src/stacks/react-ts/commands/`, `bnac-pag-*` → `src/stacks/pag/commands/`, `bnac-dotnet-*` / `bnac-python-*` / `bnac-flutter-*` → their stack; otherwise `src/core/commands/`) and author the command file there, OR (for user-authored commands) at `<cwd>/.claude/commands/<slug>.md`
   - Pair the command with the matching agent slug (e.g., `bnac-react-scaffold` → `react-developer`); if the target agent doesn't exist as a `.md` file under `src/core/agents/` or `src/stacks/**/agents/`, block with a clear message and tell the user to author the agent first via `/bnac-agent-create`
   - If no arguments → **default to the current working folder's basename** (kebab-cased) as the slug. If the basename does not start with `bnac-`, prepend `bnac-` automatically (commands must be `bnac-` prefixed). Tell the user which slug was inferred before authoring. Only ask for clarification if the basename is empty or cannot be normalized.

2. The bnac-command-creator agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, target agent's `.md` file, 2 reference commands)
   - Resolve target path from slug profile prefix
   - Confirm target agent exists; read its tools, skills, and How-You-Work
   - Determine `$ARGUMENTS` shape (file path / folder / slug / PRD path / optional / required)
   - **Write** the command file with Agent line + Target line + What-to-do + Examples (mirroring the agent's How-You-Work)
   - **Read** the written file to verify wiring

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-command-create bnac-pag-verify           → wires to pag-doc-verifier; PRD folder argument
/bnac-command-create bnac-react-pr-approve     → wires to react-pr-approver; PR number argument
/bnac-command-create bnac-flutter-scaffold     → wires to flutter-developer; widget name argument
/bnac-command-create bnac-task-plan            → wires to bnac-task-planner; milestone reference argument
```
