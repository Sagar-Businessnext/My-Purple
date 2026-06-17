Invoke the **bnac-task-planner** agent to **edit** each milestone's `m<N>-<slug>.md` file in place — filling the `## Tasks (todo list)` section with atomic `- [ ] M<N>.<i>` checkboxes (each carrying `@agent` attribution, files, S/M/L complexity, dependencies, optional steps) plus a final HUMAN REVIEW CHECKPOINT, and appending a `## Verification map` table linking every acceptance condition to the tasks that verify it. **No new files are created.**

**Agent:** `bnac-task-planner`
**Target:** `$ARGUMENTS` (milestone ID, milestone `.md` path, scope description, or PRD path; optional — auto-detects active milestone)
**Flags:**
- `--scope code[,test][,doc]` (optional; default `code`) — subsets which **task types** appear in the checklist.
- `--lens feature|testcase|automation|doc` (optional; default `default`) — switches the entire output template. Replaces the legacy `/bnac-plan-feature`, `/bnac-plan-testcase`, `/bnac-plan-automation`, `/bnac-plan-docs` commands.

**Output:** Edits in place — `.claude/phases/phase-<N>-<slug>/m<N>-<slug>.md`. No `tasks/` folder, no per-task files.

> **Path convention.** Every `.claude/...` path below is **relative to the current working directory** — the folder you ran `/bnac-task-plan` from. The planner agent must edit files directly under `<cwd>/.claude/`. **Never create a literal `project/` folder** — if you see `project/.claude/...` anywhere on disk, that's a bug. Distinct from `~/.claude/` (your home-directory global BNAC content).

## What to do

1. Parse `--scope` from `$ARGUMENTS` if present. Accepted values: `code`, `test`, `doc` (comma-separated, any order). If absent → default to `code`. Pass the resolved scope set to the agent.

2. Parse `--lens` from `$ARGUMENTS` if present. Accepted values: `feature`, `testcase`, `automation`, `doc`, `default`. If absent → `default`. The lens determines which **output template** the agent loads (default uses the standard `## Tasks (todo list)` + `## Verification map` shape; the named lenses load alternative output formats from the matching skill — see "Lenses" below).

3. Delegate to the `bnac-task-planner` agent with these instructions:
   - If `$ARGUMENTS` is a milestone ID (e.g., `M3`) → edit the matching `m3-<slug>.md` file
   - If `$ARGUMENTS` is a `m<N>-<slug>.md` path → edit it directly
   - If `$ARGUMENTS` is `.claude/phases/index.md` → edit every milestone whose `## Tasks (todo list)` is still the placeholder
   - If `$ARGUMENTS` is a PRD path (e.g., `docs/PRD-auth.md`) and `--lens` is set → derive tasks/cases/docs/automation from the PRD per the lens's output format
   - If `$ARGUMENTS` is a scope description (anything not matching the patterns above, after stripping flags) → tasks under the active milestone
   - If no arguments → auto-detect: active milestone in `milestone-status.md`, then most recent unfilled milestone

4. The bnac-task-planner agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, `.claude/CLAUDE.md`, `SUMMARY.md`, `milestone-status.md`)
   - **Read** the milestone `.md` (goal, acceptance test, agents involved, high-level tasks, acceptance criteria) and the parent phase `index.md`
   - **Read** the lens skill if `--lens` is set:
     - `--lens feature` → `feature-planning/SKILL.md` + `feature-planning/reference/output-format.md`
     - `--lens testcase` → `testcase-planning/SKILL.md` + `testcase-planning/reference/output-format.md`
     - `--lens automation` → `automation-planning/SKILL.md` + `automation-planning/reference/output-format.md`
     - `--lens doc` → `docs-planning/SKILL.md` + `docs-planning/reference/output-format.md`
     - `--lens default` (or absent) → standard `## Tasks (todo list)` + `## Verification map` shape
   - **Glob** + **Read** reference code in the target area to find existing patterns
   - Decompose each high-level task into atomic tasks with explicit file paths, `@agent` attribution, S/M/L complexity, dependencies, and optional `Steps:` blocks — **filtered by the resolved scope set** (see "Scope filter" below)
   - Add a final HUMAN REVIEW CHECKPOINT task (no `@agent`, depends on the last work task) — always emitted regardless of scope or lens
   - Build the verification map — every acceptance condition → task IDs (drop conditions whose only verifying task type is filtered out, and note them under "Out of scope for this plan")
   - Sanity-check complexity mix vs. milestone size
   - **Edit** the milestone `.md` (or write the lens-shaped plan when `$ARGUMENTS` is a PRD path without an existing milestone target) to:
     - Replace the `## Tasks (todo list)` placeholder with the filled checklist (or the lens's output template)
     - Append `## Verification map` after `## Tasks (todo list)` (default lens) — or the lens-specific sections (Architecture Decisions / TC catalog / CI integration / Doc inventory)
     - Append a `## Scope` line recording the resolved scope set (e.g., `Scope: code,test`)
     - Append a `## Lens` line if `--lens` was non-default (e.g., `Lens: testcase`)

5. After completion, append a log entry to `.claude/log.md` (include the resolved scope set and lens).

## Scope filter

The `--scope` flag controls which **task types** end up in the checklist. It does not change the lens — atomic-task discipline (file paths, S/M/L, `@agent`, dependencies) and the HUMAN REVIEW CHECKPOINT apply to every scope.

| Scope value | Includes these `@agent` tasks                                                                                  |
|-------------|----------------------------------------------------------------------------------------------------------------|
| `code` (default) | `@architect`, `@code-developer`, `@code-reviewer`, `@status-manager`, plus `@security-auditor` / `@perf-optimizer` / `@devops-engineer` if listed in the milestone's `## Agents involved`. The HUMAN REVIEW CHECKPOINT is always last. |
| `test`      | `@test-engineer` tasks — unit, integration, E2E.                                                                |
| `doc`       | `@doc-writer` tasks — README, API reference, runbooks, ADRs.                                                    |

**Resolution rules:**
- Default when `--scope` is absent: `code` only.
- `--scope test` (or `--scope doc`) on its own emits **only** that scope's tasks plus the HUMAN REVIEW CHECKPOINT — useful when running specialized planning passes after a code-only plan already exists. Re-running with a different scope **replaces** the `## Tasks (todo list)` section; if you want to extend an existing plan rather than replace it, pass the union (e.g., `--scope code,test`) and the planner will preserve task IDs that haven't changed.
- Combinations: `code,test`, `code,doc`, `test,doc`, `code,test,doc`. Order doesn't matter.
- Unknown values → fail loud, do not silently drop.

## Output that lands on disk

```
.claude/phases/phase-1-foundation/
└── m1-service-scaffold.md      ← edited: ## Tasks section filled, ## Verification map appended
```

That's the only file change. **No new folders, no new `.md` files, no `tasks/` subfolder.**

Each task line carries an `@agent` attribution so the milestone is self-routing — agents pick up tasks tagged for them without a separate dispatch table. The final task is always a HUMAN REVIEW CHECKPOINT (no `@agent`), gating milestone completion.

### Filled section shape (excerpt)

```markdown
## Tasks (todo list)

- [ ] **M1.1** (@architect) — Design Express app skeleton + route topology
       Files: `docs/architecture/M1_app_skeleton.md`
       Complexity: S · Depends on: —

- [ ] **M1.5** (@code-developer) — Add /health route
       Files: `src/routes/health.ts`
       Complexity: S · Depends on: M1.4
       Steps:
         1. Add `healthRouter` returning 200 + `{"status":"ok"}`.
         2. Mount in `src/app.ts` before the 404 handler.

- [ ] **M1.13** — **HUMAN REVIEW CHECKPOINT** (gates milestone completion)
       Files: review-only
       Complexity: — · Depends on: M1.12

**Complexity mix:** 11×S + 1×M + 1×review  (matches "small milestone" feel ✓)

## Verification map
Every condition in M1's acceptance test must trace to ≥1 task.

| Acceptance test condition                       | Tasks verifying it     |
|--------------------------------------------------|------------------------|
| `npm install` succeeds                           | M1.2, M1.3             |
| `GET /health` returns 200 + `{"status":"ok"}`    | M1.5, M1.9             |
| Human reviewer approves                          | M1.13                  |
```

## Lenses vs. scope (orthogonal)

`--scope` subsets **which task types** end up in the default-lens checklist. `--lens` switches **the entire output shape** when you want a specialized plan (test-case catalog with TC-IDs, doc inventory with audience analysis, etc.).

| Flag | Lens skill | What it adds inside the milestone .md (or PRD-derived plan) |
|------|-----------|--------------------------------------------------------------|
| `--lens feature` | `feature-planning` | Goal, Architecture Decisions, Risks, Out of Scope (in addition to the task checklist) |
| `--lens testcase` | `testcase-planning` | TC-IDs, Happy/Edge/Error/Security categories, P1/P2/P3 priority per task |
| `--lens automation` | `automation-planning` | What-to-automate, framework, CI integration |
| `--lens doc` | `docs-planning` | Doc inventory, audience, content outlines per task |
| `--lens default` (or absent) | — | Standard `## Tasks (todo list)` + `## Verification map` shape |

`--scope` and `--lens` compose freely — e.g., `--lens testcase --scope test` or `--lens doc --scope doc`. They edit the same milestone `.md`; per-task metadata and any extra appended sections differ.

> **Migration note.** This flag replaces the legacy `/bnac-plan-feature`, `/bnac-plan-testcase`, `/bnac-plan-automation`, and `/bnac-plan-docs` commands. The lens skills themselves are unchanged.

## Guarantees

- **One file per atomic task — embedded.** Atomic tasks live as `- [ ] M<N>.<i>` checkboxes inside the milestone `.md`. Future agents (`bnac-developer`, `bnac-reviewer`, `bnac-milestone-tracker`) read the milestone .md to pick up a task.
- **Per-milestone task numbering.** IDs are `M<N>.<i>` resetting `<i>` per milestone.
- **Self-routing.** Each task has an `@agent` attribution; agents work by filtering the checklist.
- **Verification map is mandatory.** Every acceptance condition traces back to task IDs.
- **Bounded blast radius.** Edits stay inside the milestone `.md` (plus a `log.md` append). No new files, no source-code edits.

## Examples

```
# Default lens (standard task checklist)
/bnac-task-plan M3                                                        → fill M3's tasks (code only — default)
/bnac-task-plan M3 --scope code,test                                      → code + tests
/bnac-task-plan M3 --scope code,test,doc                                  → code + tests + docs
/bnac-task-plan M3 --scope test                                           → tests only (run after a prior code-scoped plan)
/bnac-task-plan M3 --scope doc                                            → docs only
/bnac-task-plan .claude/phases/phase-1-foundation/m1-service-scaffold.md
                                                                          → fill that milestone's tasks (code only — default)
/bnac-task-plan .claude/phases/index.md --scope code,test                 → fill tasks (code + test) for every milestone with an empty placeholder
/bnac-task-plan refactor auth middleware                                  → tasks under the active milestone from a free-text scope (code only)
/bnac-task-plan                                                           → auto-detect active milestone (code only)

# Specialized lenses (replace the old /bnac-plan-* commands)
/bnac-task-plan M3 --lens feature                                         → feature plan (Architecture Decisions, Risks, Out of Scope)
/bnac-task-plan M3 --lens testcase                                        → test-case catalog with TC-IDs + categories
/bnac-task-plan M3 --lens automation                                      → automation strategy (what to automate, CI integration)
/bnac-task-plan M3 --lens doc                                             → docs plan (inventory, audience, content outlines)
/bnac-task-plan docs/PRD-auth.md --lens testcase                          → derive test cases directly from a PRD
/bnac-task-plan src/api/ --lens doc                                       → docs plan for an existing code area
```

## Next step after running

Run `/bnac-milestone start M<N>` to activate the milestone, then `/bnac-feature-dev <task-id>` (or stack-specific commands) to implement individual tasks.
