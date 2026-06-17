---
name: agent-authoring-template
description: Standard structure for authoring BNAC agent .md files — frontmatter shape, body sections, tool selection, model selection.
user-invocable: false
argument-hint: ""
---

Author new BNAC agent `.md` files with a consistent shape: well-formed frontmatter, the canonical body sections in the right order, and tool/model choices that match the agent's role.

## Additional Resources

- [reference/frontmatter.md](reference/frontmatter.md) — frontmatter field reference (name, description, model, tools, scope, skills)
- [reference/body-structure.md](reference/body-structure.md) — canonical body section order with examples per role type

## Steps

1. **Identify the role type**: planner, developer, verifier/reviewer, PR approver, doc writer, meta-creator
2. **Pick tools from the role-tools matrix** (see `reference/frontmatter.md` § Tool Selection)
3. **Pick the model** based on cognitive load:
   - `opus` — planning, deep review, verification, meta-creation
   - `sonnet` — code authoring, doc writing, scaffolding
4. **Pick the skills** the agent depends on (must already exist or be authored alongside)
5. **Set scope globs** to the minimal set of paths the agent reads/writes
6. **Author body sections in order**: Tools Available → Context-First → Invocation → How You Work → Rules You Follow → What You Do NOT Do
7. **Verify by reading** — confirm frontmatter parses, body matches the role-specific template

## Rules

- **One purpose per agent** — If the role description has more than one verb, split into two agents
- **Context-First section is mandatory** — Always lists the 4-step context chain
- **Anti-scope is mandatory** — "What You Do NOT Do" prevents agent overlap
- **Strict tool minimization** — A planner has Read/Glob/Grep only. A reviewer has those plus Bash for git. A developer adds Write/Edit. A meta-creator gets Write/Edit but no Bash.
- **Frontmatter is YAML** — quote strings with colons, use list syntax (`- item`) for arrays
- **Filename = name field** — `<slug>.md` where slug is the `name:` value
