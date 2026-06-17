# Agent Frontmatter Reference

Every BNAC agent `.md` file begins with YAML frontmatter. Field order matters for diff readability — keep the order below.

## Required fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Kebab-case slug, must equal filename. Example: `bnac-task-planner` |
| `description` | string | yes | One line. Starts with role title and `—`. Sets up auto-delegation. |
| `model` | enum | yes | `opus` (planning, review, meta) or `sonnet` (code, docs, scaffolds) |
| `tools` | list | yes | Subset of `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash` |
| `scope` | list | yes | Glob patterns the agent is allowed to touch |
| `skills` | list | yes | List of skill slugs the agent depends on (may be empty: `[]`) |

## Tool Selection by Role

| Role | Tools | Why |
|---|---|---|
| **Planner** (feature, milestone, task, phase) | Read, Glob, Grep | Read-only — analysis, never modifies |
| **Developer** (any stack) | Read, Write, Edit, Glob, Grep, Bash | Authors code, runs build/tests |
| **Code Verifier / Reviewer** | Read, Glob, Grep, Bash *(git only)* | Read-only review with git diff/log/blame |
| **WCAG / RTL / Compliance Checker** | Read, Glob, Grep | Read-only audits |
| **Security Checker** | Read, Glob, Grep, Bash | Reads code, may run static analysis (bandit, etc.) |
| **PR Approver** | Read, Glob, Grep, Bash *(git + gh)* | Final sign-off — reads code + CI + git history |
| **Doc Writer** | Read, Write, Edit, Glob, Grep | Authors docs, no code, no shell |
| **Meta-Creator** (agent/skill/command) | Read, Write, Edit, Glob, Grep | Authors `.md` files, no shell needed |
| **Changelog / Status Agent** | Read, Write, Edit, Glob, Grep, Bash *(git only)* | Reads git history, writes CHANGELOG/status reports |

## Model Selection

| Role | Model | Why |
|---|---|---|
| Planning (any flavor) | `opus` | Synthesis across many files, multi-step reasoning |
| Code review / verification | `opus` | Subtle correctness judgments |
| Meta-creation (agent/skill/command) | `opus` | Must understand other agents' shapes |
| Code authoring | `sonnet` | Bulk file generation, well-defined patterns |
| Doc writing | `sonnet` | Pattern-following, less ambiguity |
| Scaffolding | `sonnet` | Mechanical |
| PR approval | `opus` | Final judgment call |

## Scope Patterns by Profile

```yaml
# Cross-stack agents
scope:
  - "**/*"
  - "project/.claude/log.md"

# React stack agents
scope:
  - "src/components/**/*"
  - "src/pages/**/*"
  - "src/**/*.ts"
  - "src/**/*.tsx"
  - "src/**/*.scss"
  - "project/.claude/log.md"

# .NET agents
scope:
  - "**/*.cs"
  - "**/*.csproj"
  - "**/*.sln"
  - "project/.claude/log.md"

# Read-only planner / verifier
scope:
  - "**/*"
  - "project/.claude/**/*"
  - "~/.claude/CLAUDE.md"
  - "~/.claude/rules/**/*"

# Meta-creator (BNAC platform internals)
scope:
  - "src/stacks/**/agents/*.md"  # for agent-creator
  - "src/stacks/**/skills/**/*.md"  # for skill-creator
  - "src/stacks/**/commands/*.md"  # for command-creator
  - "src/global/<CATALOG>.md"
  - "project/.claude/log.md"
```

## Frontmatter examples

### Developer agent
```yaml
---
name: react-developer
description: Senior React+TypeScript developer with BNDS design system expertise. Builds components and pages following the 8-file separation pattern.
model: sonnet
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
scope:
  - "src/components/**/*"
  - "src/**/*.tsx"
  - "project/.claude/log.md"
skills:
  - react-component-pattern
  - use-design-system
  - use-design-tokens
---
```

### Planner agent
```yaml
---
name: bnac-task-planner
description: BNAC task planning specialist — breaks a milestone into individual tasks with dependencies, complexity, and rough estimates. Does NOT write code.
model: opus
tools:
  - Read
  - Glob
  - Grep
scope:
  - "**/*"
  - "project/.claude/**/*"
skills:
  - task-estimation
---
```

### Verifier agent
```yaml
---
name: react-code-verifier
description: React code review specialist — reviews React+TS code for separation pattern, BNDS adherence, import boundaries, and React best practices.
model: opus
tools:
  - Read
  - Glob
  - Grep
  - Bash
scope:
  - "src/**/*.tsx"
  - "src/**/*.ts"
  - "src/**/*.scss"
skills:
  - react-code-review
  - react-system-compliance
---
```

## Common mistakes

| Mistake | Fix |
|---|---|
| `tools: Read, Write` (string) | Must be a YAML list with `- ` prefix |
| Missing `model:` | Defaults aren't safe; always set explicitly |
| Filename ≠ name field | Must match exactly, case-sensitive |
| Adding Bash to a planner | Planners are read-only. Use Grep instead. |
| Adding Write to a verifier | Verifiers don't fix code. Report findings only. |
| Empty `scope` | Always declare scope; use `["**/*"]` if truly broad |
