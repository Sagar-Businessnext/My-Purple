# Agent Catalog — 54 Specialist Agents

> Each agent is a specialist. They do ONE thing well. Do not ask an agent to do another agent's job.
> Auto-delegation: When a task matches an agent's specialty, delegate to that agent proactively.
> Every agent name starts with its profile prefix (`bnac-`, `pag-`, `react-`, `dotnet-`, `python-`, `flutter-`).

| Profile | Agents | Folder |
|---------|--------|--------|
| Cross-stack `core` baseline (execution + planning + meta-creators + context+memory + pipeline governance) | 20 | `core/agents/` |
| `pag` profile (PRD authoring + verification) | 3 | `stacks/pag/agents/` |
| `react` profile (incl. HTML/CSS/SCSS authoring — `ui` profile merged in 2026-05-11; migrator/rtl/compliance collapsed 2026-05-11) | 6 | `stacks/react-ts/agents/` |
| `dotnet` profile | 8 | `stacks/dotnet/agents/` |
| `python` profile | 8 | `stacks/python/agents/` |
| `flutter` profile | 9 | `stacks/flutter/agents/` |
| **Total** | **54** | |

Convention: writers (developer / migrator / test-developer / doc-writer) run on **opus**; read-only checkers (verifier / security / WCAG / RTL / compliance / PR-approver) run on **sonnet** for cost efficiency.

---

## Cross-stack execution (`core` baseline) — 4 agents

Stack-agnostic agents that ship with every profile. All `bnac-*` prefixed.

| Agent | Specialty | Tools | Invoked By | Model |
|-------|-----------|-------|------------|-------|
| **bnac-developer** | Write code, implement features, fix builds | Read, Write, Edit, Glob, Grep, Bash | `/bnac-build-fix`, `/bnac-feature-dev`, `/bnac-pipeline-run-all`, `/bnac-update-docs` | sonnet |
| **bnac-milestone-tracker** | Track milestones — activate, report status, complete, archive | Read, Edit, Glob, Grep | `/bnac-milestone start`, `/bnac-milestone status`, `/bnac-milestone complete` | sonnet |
| **bnac-reviewer** | Review code, find issues | Read, Glob, Grep, Bash (git only) | `/bnac-code-review` | opus |
| **bnac-quality-gate** | Run quality checks, report results | Read, Glob, Bash (build/test only) | `/bnac-quality-gate` | sonnet |

**Workflow:** `planner(s) → bnac-developer → bnac-reviewer → bnac-quality-gate`

For docs / test cases / automation / feature plans: invoke `bnac-task-planner` via the unified `/bnac-task-plan --lens doc|testcase|automation|feature` — it switches lens via the corresponding planning skill (`docs-planning`, `testcase-planning`, `automation-planning`, `feature-planning`). For milestones: `bnac-milestone-tracker` activates/tracks (`/bnac-milestone start|status|complete`), `bnac-milestone-planner` defines them.

---

## `core` baseline — planning hierarchy + meta-creators + context+memory (12 of the 20 agents)

Project-management roles that operate above any single tech stack. Located in `core/agents/` alongside the execution agents (since they ship as part of the baseline `core` install).

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **bnac-planner** | Top-level orchestrator — takes a scope (PRD) and decides phase / milestone / task decomposition | `/bnac-plan` | opus |
| **bnac-phase-planner** | Breaks the project into phases (A, B, C, …) each with a clear exit criterion; emits phase roll-up readiness hint when all milestones Approved | `/bnac-phase-plan`, `/bnac-phase status` | opus |
| **bnac-milestone-planner** | Breaks a phase into milestones (M1, M2, …) with tasks and acceptance tests | `/bnac-milestone-plan` | opus |
| **bnac-task-planner** | Breaks a milestone into individual tasks; also produces feature / test case / automation / docs plans (lens-switched via skill) | `/bnac-task-plan` (default lens or `--lens feature|testcase|automation|doc`) | opus |
| **bnac-changelog-agent** | Maintains `CHANGELOG.md` in keep-a-changelog format after every feature/milestone | `/bnac-changelog` | sonnet |
| **bnac-status-update-agent** | Generates status updates (done / in-progress / blockers / ETA) from activity log + git history | `/bnac-status-update` | sonnet |
| **bnac-agent-creator** | Authors new agent `.md` files with proper frontmatter, tools, and body structure | `/bnac-agent-create` | opus |
| **bnac-skill-creator** | Authors new skill folders (`SKILL.md` + `reference/`) following BNAC skill conventions | `/bnac-skill-create` | opus |
| **bnac-command-creator** | Authors new slash-command `.md` files, wiring command → agent → skill | `/bnac-command-create` | opus |
| **bnac-bundle-creator** | Meta-orchestrator — scaffolds a wired project-local bundle (1 agent + 1 skill + 1 command, optionally + 1 rule) in one pass | `/bnac-bundle-create` | opus |
| **bnac-memory-curator** | Manages the typed long-term memory store (`project/.claude/memory/`) — add/list/forget/search across 4 types (user/feedback/project/reference), maintains `MEMORY.md` index, prunes stale entries | `/bnac-memory` | sonnet |
| **bnac-context-compactor** | Writes compact `*.summary.md` files (milestone ≤ 500 tokens, phase ≤ 1500 tokens), rebuilds `carry-forward.md`, runs `check-stale` drift detection via git mtime — invoked on milestone/phase complete and via `/bnac-context` | `/bnac-context`, `/bnac-milestone complete`, `/bnac-phase complete` | opus |

**Note:** `bnac-milestone-planner` *defines* milestones from scope; `bnac-milestone-tracker` (in `core` baseline) *manages* their lifecycle (start / status / complete). Distinct concerns, distinct agents.

**Context+memory split (Phase CMM):** `bnac-memory-curator` owns curated user/project *facts* under `memory/`; `bnac-context-compactor` owns auto-generated work-product *history* under `context/`. Different lifetimes, different writers — see `memory-management.md` rule.

---

## `core` baseline — pipeline governance (4 of the 20 agents)

Added 2026-05-22 to close gaps #2, #7, #8, #9 from [v2-vs-v3-comparison.md](../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8. These four agents enforce the BN AI Dark Factory contract end-to-end: formal stage state machine, cross-LLM consensus on critical gates, stakeholder GO / NO-GO, and runtime KPI evidence.

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **bnac-pipeline-state-tracker** | Formal 8-stage pipeline state machine — enforces explicit state, transitions, guards, and an auditable history on the BN AI Dark Factory pipeline | `/bnac-pipeline-stage` | sonnet |
| **bnac-go-nogo-approver** | Stakeholder GO / NO-GO release approval orchestrator — sits on top of `bnac-quality-gate` to require human sign-off before production | `/bnac-go-nogo` | sonnet |
| **bnac-cross-llm-reviewer** | Cross-LLM consensus reviewer — runs critical artifacts through two distinct models and classifies findings AGREE / PARTIAL / DISAGREE | `/bnac-cross-llm-review` | opus |
| **bnac-kpi-tracker** | Runtime KPI tracker — closes the loop from PRD §16 KPIs to production evidence (registry + observations + cycle reports) | `/bnac-kpi` | sonnet |

**Composition:** `bnac-go-nogo-approver` writes `release-approval.md`, which is the entry guard on `bnac-pipeline-state-tracker` T07. `bnac-kpi-tracker` writes the `cycle-N-complete` flag, which is the entry guard on T09. `bnac-cross-llm-reviewer` is optional wiring on T04 / T07 entry guards. The four agents compose into a fully closed pipeline.

---

## `pag` profile — 3 agents (PRD authoring + verification)

Product Activation Group: business requirements and PRD discipline. Located in `stacks/pag/agents/`.

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **pag-doc-writer** | Authors PRDs walking the 22-section template (problem, goals, users, scope, ACs, NFRs, sample scenarios, state machines, failure modes, AI guardrails, observability, deployment, code-gen context, …) | `/bnac-pag-write` | opus |
| **pag-doc-verifier** | Validates a PRD against 89 rules: 44 critical + 31 warning + 14 cross-reference (CR-001/CR-002/CR-011/CR-012/CR-013 are critical) | `/bnac-pag-verify` | opus |
| **pag-feature-planner** | Breaks an approved PRD into per-stack features with stack assignment + priority | `/bnac-pag-feature-plan` | opus |

---

## `react` profile — 6 agents (React + TypeScript + BNDS, HTML/CSS/SCSS authoring included)

Located in `stacks/react-ts/agents/`. All `react-*` prefixed. Absorbs former `ui` profile's HTML/CSS/SCSS authoring scope (merged 2026-05-11).

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **react-developer** | Builds React+TS components/pages using BNDS (8-file pattern), authors custom hooks (via `react-hook-patterns` skill) | `/bnac-react-scaffold`, `/bnac-feature-dev` | opus |
| **react-code-verifier** | Three-lens verifier: `code` (8-file pattern, hooks, types, tests), `rtl` (logical CSS, directional icons), `compliance` (COMP-* rules) | `/bnac-react-review`, `/bnac-react-rtl-check`, `/bnac-react-compliance-check` | sonnet |
| **react-unit-test-developer** | Authors Jest + React Testing Library tests in the split pattern (util / hook / UI) | `/bnac-react-test` | opus |
| **react-wcag-checker** | WCAG 2.2 AA audits for React components (standalone — a11y depth doesn't fit a lens) | `/bnac-react-wcag-check` | sonnet |
| **react-pr-approver** | Final merge-gate sign-off, aggregating verdicts across all lenses + WCAG + quality gate | `/bnac-react-pr-approve` | sonnet |
| **react-doc-writer** | README, JSDoc, Storybook authoring | `/bnac-react-doc-write` | opus |

**Key capabilities of react-developer:** 8-file pattern (types → util → hooks → tsx → scss → test → stories → index), import boundary enforcement, BNDS components only (no raw HTML), design tokens (`var(--bnds-g-*)`), utility-first (`bd-*` classes).

---

## `dotnet` profile — 8 agents

.NET backend (Clean Architecture, ADO.NET, EF Core, OWASP). Located in `stacks/dotnet/agents/`.

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **dotnet-developer** | Writes .NET features (services, repositories, controllers) | `/bnac-dotnet-feature-dev` | opus |
| **dotnet-migrator** | Migrates legacy .NET to current patterns | `/bnac-dotnet-migrate` | opus |
| **dotnet-code-verifier** | Reviews .NET code for patterns, structure, types | `/bnac-dotnet-verify` | sonnet |
| **dotnet-unit-test-developer** | Authors xUnit/NUnit tests | `/bnac-dotnet-test` | opus |
| **dotnet-security-checker** | OWASP Top 10 audits, parameterized queries, auth checks | `/bnac-dotnet-security-check` | sonnet |
| **dotnet-compliance-checker** | BusinessNext-specific compliance (naming, structure, imports) | `/bnac-dotnet-compliance-check` | sonnet |
| **dotnet-pr-approver** | Final merge-gate sign-off | `/bnac-dotnet-pr-approve` | sonnet |
| **dotnet-doc-writer** | XML docs, README authoring | `/bnac-dotnet-doc-write` | opus |

---

## `python` profile — 8 agents

Python backend / scripting (typing, pytest, OWASP, bandit). Located in `stacks/python/agents/`.

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **python-developer** | Writes Python features following project structure | `/bnac-python-feature-dev` | opus |
| **python-migrator** | Migrates legacy Python (e.g. Python 2 → 3, untyped → typed) | `/bnac-python-migrate` | opus |
| **python-code-verifier** | Reviews Python code for PEP 8, typing, structure | `/bnac-python-verify` | sonnet |
| **python-unit-test-developer** | Authors pytest tests | `/bnac-python-test` | opus |
| **python-security-checker** | OWASP + bandit audits | `/bnac-python-security-check` | sonnet |
| **python-compliance-checker** | BusinessNext-specific compliance | `/bnac-python-compliance-check` | sonnet |
| **python-pr-approver** | Final merge-gate sign-off | `/bnac-python-pr-approve` | sonnet |
| **python-doc-writer** | Docstrings, README authoring | `/bnac-python-doc-write` | opus |

---

## `flutter` profile — 9 agents

Flutter / Dart mobile (widgets, state, navigation, mobile a11y, RTL). Located in `stacks/flutter/agents/`. Has 9 agents (vs 8 for other stacks) because mobile a11y is a distinct concern from compliance and gets its own checker.

| Agent | Specialty | Invoked By | Model |
|-------|-----------|-----------|-------|
| **flutter-developer** | Builds Flutter widgets, screens, state management | `/bnac-flutter-feature-dev` | opus |
| **flutter-migrator** | Migrates legacy Flutter / older Dart patterns | `/bnac-flutter-migrate` | opus |
| **flutter-code-verifier** | Reviews Flutter/Dart code for structure, types | `/bnac-flutter-verify` | sonnet |
| **flutter-unit-test-developer** | Authors `flutter_test` widget + unit tests | `/bnac-flutter-test` | opus |
| **flutter-a11y-checker** | Mobile accessibility audits (Semantics, screen reader, touch targets) | `/bnac-flutter-a11y-check` | sonnet |
| **flutter-rtl-checker** | RTL layout verification | `/bnac-flutter-rtl-check` | sonnet |
| **flutter-compliance-checker** | BusinessNext-specific compliance | `/bnac-flutter-compliance-check` | sonnet |
| **flutter-pr-approver** | Final merge-gate sign-off | `/bnac-flutter-pr-approve` | sonnet |
| **flutter-doc-writer** | Dart docstrings, README authoring | `/bnac-flutter-doc-write` | opus |

---

## Agent Workflow

For a typical feature flowing through any code-authoring stack:

```
pag-* (requirements)  →  bnac-* (planning)  →  <stack>-developer  →  <stack>-code-verifier
                                                                  →  <stack>-unit-test-developer
                                                                  →  <stack>-security-checker / wcag / rtl / compliance
                                                                  →  <stack>-pr-approver  →  bnac-quality-gate
```

For documentation: `bnac-task-planner` (docs-planning lens, via `/bnac-task-plan --lens doc`) plans → `<stack>-doc-writer` writes.
For PRD work: `pag-doc-writer` authors → `pag-doc-verifier` validates → `pag-feature-planner` breaks down.
For new BNAC content: `bnac-agent-creator` / `bnac-skill-creator` / `bnac-command-creator` author it.
