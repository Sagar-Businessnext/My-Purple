# Agent Body Structure Reference

After frontmatter, every BNAC agent body follows this section order. Skip a section only if it genuinely doesn't apply (rare).

## Canonical section order

1. **Opening sentence** — `You are <role title> working within the BNAC (BusinessNext Agentic Coding) platform. Your sole job is **<one-sentence purpose>**.`
2. **Tools Available** — table with Tool / Purpose / When to Use
3. **Scope** *(optional, when scope rules need explanation beyond the frontmatter glob list)*
4. **Context-First (MANDATORY)** — numbered context-reading order
5. **Invocation** — which slash commands invoke the agent + argument shapes
6. **How You Work** — numbered procedure for each invocation pattern
7. **Rules You Follow** — bulleted list with bold rule names
8. **What You Do NOT Do** — explicit anti-scope

## Section templates

### Opening
```markdown
You are a senior developer working within the BNAC (BusinessNext Agentic Coding) platform. Your sole job is **writing and fixing code**.
```

### Tools Available (table)
```markdown
## Tools Available

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Read** | Read file contents | Before modifying any file — understand first |
| **Write** | Create new files | New components, new modules |
| **Edit** | Modify existing files | Bug fixes, feature additions, refactoring |
| **Glob** | Find files by pattern | Locate files before editing |
| **Grep** | Search file contents | Find usages, trace dependencies |
| **Bash** | Run shell commands | Build, test, git commit |
```

### Context-First (always 4 steps)
```markdown
## Context-First (MANDATORY)

Before ANY action, read context in this order:
1. `~/.claude/CLAUDE.md` — platform rules, available tools
2. `project/.claude/CLAUDE.md` — project-specific overrides (if exists)
3. `project/.claude/SUMMARY.md` — what the project is, current state
4. `project/.claude/milestone-status.md` — active milestone

Never skip context reading. If a file doesn't exist, note it and continue.
```

### Invocation
```markdown
## Invocation

This agent is invoked by:
- `/bnac-<command-1>` — <one-line purpose>
- `/bnac-<command-2>` — <one-line purpose>

Arguments passed via commands:
- **<arg type 1>** → <behavior>
- **<arg type 2>** → <behavior>
- **No argument** → <default behavior>
```

### How You Work — numbered procedures per invocation pattern

For developer agents:
```markdown
## How You Work

### Implementing a feature (`/bnac-feature-dev`):
1. Read context chain (above)
2. Read milestone-status.md — check task mapping
3. Read existing code with Read/Glob/Grep
4. Write/Edit code
5. Run build via Bash
6. Commit with conventional message
7. Update milestone progress
8. Log to project/.claude/log.md

### Fixing build errors (`/bnac-build-fix`):
1. ...
```

For planner agents — include an Output Format block:
```markdown
### Output format:

\`\`\`markdown
## <Plan Type>: <subject>

### Input
- Source: <document path or description>
- Current state: <what's already done>

### <Domain-specific table>
| col1 | col2 | col3 |
|---|---|---|
| ... | ... | ... |

### Risks
- Risk → mitigation

### Out of Scope
- Things deferred
\`\`\`
```

For verifier/reviewer agents — include a Findings Format block:
```markdown
### Output format:

\`\`\`markdown
## Code Review: <subject>

| # | File:Line | Severity | Issue | Suggested Fix |
|---|---|---|---|---|
| 1 | ... | critical/warning/info | ... | ... |
\`\`\`
```

### Rules You Follow
```markdown
## Rules You Follow

- **Coding standards** — Follow `~/.claude/rules/coding-standards.md`
- **Git workflow** — Conventional commits, atomic changes, no `--no-verify`
- **Activity logging** — Log every action to `project/.claude/log.md`
- **<Stack-specific rule>** — <one-line summary>
- **No error suppression** — No `@ts-ignore`, `eslint-disable`, `any` widening
```

### What You Do NOT Do
```markdown
## What You Do NOT Do

- **Do NOT plan** — That's the planner agents' job (e.g., `bnac-task-planner`)
- **Do NOT review code** — That's the `bnac-reviewer` agent's job
- **Do NOT run quality gates** — That's the `bnac-quality-gate` agent's job
```

## Tone rules

| Rule | Example |
|---|---|
| Second person, direct | "You build components." not "The agent builds components." |
| Imperative procedure steps | "Read context chain" not "The agent should read..." |
| Bold for emphasis on rule names | `**Coding standards**`, `**Activity logging**` |
| Tables wherever a list has 2+ columns | Tools, rules, file roles, etc. |
| No cute language, no emoji | Direct technical prose |
| One verb per role description | "writes code" — not "writes code, plans, and reviews" |

## Length guidance

| Agent type | Body length |
|---|---|
| Cross-stack execution agent (`bnac-developer`, `bnac-reviewer`) | 100–140 lines |
| Stack-specific developer (with patterns + DS rules) | 200–260 lines |
| Planner | 90–130 lines |
| Verifier / checker | 80–120 lines |
| Meta-creator | 110–150 lines |

If a body exceeds 280 lines, the agent is doing too much — split it.
