# BusinessNext Agentic Coding Platform (BNAC)

> **Version:** 2.0.0
> **Active content:** 54 agents | 10 rules | 62 commands | 80 skills
> **Profiles:** 5 (`pag`, `react`, `dotnet`, `python`, `flutter`) + expanded `core` baseline (planning hierarchy + meta-creators + context+memory subsystem shipped Phase CMM 2026-05-21 + pipeline governance subsystem shipped 2026-05-22 to close BN AI Dark Factory gaps #2 / #7 / #8 / #9). `ui` profile merged into `react` on 2026-05-11.

## What This Is

You are operating within the **BNAC enterprise coding platform**. Every command, skill, agent, and rule you use comes from this system. It ensures consistency, quality, and compliance across all BusinessNext projects.

This file is your primary entry point. Read it first on every session.

---

## Core AI Instructions (NON-NEGOTIABLE)

These four rules apply to every action you take, before any task-specific guidance. Violating any of them is a blocking failure.

### 1. Follow installed skills — user-level AND project-level

When a skill applies, **use it**. Both tiers count:

- **User-level skills** — `~/.claude/skills/<name>/SKILL.md` (installed by `bnac install`, shared across all projects on the machine)
- **Project-level skills** — `<project>/.claude/skills/<name>/SKILL.md` (project-specific overrides; same filename wins over the user-level version per [Two-Tier Resolution](#two-tier-resolution))

If a skill exists for the task you're doing, load it before acting. Don't reinvent guidance that a skill already covers. Don't skip a skill because you "already know how" — the skill is the contract.

### 2. Stay within the current working directory

**Do not search, read, or modify files outside `cwd`.** For example, if `cwd` is `@app/base-controls`, you must not:

- Glob/grep into sibling monorepo packages (`@app/base-ui`, `@app/utils`, …)
- Read files in `../` or higher
- Modify files outside the project tree

**Exceptions** — these are the only times reaching outside `cwd` is allowed:

- The user explicitly names a path outside `cwd` (e.g. "look at `../base-ui/Button.tsx`")
- A skill, agent, or command file you're loading lives outside `cwd` (e.g. `~/.claude/skills/...`) — reading the skill is allowed; reading other files in the skill's tree is not
- The current working directory itself contains a symlink or alias that legitimately resolves outside

If you think you need to reach outside `cwd` for any other reason, **ask the user first**. Cross-package searches without permission produce noisy, off-scope output.

### 3. Write a concise summary when work is done

After completing a task, end your turn with a brief summary covering:

- **What changed** — the files modified/created/deleted, in `file_path:line_number` format where applicable
- **What's next** — open follow-ups, blockers, or "the user should now run X"

One or two short paragraphs is plenty. The summary is for the user; it does not replace the activity log (rule 4 — that's for posterity).

### 4. Update `<project>/.claude/log.md` on every change

Every action that modifies state — file write/edit/delete, command run, milestone update, quality gate result — must be appended to `<project>/.claude/log.md` with:

- Timestamp
- Command or action taken
- Context files read (which CLAUDE.md, SUMMARY.md, etc.)
- Files modified (paths)
- Result (success / failure / partial)

If the file doesn't exist, create it. If `<project>/.claude/` doesn't exist, run `/bnac-init` first. **Don't batch logs** — log per significant action. **Don't skip logging on failure** — failed actions are valuable context.

---

## Context-First Execution (MANDATORY)

Before executing ANY command, skill, or agent action, you MUST read context in this order:

1. **This file** — `~/.claude/CLAUDE.md` (platform rules, available tools)
2. **Project context** — `project/.claude/CLAUDE.md` (project structure, build commands, conventions, overrides)
3. **Project summary** — `project/.claude/SUMMARY.md` (what the project is, tech stack, architecture, decisions)
4. **Active milestone** — `project/.claude/milestone-status.md` (active milestone, task progress, blockers)
5. **Typed memory index** — `project/.claude/memory/MEMORY.md` (if exists; long-term user/feedback/project/reference facts — see [`/bnac-memory`](#common-commands-quick-reference))
6. **Compact carry-forward** — `project/.claude/context/carry-forward.md` (if exists; stitched summary of completed milestones/phases — auto-built by `/bnac-milestone complete` and `/bnac-phase complete`)

**Never skip context reading.** Every action must be informed by the project's current state.

If project context files don't exist, run `/bnac-init` to create them from templates. Steps 5 and 6 are conditional — projects without `memory/` or `context/` continue to work; running `/bnac-init` on an existing project scaffolds the missing folders without clobbering anything.

**Completed-milestone detail guard:** default load is summary-only. Agents MAY opt up and read a completed milestone's full `*.md` detail when explicitly needed (regression debugging, cross-milestone refactor, or user request) — see [memory-management.md](rules/memory-management.md) and [context-carry-forward](skills/context-carry-forward/) for the rule.

---

## Two-Tier Resolution

BNAC uses a two-tier system. When both tiers have the same file, project-local wins.

| Tier | Location | Installed By | Purpose |
|------|----------|-------------|---------|
| **Global** | `~/.claude/` | `bnac install` | Company-wide standards, shared agents/skills/commands/rules |
| **Project-local** | `project/.claude/` | Pipeline generation or manual | Project-specific agents, domain skills, custom rules |

**Priority: Project-local > Global** — same filename in both = project-local overrides.

---

## Naming Convention (NON-NEGOTIABLE)

Every agent name starts with its **profile prefix**: `bnac-`, `pag-`, `react-`, `dotnet-`, `python-`, `flutter-`.
Every command starts with `/bnac-` so BNAC-provided tooling is instantly recognizable next to user/org content.

Why: collision avoidance (between profiles, with user-created content in `~/.claude/`, and with other org-installed content) and ownership clarity when reporting issues.

---

## Enterprise Standards (NON-NEGOTIABLE)

| # | Standard | Enforcement |
|---|----------|------------|
| 1 | **Context-first execution** | All agents read context before acting |
| 2 | **Git workflow** | Conventional commits, branching strategy, no `--no-verify` |
| 3 | **Coding standards** | Per-stack rules for naming, patterns, security |
| 4 | **Activity logging** | Every action logged to `project/.claude/log.md` |
| 5 | **BNDS design system** (React) | BNDS components only, design tokens, no hardcoded values |
| 6 | **8-file separation pattern** (React) | Components split into types/util/hooks/tsx/scss/test/stories/index |
| 7 | **WCAG 2.2 AA accessibility** (React + Flutter) | All interactive content auditable |
| 8 | **PRD quality gate** (PAG) | 44 critical + 31 warning + 14 cross-reference rules across the 22-section schema |

---

## Available Profiles

Install only the profiles you need. Each profile is self-contained.

| # | Profile | Install Command | Purpose | Agents | Skills | Commands |
|---|---------|----------------|---------|--------|--------|----------|
| 1 | **`core`** (baseline) | `bnac install --profile core` | Cross-stack execution + planning hierarchy + meta-creators (developer/reviewer/quality-gate/milestone-tracker/planner/phase-planner/milestone-planner/task-planner/changelog/status/agent-skill-command-creators/bundle-creator) + context+memory subsystem (memory-curator + context-compactor — Phase CMM 2026-05-21) + pipeline governance subsystem (pipeline-state-tracker / go-nogo-approver / cross-llm-reviewer / kpi-tracker — 2026-05-22, closes BN AI Dark Factory gaps #2 / #7 / #8 / #9). Typed long-term memory via `/bnac-memory`, hierarchical compaction via `/bnac-phase` + `/bnac-context`, formal 8-stage state machine via `/bnac-pipeline-stage`, GO/NO-GO via `/bnac-go-nogo`, consensus review via `/bnac-cross-llm-review`, KPI evidence loop via `/bnac-kpi`. | 20 | 26 | 26 |
| 2 | **`pag`** | `bnac install --profile pag` | PRD authoring + 89-rule verification across the 22-section schema (Product Activation Group) | +3 | +4 | +3 |
| 3 | **`react`** | `bnac install --profile react` | React+TS consumer profile with BusinessNext design system, 8-file pattern. 6 agents: developer (also hooks via `react-hook-patterns` skill), code-verifier (3-lens: `code`/`rtl`/`compliance`), unit-test-developer, wcag-checker (standalone — a11y depth), pr-approver, doc-writer. 20 skills (trimmed 2026-05-23): 3 `use-design-*` (consumer DS usage — `use-design-system` umbrella, `use-design-tokens`, `use-css-utilities`) + 5 `react-component-*` (scaffolding tiers) + 11 generic `react-*` + 1 `react-system-compliance`. DS-authoring skills and project-specific consumer-DS skills (theme provider wiring, dashlet composition, widget catalog, shared-folder, component-registration) moved to project-local install inside `<project>/.claude/skills/` or `base-ui/.claude/skills/`. | +6 | +20 | +8 |
| 4 | **`dotnet`** | `bnac install --profile dotnet` | .NET backend (developer/migrator/verifier/test/security/compliance/PR/doc) | +8 | +10 | +8 |
| 5 | **`python`** | `bnac install --profile python` | Python backend / scripting (full role set) | +8 | +10 | +8 |
| 6 | **`flutter`** | `bnac install --profile flutter` | Flutter / Dart mobile (full role set + a11y + RTL) | +9 | +10 | +9 |

The `core` baseline is always installed by every profile. Counts marked `+N` are the profile's contribution on top of `core`. The legacy `bnac` profile flag still resolves (alias of `core`) for backward compatibility.

Composite profiles available: `fullstack` (react+dotnet), `fullstack-mobile` (react+dotnet+flutter), `enterprise` (everything).

For full per-profile catalogs, see [AGENTS.md](AGENTS.md), [COMMANDS.md](COMMANDS.md), [SKILLS.md](SKILLS.md), [RULES.md](RULES.md).

---

## Common Commands (Quick Reference)

| Need | Command |
|------|---------|
| **Cross-stack** | |
| Fix build/type/lint errors | `/bnac-build-fix [path]` |
| Review code | `/bnac-code-review [path]` |
| Run quality gate | `/bnac-quality-gate [path]` |
| Develop a feature | `/bnac-feature-dev <desc> [path]` |
| Init project context | `/bnac-init [name]` (add `--minimal` for prototype, `--root` to also write a root CLAUDE.md) |
| Update project docs | `/bnac-update-docs` |
| **Planning (`core` baseline)** | |
| Plan whole project from PRD | `/bnac-plan <prd-folder>` |
| Plan phases / milestones / tasks | `/bnac-phase-plan` / `/bnac-milestone-plan` / `/bnac-task-plan` |
| Update changelog / status | `/bnac-changelog` / `/bnac-status-update` |
| **Milestone lifecycle** | |
| Start / status / complete | `/bnac-milestone start <M#>` / `/bnac-milestone status` / `/bnac-milestone complete` |
| **Phase lifecycle (`core` baseline)** | |
| Roll-up / status | `/bnac-phase complete <folder>` / `/bnac-phase status` |
| **Context & Memory (`core` baseline)** | |
| Typed memory | `/bnac-memory <add\|list\|forget\|search> [args]` |
| Carry-forward control | `/bnac-context <refresh\|show\|load\|check-stale> [target]` |
| **Pipeline governance (`core` baseline; closes Dark Factory gaps #2 / #7 / #8 / #9)** | |
| 8-stage state machine | `/bnac-pipeline-stage <status\|init\|advance <target>\|rollback <prev>\|freeze\|abort <reason>>` |
| Stakeholder GO / NO-GO | `/bnac-go-nogo <request <tier>\|approve <role> <decision>\|status\|rotate>` |
| Cross-LLM consensus | `/bnac-cross-llm-review <artifact> --gate <gate-name>` |
| Runtime KPI tracker | `/bnac-kpi <register <prd-folder>\|collect <id> <value>\|report>` |
| **PRD (`pag` profile)** | |
| Author / verify / break into features | `/bnac-pag-write` / `/bnac-pag-verify` / `/bnac-pag-feature-plan` |
| **React (`react` profile)** | |
| Scaffold / review / test component | `/bnac-react-scaffold <Name>` / `/bnac-react-review <Name>` / `/bnac-react-test <Name>` |
| WCAG / RTL / compliance | `/bnac-react-wcag-check` / `/bnac-react-rtl-check` / `/bnac-react-compliance-check` |
| **.NET (`dotnet` profile)** | |
| Develop / migrate / test / verify | `/bnac-dotnet-feature-dev` / `/bnac-dotnet-migrate` / `/bnac-dotnet-test` / `/bnac-dotnet-verify` |
| Security / compliance / PR | `/bnac-dotnet-security-check` / `/bnac-dotnet-compliance-check` / `/bnac-dotnet-pr-approve` |
| **Python (`python` profile)** | |
| Develop / migrate / test / verify | `/bnac-python-feature-dev` / `/bnac-python-migrate` / `/bnac-python-test` / `/bnac-python-verify` |
| Security / compliance / PR | `/bnac-python-security-check` / `/bnac-python-compliance-check` / `/bnac-python-pr-approve` |
| **Flutter (`flutter` profile)** | |
| Develop / migrate / test / verify | `/bnac-flutter-feature-dev` / `/bnac-flutter-migrate` / `/bnac-flutter-test` / `/bnac-flutter-verify` |
| A11y / RTL / compliance / PR | `/bnac-flutter-a11y-check` / `/bnac-flutter-rtl-check` / `/bnac-flutter-compliance-check` / `/bnac-flutter-pr-approve` |
| **Meta-creators (`core` baseline)** | |
| Author new agent / skill / command | `/bnac-agent-create` / `/bnac-skill-create` / `/bnac-command-create` |
| Scaffold a wired bundle (agent + skill + command, optionally + rule) | `/bnac-bundle-create <agent-slug> [folder] [purpose] [--with-rule]` |

For the full command list with descriptions and usage examples, see [COMMANDS.md](COMMANDS.md).

---

## Activity Logging

Every action you take must be logged to `project/.claude/log.md`:
- Command executed
- Context files read
- Files created/modified
- Milestone progress
- Quality gate results
