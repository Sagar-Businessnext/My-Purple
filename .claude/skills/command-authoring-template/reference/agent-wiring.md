# Agent Wiring Reference

Every command wires to exactly one agent. This file describes how to pick the right agent and how to verify the wiring is sound.

## The wiring contract

A command file is a thin invocation layer. The runtime contract:

```
User types     →  /bnac-<name> [args]
Claude reads   →  src/.../<name>.md  (the command file)
Command says   →  Delegate to <agent-slug>
Claude invokes →  <agent-slug>'s .md file (the agent definition)
Agent executes →  Following its "How You Work" procedure
Agent logs     →  project/.claude/log.md
```

For this to work end-to-end, three things must align:
1. **Command file slug** — matches what user typed
2. **Agent slug in command** — matches an existing agent `.md` file's `name:` field
3. **Agent's `Invocation` section** — references this command back

## Verifying wiring before authoring a command

Before writing `bnac-<name>.md`:

1. **Read the agent file** the command will delegate to. Confirm:
   - `name:` field matches the slug you're about to use
   - The agent's `Invocation` section either already lists this command, or you'll add it after
   - The agent's tools support the command's intent (don't write a fix command that targets a read-only agent)
2. **Check for existing commands** that already invoke this agent. If 3+ commands already exist, the agent may be overloaded — flag for review.
3. **Confirm the command appears in the global catalog** — after authoring, list it in `src/global/COMMANDS.md` (and reference the agent in `src/global/AGENTS.md`) so the installed harness picks it up.

## Bidirectional sync

When you author a new command, you also need to update the agent's `Invocation` section to list it:

```markdown
## Invocation

This agent is invoked by:
- `/bnac-<existing-cmd>` — <purpose>
- `/bnac-<new-cmd>` — <purpose>     ← add this line
```

If you forget this step, the agent file becomes stale documentation. Treat it as part of the command-creation workflow.

## Argument-shape conventions per agent type

| Agent type | Common argument shapes |
|---|---|
| **Developer** | file path / folder path / no arg |
| **Planner** | PRD path / description / milestone reference |
| **Reviewer / Verifier** | file path / folder path / PR number |
| **Doc Writer** | scope description / target path |
| **Meta-creator** | slug / target profile (slug usually carries profile prefix) |
| **PR Approver** | PR number / branch name |

If the command's argument shape doesn't fit the agent's accepted shapes, the wiring is off — either the wrong agent is targeted, or the agent needs to be extended.

## One agent, multiple commands — when it's OK

Several commands legitimately wire to the same agent if each command represents a distinct **invocation pattern**, not just a distinct argument:

✅ Good:
- `/bnac-build-fix` → `bnac-developer` (run build, parse errors, fix)
- `/bnac-feature-dev` → `bnac-developer` (read plan, implement feature, commit)
- `/bnac-pipeline-run-all` → `bnac-developer` (orchestrate PRD-to-project)

Each is a different pattern of work the `bnac-developer` agent can do.

❌ Bad:
- `/bnac-build-fix-typescript` → `bnac-developer`
- `/bnac-build-fix-eslint` → `bnac-developer`
- `/bnac-build-fix-test` → `bnac-developer`

These are arguments, not patterns. Use one command with arg-based dispatch.

## Anti-patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| Command delegates to "developer or reviewer depending on arg" | Two-agent commands are fragile and confuse the runtime | Split into two commands |
| Command does work itself before delegating | Commands have no tools — they only delegate | Move logic into the agent |
| Command instructs agent to ignore a rule | Rules are non-negotiable | If the rule shouldn't apply, fix the rule, not the command |
| Command invokes a non-existent agent | The runtime will fail at execution | Author the agent first via `/bnac-agent-create` |
| Command repeats the agent's full procedure | Duplication that drifts | Step 2 mirrors agent How-You-Work; don't expand |

## Cross-references

When a command's existence implies skill or rule changes:
- New skill needed? Author it via `/bnac-skill-create` BEFORE the command is wired
- Rule changes? Coordinate with the rules folder; commands don't change rules
- New agent needed? Author it via `/bnac-agent-create` first; never reference a phantom agent
