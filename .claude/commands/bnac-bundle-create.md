Invoke the **bnac-bundle-creator** agent to scaffold a complete project-local bundle in one pass: 1 agent + 1 skill + 1 command, optionally + 1 rule, all wired together. Writes to `<folder>/.claude/` only — never to the BNAC system source.

**Agent:** `bnac-bundle-creator`
**Target:** `$ARGUMENTS` (positional: `<agent-slug> [folder] [purpose...]`, plus optional flag `--with-rule`)

## What to do

1. Delegate to the `bnac-bundle-creator` agent. Pass `$ARGUMENTS` through verbatim — the agent parses positional args and the `--with-rule` flag itself.

2. The bnac-bundle-creator agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, project `CLAUDE.md` if any) and 2 reference files of each type (agent / skill / command / rule)
   - **Resolve** the destination folder (defaults to cwd) — refuse if it would write outside `<folder>/.claude/`
   - **Infer** skill slug and command slug from the agent slug + role suffix (and rule slug if `--with-rule`)
   - **Print the bundle plan** showing all destination paths and inferred slugs, and **wait for the user to confirm** (or send `--skill=<slug>` / `--command=<slug>` / `--rule=<slug>` overrides)
   - **Detect collisions** — refuse the whole bundle if any target path already exists (no partial overwrite)
   - **Write in dependency order:** skill folder → agent → (optional rule) → command — so cross-references resolve cleanly
   - **Verify** all files exist and are wired correctly (agent's `skills:` includes the skill; command's `**Agent:**` points to the agent; if rule, agent body references it)
   - **Log** a single bundle entry to `<folder>/.claude/log.md`

3. After completion, the agent reports: file paths created, wiring verified, and any follow-up commands the user might want (e.g., `/bnac-agent-create` for additional agents, `/bnac-skill-create` for additional skills).

## Argument shape

| # | Arg | Required | Default | Description |
|---|-----|----------|---------|-------------|
| 1 | `agent-slug` | yes | — | Kebab-case agent name with profile prefix. Example: `react-tooltip-developer`. |
| 2 | `folder` | no | cwd | Project root. Bundle lands at `<folder>/.claude/`. |
| 3 | `purpose` | no | — | Free-text role description (rest of args). Improves inference. |
| flag | `--with-rule` | no | off | If present, also create a custom rule and reference it in the agent body. |

## Examples

```
/bnac-bundle-create react-tooltip-developer
   → cwd/.claude/agents/react-tooltip-developer.md
   → cwd/.claude/skills/tooltip-authoring/SKILL.md
   → cwd/.claude/commands/bnac-react-tooltip-create.md

/bnac-bundle-create react-tooltip-developer ./my-app "creates BNDS tooltip components"
   → my-app/.claude/agents/react-tooltip-developer.md
   → my-app/.claude/skills/tooltip-authoring/SKILL.md
   → my-app/.claude/commands/bnac-react-tooltip-create.md

/bnac-bundle-create dotnet-cache-verifier ./service "audits cache invalidation patterns" --with-rule
   → service/.claude/agents/dotnet-cache-verifier.md
   → service/.claude/skills/cache-code-review/SKILL.md
   → service/.claude/commands/bnac-dotnet-cache-verify.md
   → service/.claude/rules/cache-invalidation.md           (custom rule)

/bnac-bundle-create python-celery-test-developer ./worker
   → worker/.claude/agents/python-celery-test-developer.md
   → worker/.claude/skills/celery-testing/SKILL.md
   → worker/.claude/commands/bnac-python-celery-test.md
```

## When to use vs the individual creators

| Use this command (`/bnac-bundle-create`) | Use the individual creators |
|---|---|
| First-time setup of a new agent + the skill that drives it + the command that invokes it | Adding more skills to an existing agent |
| You want one self-contained, wired-up unit | Adding more commands that target an existing agent |
| You want consistent slugs across all 3 (or 4) files | Adding a rule that applies to several agents |
| Default 1:1:1 (or 1:1:1:1 with rule) shape | Anything richer than 1:1:1 |
