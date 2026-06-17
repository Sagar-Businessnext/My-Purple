# Command File Format Reference

Every BNAC slash command is one `.md` file. The file has no frontmatter — it's a flat instruction document Claude reads when the user types `/bnac-<name>`.

## Canonical structure

```markdown
Invoke the **<agent-slug>** agent to <one-line purpose>.

**Agent:** `<agent-slug>`
**Target:** `$ARGUMENTS` (<argument shape; mark optional/required and defaults>)

## What to do

1. Delegate to the `<agent-slug>` agent with these instructions:
   - <conditional 1 — if arg is X>
   - <conditional 2 — if arg is Y>
   - <fallback — no arg>

2. The <agent-slug> agent will:
   - <step from agent's How You Work>
   - <step>
   - <step>

3. After completion, log results to `project/.claude/log.md`

## Examples

\`\`\`
/bnac-<name>                                    → <default behavior>
/bnac-<name> <example-arg-1>                    → <behavior with arg 1>
/bnac-<name> <example-arg-2>                    → <behavior with arg 2>
\`\`\`
```

## Section rules

### Opening sentence
- Always: `Invoke the **<agent-slug>** agent to <one-line purpose>.`
- The agent slug is bolded with `**`
- The purpose is one short sentence

### Agent + Target lines
- Both bold-key + value pattern
- `**Agent:** \`<slug>\`` — slug in backticks, must match an existing agent file
- `**Target:** \`$ARGUMENTS\` (<argument metadata>)`

### Argument metadata patterns

| Argument shape | Target line |
|---|---|
| Required slug | `\`$ARGUMENTS\` (component name, required)` |
| Optional file/folder path | `\`$ARGUMENTS\` (file or folder path, optional — defaults to full project)` |
| Required PRD path | `\`$ARGUMENTS\` (PRD folder path, required)` |
| Multi-form argument | `\`$ARGUMENTS\` (PRD path, project description, or milestone reference)` |
| No argument | `\`$ARGUMENTS\` (none — operates on full project)` |

### What to do — three-step pattern

```markdown
1. Delegate to the `<agent>` agent with these instructions:
   - If $ARGUMENTS is X → ...
   - If $ARGUMENTS is Y → ...
   - If no arguments → ...

2. The <agent> agent will:
   - <verb> ...
   - <verb> ...
   - <verb> ...

3. After completion, log results to `project/.claude/log.md`
```

Step 2's bullets MUST mirror the agent's "How You Work" section — same verbs, same order. If the agent says "Read context chain → Read failing files → Edit → re-run build", the command says the same.

### Examples block
- Always a fenced code block (no language tag)
- Show the arrow pattern: `/cmd args  → expected behavior`
- 2–3 examples covering: no-arg default, common arg, edge case
- Use realistic argument values (not `<placeholder>`)

## Target file path resolution by slug

| Slug pattern | Target path |
|---|---|
| `bnac-build-fix`, `bnac-code-review`, `bnac-feature-dev`, `bnac-quality-gate`, etc. (cross-stack) | `src/core/commands/<slug>.md` |
| `bnac-init`, `bnac-update-docs`, `bnac-pipeline-run-all`, `bnac-milestone` (cross-stack) | `src/core/commands/<slug>.md` |
| `bnac-plan`, `bnac-phase-plan`, `bnac-milestone-plan`, `bnac-task-plan`, `bnac-changelog`, `bnac-status-update`, `bnac-agent-create`, `bnac-skill-create`, `bnac-command-create` | `src/core/commands/<slug>.md` (core baseline — planning + meta-creators) |
| `bnac-pag-*` | `src/stacks/pag/commands/<slug>.md` |
| `bnac-react-*` | `src/stacks/react-ts/commands/<slug>.md` |
| `bnac-dotnet-*` | `src/stacks/dotnet/commands/<slug>.md` |
| `bnac-python-*` | `src/stacks/python/commands/<slug>.md` |
| `bnac-flutter-*` | `src/stacks/flutter/commands/<slug>.md` |

## Length

- Typical: 25–50 lines
- Hard ceiling: 70 lines
- If exceeded: the command is doing too much. Move logic into the agent's How-You-Work and keep the command thin.

## Common mistakes

| Mistake | Fix |
|---|---|
| Frontmatter at top | Commands have no frontmatter |
| Multiple agents in step 1 | One command = one agent. Chain via agent's procedure. |
| Step 2 invents new behavior | Step 2 mirrors the agent's How-You-Work — copy from the agent file |
| Placeholder examples (`<arg>`) | Use realistic values |
| Missing log step | Always include "After completion, log results to project/.claude/log.md" |
| Agent slug with leading slash | Agent slug = the bare slug from the agent file's `name:` frontmatter (e.g., `bnac-developer`, `react-developer`, `pag-doc-writer`) — never with a leading slash like `/bnac-developer`. Slash-prefix is reserved for command names. |
