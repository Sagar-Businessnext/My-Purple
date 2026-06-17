---
name: command-authoring-template
description: Standard structure for authoring BNAC slash-command .md files — wiring command → agent → skill, $ARGUMENTS handling, and Examples block.
user-invocable: false
argument-hint: ""
---

Author new BNAC slash-command `.md` files with consistent shape: a thin invocation layer that delegates to a single agent with clear `$ARGUMENTS` handling.

## Additional Resources

- [reference/command-format.md](reference/command-format.md) — canonical command file structure (Agent / Target / What to do / Examples)
- [reference/agent-wiring.md](reference/agent-wiring.md) — how to wire `command → agent → skill` correctly

## Steps

1. **Confirm the target agent exists** — read its `.md` file to verify the slug, tools, and skills
2. **Pick the slash-command name** — must start with `bnac-` and follow `bnac-<verb>-<noun>` or `bnac-<profile>-<verb>` pattern
3. **Determine `$ARGUMENTS` shape** — file path? folder? slug? PRD path? optional or required?
4. **Resolve target file path** from slug profile prefix (see `reference/command-format.md`)
5. **Author the command file** — Agent line + Target line + "What to do" numbered list + Examples block
6. **Mirror the agent's How-You-Work procedure** — step 2 of "What to do" should restate the agent's invocation procedure verbatim, not invent new steps
7. **Always include log-to-`project/.claude/log.md` as the final step**
8. **Add 2–3 realistic Examples** — show argument shapes the agent actually accepts

## Rules

- **Wire to a real agent** — the agent slug must match an actual `.md` file
- **One agent per command** — never delegate to multiple agents from one command (chain via the agent's How-You-Work instead)
- **Command files are short** — 25–50 lines is typical; over 70 lines is a smell
- **`$ARGUMENTS` is the only argument variable** — Claude's command system passes the full argument string as `$ARGUMENTS`
- **Examples are runnable** — every example should be something a user could literally type and have it work
- **Don't add features beyond agent capabilities** — a command is invocation glue, not a workflow definition
