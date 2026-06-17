Invoke the **bnac-agent-creator** agent to author a new agent `.md` file with proper frontmatter, tools, scope, and body structure.

**Agent:** `bnac-agent-creator`
**Arguments:** `$ARGUMENTS` — `<agent-name> [folder] [purpose...]`

## Argument shape (positional)

| # | Name | Required | Default | Notes |
|---|------|----------|---------|-------|
| 1 | `agent-name` | yes | — | Kebab-case slug; becomes the filename. Examples: `react-hook-developer`, `bnac-task-planner`, `pag-doc-writer`. |
| 2 | `folder` | no | **current working directory (cwd)** | Project root where `.claude/agents/` lives. Relative paths resolve against cwd; `.` or `./` means cwd. The file lands at `<folder>/.claude/agents/<agent-name>.md`. |
| 3+ | `purpose` | no | inferred from slug | Free-text role description used to seed the agent's body — e.g. `"creates custom React hooks following rules-of-hooks"`. |

If `agent-name` is omitted, fall back to the cwd basename (kebab-cased) and tell the user which slug was inferred before authoring.

## Destination rule (HARD)

- **Default destination:** `<cwd>/.claude/agents/<agent-name>.md` — i.e., the working project, not user-global.
- **`~/.claude/agents/` is FORBIDDEN.** That folder holds BNAC system agents installed via `bnac install`; custom user agents must not land there.
- **`src/stacks/**/agents/` is FORBIDDEN.** That's the BNAC package source.
- If `<folder>/.claude/agents/` does not exist, create it before writing.
- If a resolved path would fall under either forbidden location, refuse and surface the path to the user.

## What to do

1. Delegate to the `bnac-agent-creator` agent. Pass `$ARGUMENTS` through verbatim and let the agent parse positional args.
2. The bnac-agent-creator agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, project CLAUDE.md if present, 2 reference agents matching role shape)
   - **Resolve destination** = `<folder ?? cwd>/.claude/agents/<agent-name>.md`, with the forbidden-path check above
   - **If the slug matches a BNAC roster agent** (profile prefix `bnac-`/`pag-`/`react-`/`dotnet-`/`python-`/`flutter-` AND already present in the installed `~/.claude/agents/` or `src/core/agents/`, `src/stacks/**/agents/`) → use that existing agent file as the canonical source for tools, model, and skills
   - **Otherwise** (custom user agent) → infer tools and model from the `purpose` text using the role-tools matrix in [agent-authoring-template/reference/frontmatter.md](../skills/agent-authoring-template/reference/frontmatter.md)
   - **Write** the new agent file with canonical frontmatter and body sections
   - **Read** the written file back to verify frontmatter parses
3. After completion, log results to `project/.claude/log.md`.

## Examples

```
# Default — lands in the current project (cwd)
/bnac-agent-create react-hook-developer
  → <cwd>/.claude/agents/react-hook-developer.md

# Same, with a purpose hint to seed the body
/bnac-agent-create react-hook-developer . "creates custom React hooks following rules-of-hooks"
  → <cwd>/.claude/agents/react-hook-developer.md

# Explicit destination folder (e.g., authoring into a sibling project)
/bnac-agent-create my-linter ../other-project "lints docstrings"
  → ../other-project/.claude/agents/my-linter.md

# BNAC roster agent — slug matches an existing installed agent; still lands in cwd
/bnac-agent-create bnac-task-planner
  → <cwd>/.claude/agents/bnac-task-planner.md
```

## What this command does NOT do

- Never writes to `~/.claude/agents/` — reserved for system-installed BNAC agents.
- Never writes to `src/stacks/**/agents/` — that's the BNAC package source.
- Does not also create commands or skills — use `/bnac-command-create` and `/bnac-skill-create` for those.
