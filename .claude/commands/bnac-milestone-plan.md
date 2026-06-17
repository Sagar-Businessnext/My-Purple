Invoke the **bnac-milestone-planner** agent to write one `m<N>-<slug>.md` file flat inside each `.claude/phases/phase-<N>-<slug>/` folder, with goal, status, single acceptance test, agents involved, high-level tasks, deliverables, acceptance criteria, definition of done, and risks. Leaves `## Tasks (todo list)` as a placeholder for `/bnac-task-plan`.

**Agent:** `bnac-milestone-planner`
**Target:** `$ARGUMENTS` (phase ID, top-level `index.md` path, or PRD path; optional — auto-detects)
**Flags:** `--scope code[,test][,doc]` (optional; default `code`)
**Output folder:** Always `.claude/phases/phase-<N>-<slug>/` in the current project root. Milestones are flat `.md` files inside the phase folder — no `milestones/` subfolder.

> **Path convention.** Every `.claude/...` path below is **relative to the current working directory** — the folder you ran `/bnac-milestone-plan` from. The planner agent must write directly into `<cwd>/.claude/`. **Never create a literal `project/` folder** — if you see `project/.claude/...` anywhere on disk, that's a bug. Distinct from `~/.claude/` (your home-directory global BNAC content).

## What to do

1. Parse `--scope` from `$ARGUMENTS` if present. Accepted values: `code`, `test`, `doc` (comma-separated). If absent → default to `code`. Pass the resolved scope set to the agent so it can shape `## Agents involved`, the `## High-level tasks` table rows, and the `Definition of Done` checklist accordingly.

2. Delegate to the `bnac-milestone-planner` agent with these instructions:
   - If `$ARGUMENTS` is a phase ID (e.g., `phase-1`, `phase-2`) → write milestones into that phase folder
   - If `$ARGUMENTS` is `.claude/phases/index.md` → write milestones for every phase that has none
   - If `$ARGUMENTS` is a PRD path → derive scope, then write milestones (under wrapper phase for medium tier)
   - If no arguments → auto-detect: active phase from `milestone-status.md`, then `index.md`, then PRD

3. The bnac-milestone-planner agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, `.claude/CLAUDE.md`, `SUMMARY.md`, `milestone-status.md`)
   - **Glob** `.claude/phases/phase-*/m*.md` to detect the highest existing M-number — milestone IDs are globally numbered, never reset per phase
   - **Read** the parent `phase-<N>-<slug>/index.md` and the PRD source
   - Identify scope boundaries (deliverable, tech, verification)
   - For each milestone:
     - **Write** `phase-<N>-<slug>/m<N>-<slug>.md` (flat in phase folder) with:
       - Status (`Not Started`), Goal, **single objective acceptance test**, Estimated tasks
       - **Agents involved** — only those whose category is in the resolved scope set (always include code-side agents under `code`; include `Test Engineer Agent` only when `test` ∈ scope; include `Documentation Writer Agent` only when `doc` ∈ scope; specialty agents follow the milestone's nature)
       - **High-level tasks table** (5–8 rows) — drop rows whose `Type` is filtered out (`test` rows when `test` ∉ scope, `docs` rows when `doc` ∉ scope)
       - `## Tasks (todo list — populated by /bnac-task-plan)` placeholder
       - `Scope: <resolved-scope>` line directly under the `## Tasks` placeholder so `/bnac-task-plan` defaults to the same set unless overridden
       - Deliverables (drop test/doc artifacts when their scope is excluded)
       - Acceptance criteria checklist (drop checks whose only verification path was just removed; record those under a `## Out of scope for this milestone plan` section with the follow-up command)
       - Dependencies
       - Definition of Done (incl. human review checkpoint; the "Tests pass" / "Documentation updated" lines stay only when their scope is included)
       - Risks
   - **Edit** the parent `phase-<N>-<slug>/index.md` "Milestones in this phase" table to link real files
   - Identify cross-milestone risks (recorded in parent `index.md`)
   - Recommend `/bnac-task-plan M<N> --scope <resolved-scope>` for each milestone (matching the scope used here)

4. After completion, append a log entry to `.claude/log.md` (include the resolved scope set).

## Scope filter

`--scope` here shapes which agents and high-level task rows show up in the milestone .md, and which acceptance/DoD lines get retained. It does **not** suppress the `## Tasks (todo list)` placeholder — that stays empty for `/bnac-task-plan` to fill. The recommended next-step command embeds the same scope so the downstream task plan stays aligned by default.

| Scope value | Effect on the milestone .md |
|-------------|------------------------------|
| `code` (default) | Code-side agents only. High-level tasks table excludes `test` and `docs` rows. DoD drops the "tests pass" and "documentation updated" lines. |
| `test`           | Adds Test Engineer Agent + `test` rows + DoD "tests pass" line. |
| `doc`            | Adds Documentation Writer Agent + `docs` rows + DoD "documentation updated" line. |
| Any combination  | Union of the above. |

If a single PRD/phase needs a mix where some milestones cover tests and others don't, run `/bnac-milestone-plan` separately per phase with the right `--scope`, or run a code-only pass first and then re-run with `--scope code,test,doc` over a specific phase ID later.

## Output that lands on disk

```
.claude/phases/phase-1-foundation/
├── index.md                            ← edited (Milestones table linked to real files)
├── m1-service-scaffold.md              ← written by this command
├── m2-db-migration-baseline.md         ← written by this command
└── m3-ci-pipeline.md                   ← written by this command
```

**No `milestones/` subfolder. No `tasks/.gitkeep`. No per-task .md files.** Tasks will live inside each `m<N>-<slug>.md` once `/bnac-task-plan` runs — as a `## Tasks (todo list)` checklist.

## Distinct from `/bnac-milestone` lifecycle

This command **defines** milestones from scope. To **activate / report on / complete** an existing milestone, use:
- `/bnac-milestone start <M#>` — activate a milestone
- `/bnac-milestone status [M#]` — show milestone progress
- `/bnac-milestone complete [M#]` — complete and archive a milestone

These wire to `bnac-milestone-tracker`, not `bnac-milestone-planner`.

## Guarantees

- **Global M-numbering.** The agent globs the entire `phases/` tree to find the next M-number; never duplicates, never resets per phase.
- **Idempotent.** Re-running edits existing milestone files; doesn't create duplicates.
- **Bounded blast radius.** Writes stay under `.claude/phases/**` (plus a `log.md` append).
- **Flat shape.** Milestone files sit directly in the phase folder, never under a `milestones/` subfolder.

## Examples

```
/bnac-milestone-plan phase-1                                    → write m<N>-*.md flat into phase-1 folder (code only — default)
/bnac-milestone-plan phase-1 --scope code,test                  → milestones with code + test agents, rows, DoD lines
/bnac-milestone-plan phase-1 --scope code,test,doc              → milestones with all three categories
/bnac-milestone-plan .claude/phases/index.md            → fill milestones for every phase (code only)
/bnac-milestone-plan ./prds/payment/ --scope code,doc           → PRD-derived milestones with code + docs (no tests at this layer)
/bnac-milestone-plan                                            → auto-detect upstream plan (code only)
```

## Next step after running

Run `/bnac-task-plan M<N>` (defaults to the milestone's recorded `Scope:`) for each milestone — it will edit the milestone `.md` to fill `## Tasks (todo list)` with the atomic checklist. Pass an explicit `--scope` to override. Or `/bnac-milestone start M<N>` to activate the first one.
