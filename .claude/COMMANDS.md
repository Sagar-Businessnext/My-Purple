# Command Reference — 63 Commands

> **Location:** `~/.claude/commands/` (global) and `project/.claude/commands/` (project-local overrides)
> Every command starts with `/bnac-` so BNAC tooling is instantly recognizable. Each command delegates to a single agent — see [AGENTS.md](AGENTS.md) for the agent → tool mapping.

| Profile | Commands | Folder |
|---------|----------|--------|
| Cross-stack `core` baseline (execution + planning + meta-creators + context+memory + pipeline governance) | 26 | `core/commands/` |
| `pag` profile (PRD authoring + verification) | 3 | `stacks/pag/commands/` |
| `react` profile (HTML/CSS/SCSS authoring folded in 2026-05-11) | 9 | `stacks/react-ts/commands/` |
| `dotnet` profile | 8 | `stacks/dotnet/commands/` |
| `python` profile | 8 | `stacks/python/commands/` |
| `flutter` profile | 9 | `stacks/flutter/commands/` |
| **Total** | **63** | |

---

## Cross-stack execution (`core` baseline — execution subset) — 9 commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-build-fix [path]` | `bnac-developer` | Diagnose and fix build/type/lint errors |
| `/bnac-code-review [path]` | `bnac-reviewer` | Review code against standards |
| `/bnac-feature-dev <desc> [path]` | `bnac-developer` | End-to-end feature development |
| `/bnac-quality-gate [path]` | `bnac-quality-gate` | Run full verification (build + type + lint + test) |
| `/bnac-init [name] [--minimal] [--root]` | — | Initialize project context. Default writes the `.claude/` bundle; `--minimal` skips `SUMMARY.md`; `--root` also writes a root `CLAUDE.md`. (Replaces `init-project-local`, `quick-project`, `init-claude-md`.) |
| `/bnac-milestone <start\|status\|complete> [M#]` | `bnac-milestone-tracker` | Milestone lifecycle. `start <M#>` activates, `status [M#]` reports progress, `complete [M#]` archives and advances. (Replaces `milestone-start`, `milestone-status`, `milestone-complete`.) |
| `/bnac-update-docs [path]` | `bnac-developer` | Update project context docs after changes |
| `/bnac-pipeline-run-all [prd-folder]` | `bnac-developer` | Run full PRD→project pipeline |
| `/bnac-undo [target]` | `bnac-developer` | Reverse the last generation, install, or commit safely |

---

## `core` baseline — planning hierarchy + meta-creators (10 of the 26 commands)

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-plan <prd-folder>` | `bnac-planner` | Top-level project orchestration — emits phase / milestone / task tree |
| `/bnac-phase-plan <scope>` | `bnac-phase-planner` | Break project into phases with exit criteria |
| `/bnac-milestone-plan <phase>` | `bnac-milestone-planner` | Break a phase into milestones with tasks and acceptance tests |
| `/bnac-task-plan <milestone> [--scope ...] [--lens feature\|testcase\|automation\|doc]` | `bnac-task-planner` | Break a milestone into atomic tasks. `--scope` subsets task types; `--lens` swaps the output template (replaces the legacy `/bnac-plan-feature\|testcase\|automation\|docs`). |
| `/bnac-changelog [version]` | `bnac-changelog-agent` | Update `CHANGELOG.md` (keep-a-changelog format) |
| `/bnac-status-update [period]` | `bnac-status-update-agent` | Generate status update from log + git history |
| `/bnac-agent-create <slug>` | `bnac-agent-creator` | Author a new agent `.md` file with proper frontmatter |
| `/bnac-skill-create <slug>` | `bnac-skill-creator` | Author a new skill folder (`SKILL.md` + `reference/`) |
| `/bnac-command-create <slug>` | `bnac-command-creator` | Author a new command file wiring command → agent → skill |
| `/bnac-bundle-create <agent-slug> [folder] [purpose] [--with-rule]` | `bnac-bundle-creator` | Scaffold a wired project-local bundle in one pass: 1 agent + 1 skill + 1 command (+ 1 rule with flag). Project-local only — never writes to BNAC source. |

---

## `core` baseline — context + memory (3 commands; Phase CMM 2026-05-21)

Typed long-term memory store and hierarchical phase/milestone compaction. See [how-to-use-context-and-memory](../../GetStarted/how-to-use-context-and-memory.md) for the full walkthrough.

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-memory <add\|list\|forget\|search> [args]` | `bnac-memory-curator` | Manage typed long-term memory (4 types: `user` / `feedback` / `project` / `reference`). `add <type> "<body>"` writes one entry, `list [type] [--prune-stale]` lists/prunes, `forget <slug>` tombstones, `search <query>` finds by description. Maintains `project/.claude/memory/MEMORY.md` index. |
| `/bnac-phase <complete\|status> [folder]` | `bnac-context-compactor` (complete) / `bnac-phase-planner` (status) | Phase lifecycle. `complete <folder>` rolls up an entire phase into one `index.summary.md` (≤ 1500 tokens, built from milestone *details* per CMM-D4); `status [folder]` reports per-milestone breakdown. Pre-check refuses to roll up a phase with non-Approved milestones. |
| `/bnac-context <refresh\|show\|load\|check-stale> [target]` | `bnac-context-compactor` | Manual control of the carry-forward layer. `show` prints current `carry-forward.md`, `load` rebuilds it for the active milestone, `refresh [M#\|P#]` re-runs the compactor for one or all summaries, `check-stale` reports summaries whose listed artifacts have newer git mtime. Default action is `show` (read-only). |

---

## `core` baseline — pipeline governance (4 commands; added 2026-05-22 for gaps #2 / #7 / #8 / #9)

Closes the four BN AI Dark Factory gaps still open after Wave 1. See [dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md](../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-pipeline-stage <status\|init\|advance <target>\|rollback <prev>\|freeze [reason]\|unfreeze\|abort <reason>>` | `bnac-pipeline-state-tracker` | Formal 8-stage pipeline state machine. `advance` evaluates entry guards (VALIDATION_REPORT PROCEED, quality-gate PASS, release-approval GO, KPI cycle-complete) before allowing the move. (gap #2) |
| `/bnac-go-nogo <status\|request <tier>\|approve <role> <decision>\|reject <role> <reason>\|check-conditions\|rotate>` | `bnac-go-nogo-approver` | Stakeholder GO / NO-GO release approval. Records named approvers + decisions + evidence reviewed; writes `release-approval.md` which is the T07 entry guard. (gap #8) |
| `/bnac-cross-llm-review <artifact-path> --gate <gate-name> [--primary <model>] [--secondary <model>]` | `bnac-cross-llm-reviewer` | Run an artifact through two distinct models and classify findings AGREE / PARTIAL / DISAGREE; mechanical verdict PASS / PASS-WITH-CAVEAT / FAIL. Non-blocking by default; optional T04 / T07 entry guard. (gap #7) |
| `/bnac-kpi <register <prd-folder>\|list\|collect <kpi-id> <value>\|collect-auto <kpi-id>\|status <kpi-id>\|report\|verify>` | `bnac-kpi-tracker` | Runtime KPI tracker. `register` extracts PRD §16 into a live registry + per-KPI evidence files; `report` closes a review cycle and writes the `cycle-N-complete` flag (T09 entry guard). (gap #9) |

---

## `pag` profile — 3 commands (PRD authoring + verification)

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-pag-write <topic>` | `pag-doc-writer` | Walk the 22-section PRD template |
| `/bnac-pag-verify <prd-folder>` | `pag-doc-verifier` | Validate PRD against 89 rules (44 critical + 31 warning + 14 cross-ref) |
| `/bnac-pag-feature-plan <prd-folder>` | `pag-feature-planner` | Break approved PRD into per-stack features with priority |

---

## `react` profile — 8 commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-react-scaffold <Name>` | `react-developer` | Scaffold a React component (8-file pattern, BNDS) |
| `/bnac-react-review <Name>` | `react-code-verifier --lens code` | Review for separation pattern + DS compliance |
| `/bnac-react-test <Name>` | `react-unit-test-developer` | Author Jest + RTL tests in split pattern |
| `/bnac-react-wcag-check <path>` | `react-wcag-checker` | WCAG 2.2 AA audit |
| `/bnac-react-rtl-check <path>` | `react-code-verifier --lens rtl` | RTL rendering verification |
| `/bnac-react-compliance-check <path>` | `react-code-verifier --lens compliance` | BusinessNext-specific compliance |
| `/bnac-react-pr-approve <pr>` | `react-pr-approver` | Final merge-gate sign-off |
| `/bnac-react-doc-write <Name>` | `react-doc-writer` | README + JSDoc + Storybook |

---

## `dotnet` profile — 8 commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-dotnet-feature-dev <desc> [path]` | `dotnet-developer` | Develop a .NET feature (services / repos / controllers) |
| `/bnac-dotnet-migrate <path>` | `dotnet-migrator` | Migrate legacy .NET to current patterns |
| `/bnac-dotnet-verify <path>` | `dotnet-code-verifier` | Review .NET code for patterns, structure, types |
| `/bnac-dotnet-test <path>` | `dotnet-unit-test-developer` | Author xUnit / NUnit tests |
| `/bnac-dotnet-security-check <path>` | `dotnet-security-checker` | OWASP Top 10 audit, parameterized queries |
| `/bnac-dotnet-compliance-check <path>` | `dotnet-compliance-checker` | BusinessNext-specific compliance |
| `/bnac-dotnet-pr-approve <pr>` | `dotnet-pr-approver` | Final merge-gate sign-off |
| `/bnac-dotnet-doc-write <path>` | `dotnet-doc-writer` | XML docs + README |

---

## `python` profile — 8 commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-python-feature-dev <desc> [path]` | `python-developer` | Develop a Python feature |
| `/bnac-python-migrate <path>` | `python-migrator` | Migrate legacy Python (typing, structure) |
| `/bnac-python-verify <path>` | `python-code-verifier` | PEP 8 + typing + structure review |
| `/bnac-python-test <path>` | `python-unit-test-developer` | Author pytest tests |
| `/bnac-python-security-check <path>` | `python-security-checker` | OWASP + bandit audit |
| `/bnac-python-compliance-check <path>` | `python-compliance-checker` | BusinessNext-specific compliance |
| `/bnac-python-pr-approve <pr>` | `python-pr-approver` | Final merge-gate sign-off |
| `/bnac-python-doc-write <path>` | `python-doc-writer` | Docstrings + README |

---

## `flutter` profile — 9 commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/bnac-flutter-feature-dev <desc> [path]` | `flutter-developer` | Build Flutter widgets / screens / state |
| `/bnac-flutter-migrate <path>` | `flutter-migrator` | Migrate legacy Flutter / Dart |
| `/bnac-flutter-verify <path>` | `flutter-code-verifier` | Review Flutter/Dart structure, types |
| `/bnac-flutter-test <path>` | `flutter-unit-test-developer` | Author `flutter_test` widget + unit tests |
| `/bnac-flutter-a11y-check <path>` | `flutter-a11y-checker` | Mobile accessibility audit (Semantics, touch targets) |
| `/bnac-flutter-rtl-check <path>` | `flutter-rtl-checker` | RTL layout verification |
| `/bnac-flutter-compliance-check <path>` | `flutter-compliance-checker` | BusinessNext-specific compliance |
| `/bnac-flutter-pr-approve <pr>` | `flutter-pr-approver` | Final merge-gate sign-off |
| `/bnac-flutter-doc-write <path>` | `flutter-doc-writer` | Dart docstrings + README |

---

## Conventions

- All commands accept an optional file or folder path to scope the work.
- Commands delegate to their assigned agent — see [AGENTS.md](AGENTS.md) for tools and skills.
- Composite profiles (`fullstack`, `fullstack-mobile`, `enterprise`) install commands from all included stacks.
- Project-local commands in `project/.claude/commands/` override globals with the same name.

## Naming patterns for `plan` commands

The planning hierarchy is four commands, one per level. Output shape is then switched inside `/bnac-task-plan` via `--lens`.

| Command | Role | Notes |
|---------|------|-------|
| `/bnac-plan` | Top-level orchestration | Scaffolds `.claude/phases/` skeleton |
| `/bnac-phase-plan` | Phase enrichment | Goals + exit criteria per phase |
| `/bnac-milestone-plan` | Milestone definition | Writes `m<N>-*.md` files inside each phase |
| `/bnac-task-plan` | Task decomposition + lens switch | `--lens feature\|testcase\|automation\|doc` swaps the output template; default is the standard atomic-task checklist |

`/bnac-task-plan` runs the **same** agent (`bnac-task-planner`) regardless of lens — the lens skill (`feature-planning`, `testcase-planning`, `automation-planning`, `docs-planning`) supplies the output template. Pre-2026-05 versions exposed four separate commands (`/bnac-plan-feature|testcase|automation|docs`); those have been collapsed into the `--lens` flag.

## Future commands

- **M16:** Multi-harness adapter commands (Codex / Cursor / Augment).
- **M17:** `bnac quickstart`, `/quick-project` (lite-tier entry points).
- **M21:** `bnac metrics`, `bnac cost` (telemetry + cost tracking).
