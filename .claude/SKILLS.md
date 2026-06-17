# Skill Catalog — 80 Skills

> **Structure:** Each skill is a directory with `SKILL.md` (instructions) and optional `reference/` files (templates, examples).
> **Location:** `~/.claude/skills/` (global) and `project/.claude/skills/` (project-local overrides).
> Skills are loaded by agents on-demand. See [AGENTS.md](AGENTS.md) for which agent uses which skill.

| Profile | Skills | Folder |
|---------|--------|--------|
| Cross-stack `core` baseline (execution + planning + meta-creators + context+memory + pipeline governance) | 26 | `core/skills/` |
| `pag` profile (PRD authoring + verification) | 4 | `stacks/pag/skills/` |
| `react` profile (consumer-side; trimmed 2026-05-23) | 20 | `stacks/react-ts/skills/` |
| `dotnet` profile | 10 | `stacks/dotnet/skills/` |
| `python` profile | 10 | `stacks/python/skills/` |
| `flutter` profile | 10 | `stacks/flutter/skills/` |
| **Total** | **80** | |

---

## Cross-stack execution (`core` baseline) — 5 skills

| Skill | Description | Used By |
|-------|------------|---------|
| **code-review** | Structured code review with severity-classified findings table | `bnac-reviewer` |
| **build-fix** | Iterative build error diagnosis and resolution | `bnac-developer` |
| **verification-loop** | Build → type → lint → test verification cycle | `bnac-quality-gate`, `bnac-developer` |
| **git-workflow** | Conventional commits, branching strategy, PR workflow | All write-capable agents |
| **milestone-management** | Milestone planning, tracking, and completion lifecycle | `bnac-milestone-tracker`, `bnac-milestone-planner` |

---

## `core` baseline — planning hierarchy + meta-creators (13 of the 26 skills)

Located in `core/skills/` alongside the execution skills.

| Skill | Description | Used By |
|-------|------------|---------|
| **project-planning** | High-level scope-to-plan decomposition patterns | `bnac-planner` |
| **phase-template** | Phase structure — name, goal, exit criterion | `bnac-phase-planner` |
| **milestone-template** | Milestone structure — tasks, dependencies, DoD | `bnac-milestone-planner` |
| **task-estimation** | Task breakdown with deps and rough estimates | `bnac-task-planner` |
| **feature-planning** | Lens output for feature plans (goal, architecture, risks, atomic tasks) | `bnac-task-planner --lens feature` |
| **testcase-planning** | Lens output for test case plans (scenarios, expected results, priority) | `bnac-task-planner --lens testcase` |
| **automation-planning** | Lens output for test automation plans (framework, CI, implementation tasks) | `bnac-task-planner --lens automation` |
| **docs-planning** | Lens output for documentation plans (audience, inventory, content outline) | `bnac-task-planner --lens doc` |
| **changelog-conventions** | Keep-a-changelog format and update patterns | `bnac-changelog-agent` |
| **status-report-template** | Status update structure (done / in-progress / blockers / ETA) | `bnac-status-update-agent` |
| **agent-authoring-template** | Frontmatter + body structure for new agents | `bnac-agent-creator` |
| **skill-authoring-template** | `SKILL.md` format + reference-file conventions | `bnac-skill-creator` |
| **command-authoring-template** | Command file format and command → agent → skill wiring | `bnac-command-creator` |

Each skill ships as `SKILL.md` + 1–2 reference files.

---

## `core` baseline — pipeline governance (4 skills; added 2026-05-22 for gaps #2 / #7 / #8 / #9)

Added to close gaps #2, #7, #8, #9 from [v2-vs-v3-comparison.md](../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

| Skill | Description | Used By |
|-------|------------|---------|
| **pipeline-stage-machine** | Formal 8-stage state machine for the BN AI Dark Factory pipeline — states, transitions, guards, terminal states, and the on-disk current-state file format (gap #2) | `bnac-pipeline-state-tracker` |
| **release-approval** | Stakeholder GO / NO-GO release approval protocol — release tiers, approver matrix, evidence requirements, on-disk record format (gap #8) | `bnac-go-nogo-approver` |
| **cross-llm-consensus** | Consensus-of-two-models review protocol — pairwise match, AGREE / PARTIAL / DISAGREE classification, mechanical verdict (PASS / PASS-WITH-CAVEAT / FAIL) (gap #7) | `bnac-cross-llm-reviewer` |
| **kpi-evidence-collection** | Runtime KPI evidence protocol — registry + observations + cycle reports + the `cycle-N-complete` flag that gates pipeline T09 (gap #9) | `bnac-kpi-tracker` |

---

## `core` baseline — context + memory (4 skills; Phase CMM 2026-05-21)

| Skill | Description | Used By |
|-------|------------|---------|
| **memory-conventions** | Contract for the typed memory store under `project/.claude/memory/` — 4 types (user/feedback/project/reference), frontmatter shape, slug ↔ filename equality, `MEMORY.md` index format, body structure (Why + How to apply for feedback/project) | `bnac-memory-curator` |
| **compact-milestone-template** | Strict ≤ 500-token milestone summary template (Goal, Key decisions w/ Why, Artifacts as paths-only, Public surface as signatures-only, Gotchas ≤ 3 lines) + over-budget retry protocol | `bnac-context-compactor` (milestone mode) |
| **compact-phase-template** | Strict ≤ 1500-token phase summary template (Goal, Milestones rollup, Architecture decisions w/ Why, Public surface, Carried-forward debt) — built from milestone *details* per CMM-D4, never from summary-of-summaries | `bnac-context-compactor` (phase mode) |
| **context-carry-forward** | Stitching algorithm for `carry-forward.md` (≤ 5000 tokens total) — phase-vs-milestone strategy decision, active-milestone-as-pointer rule, drift-warning surfacing, idempotent strip-and-regenerate | `bnac-context-compactor` (stitch-only + check-stale) |

---

## `pag` profile — 4 skills (PRD authoring + verification)

| Skill | Description | Used By |
|-------|------------|---------|
| **pag-template** | 22-section PRD template with prompts per section (covers enterprise context, sample scenarios, state machines, failure modes, AI guardrails, observability, deployment, code-gen context) | `pag-doc-writer` |
| **pag-critical-rules** | Index over the 44 critical validation rules in `pipeline/validation/critical-rules.md` | `pag-doc-verifier` |
| **pag-warning-rules** | Index over the 31 warning rules in `pipeline/validation/warning-rules.md` | `pag-doc-verifier` |
| **pag-cross-reference** | 14 cross-reference checks (CR-001 / CR-002 / CR-011 / CR-012 / CR-013 critical) with extraction procedure | `pag-doc-verifier` |

Skills wrap the existing `pipeline/validation/` content rather than duplicating it.

---

## `react` profile — 20 skills (trimmed 2026-05-23)

All skills prefixed with `react-`, `use-design-system`, `use-design-tokens`, or `use-css-utilities` to avoid collision in multi-stack installs. The DS reference for consumers is `use-design-system` (@app/base-ui / `window.crmnextUi`), backed by `use-design-tokens` (SCSS + styled-system token catalog) and `use-css-utilities` (production utility classes). DS-authoring skills (formerly `bn-design-system` / `bn-ds-*` / `bnds-compliance`) are removed from this profile — they now live as project-local skills inside the DS repo (`base-ui/.claude/skills/`). Theme provider wiring, dashlet composition, and per-widget catalogs are also intentionally consumer-project concerns and are not shipped here — author them as project-local skills if needed.

### Use design system family (3) — consumer side
| Skill | Description | Used By |
|-------|------------|---------|
| **use-design-system** | Consumer-side DS master — bundle load order, externals, crmnextUi alias, hard rules for consumers | `react-developer`, `react-code-verifier` |
| **use-design-tokens** | SCSS tokens (`$brand`, `$spacing-N`, `$font-N`) + runtime theme tokens (styled-system props) | `react-developer`, `react-code-verifier` |
| **use-css-utilities** | Production utility class catalog (`.ma3`, `.flex`, `.items-center`, `.dn-lg`) | `react-developer` |

### Component scaffolding (5) — app component structure
| Skill | Description | Used By |
|-------|------------|---------|
| **react-component-pattern** | Small/medium/large scaffolding tiers, separation rules, post-creation checklist | `react-developer`, `react-code-verifier`, `react-doc-writer`, `react-unit-test-developer` |
| **react-component-small** | Tier-1 leaf component scaffold | `react-developer` |
| **react-component-medium** | Tier-2 typed-state component scaffold | `react-developer` |
| **react-component-large** | Tier-3 Manager+Context+hook scaffold | `react-developer` |
| **react-component-complex** | Tier-4 component family scaffold | `react-developer` |

### Generic React (11)
| Skill | Description | Used By |
|-------|------------|---------|
| **react-hook-patterns** | Rules of Hooks, effect cleanup, memoization, `renderHook` testing | `react-developer` |
| **react-http-request** | Make HTTP calls through the shared HTTP helper | `react-developer` |
| **react-use-signalr** | Wire a component to a SignalR hub | `react-developer` |
| **react-jest-testing** | Jest patterns for util / hook unit tests | `react-unit-test-developer` |
| **react-testing-library** | RTL patterns for UI render tests | `react-unit-test-developer` |
| **react-write-tests** | Split test pattern (util + hook + UI separately) | `react-unit-test-developer` |
| **react-write-scss** | Custom SCSS with production tokens + mixins (`hover-focus`, `set-media-width`, `input-focus`) | `react-developer` |
| **react-code-review** | React-specific review checklist | `react-code-verifier` |
| **react-rte-review** | Ecosystem-wide JS/TS/React/CSS/SCSS hygiene checklist | `rte-reviewer` |
| **react-wcag-audit** | WCAG 2.2 AA audit procedure for React components | `react-wcag-checker` |
| **react-rtl-support** | Paired `-rtl.scss` files, directional icons, locale flips | `react-code-verifier --lens rtl` |

### Compliance (1)
| Skill | Description | Used By |
|-------|------------|---------|
| **react-system-compliance** | DS-only / tokens-only / COMP-* compliance rules for consumer code | `react-code-verifier --lens compliance`, `react-developer` |

---

## `dotnet` profile — 10 skills

| Skill | Description |
|-------|------------|
| **dotnet-project-structure** | Clean Architecture project layout |
| **dotnet-patterns** | Services, repositories, controllers, DI |
| **dotnet-code-review** | .NET-specific review checklist |
| **xunit-testing** | xUnit patterns and assertions |
| **nunit-testing** | NUnit patterns and assertions |
| **owasp-dotnet** | OWASP Top 10 in .NET context |
| **ado-connection-pooling** | ADO.NET connection pooling and parameterization |
| **ef-core-patterns** | Entity Framework Core patterns and pitfalls |
| **dotnet-xml-docs** | XML documentation conventions |
| **dotnet-readme-template** | README structure for .NET projects |

---

## `python` profile — 10 skills

| Skill | Description |
|-------|------------|
| **python-project-structure** | Layout for libraries, services, scripts |
| **python-patterns** | Idiomatic patterns (context managers, dataclasses, protocols) |
| **python-code-review** | Python-specific review checklist |
| **pytest-testing** | pytest patterns, fixtures, parametrization |
| **owasp-python** | OWASP Top 10 in Python context |
| **python-security-bandit** | Bandit static-analysis rules and remediation |
| **python-typing** | Type hints, generics, `typing` module |
| **pep8-style** | PEP 8 conformance, formatter wiring (black/ruff) |
| **python-docstrings** | Docstring conventions (Google / NumPy / reST) |
| **python-readme-template** | README structure for Python projects |

---

## `flutter` profile — 10 skills

| Skill | Description |
|-------|------------|
| **flutter-project-structure** | Standard Flutter app / package layout |
| **flutter-widgets** | Stateful / stateless / inherited widget patterns |
| **flutter-state-management** | BLoC / Provider / Riverpod patterns |
| **flutter-navigation** | Navigator 2.0, GoRouter |
| **flutter-testing** | Widget tests, integration tests, golden tests |
| **mobile-a11y** | Semantics widgets, screen reader, touch targets |
| **mobile-rtl** | Directional widgets, locale flipping |
| **flutter-compliance** | BusinessNext-specific compliance for Flutter |
| **dart-docstrings** | Dart documentation conventions |
| **flutter-readme-template** | README structure for Flutter projects |

---

## Conventions

- Each skill is a directory with `SKILL.md` + optional `reference/*.md`.
- Skills are stack-specific by default; cross-stack skills live in `core/skills/`.
- Project-local skills in `project/.claude/skills/` override globals with the same name.
- The `use-design-tokens` skill (React profile) is the authoritative BN token catalog. Token reference data lives in `reference/colors.md` and `reference/typography-spacing.md`.
