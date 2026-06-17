Invoke the **bnac-phase-planner** agent to enrich each phase's `index.md` under `.claude/phases/` with goals, single objective exit criteria, agents-involved rollup, quality gates, milestone allocation, and dependencies — and to enrich the top-level `phases/index.md` with the cross-phase rollup.

**Agent:** `bnac-phase-planner`
**Target:** `$ARGUMENTS` (phase ID, top-level plan path, PRD path, or scope description; optional — auto-detects existing skeleton)
**Output folder:** Always `.claude/phases/` in the current project root.

> **Path convention.** Every `.claude/...` path below is **relative to the current working directory** — the folder you ran `/bnac-phase-plan` from. The planner agent must write directly into `<cwd>/.claude/`. **Never create a literal `project/` folder** — if you see `project/.claude/...` anywhere on disk, that's a bug. Distinct from `~/.claude/` (your home-directory global BNAC content).

## What to do

1. Delegate to the `bnac-phase-planner` agent with these instructions:
   - If `$ARGUMENTS` is a phase ID (e.g., `phase-1`, `phase-2`) → enrich only that phase folder
   - If `$ARGUMENTS` is `.claude/phases/index.md` → enrich every existing phase folder
   - If `$ARGUMENTS` is a PRD path → derive scope, then phase (creates folders if `bnac-planner` was skipped)
   - If `$ARGUMENTS` is a scope description → phase the described scope
   - If no arguments → auto-detect: existing top-level `index.md` first, then PRD

2. The bnac-phase-planner agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, `.claude/CLAUDE.md`, `SUMMARY.md`, `milestone-status.md`)
   - **Read** the top-level plan at `.claude/phases/index.md` (if present) and the PRD source
   - **Glob** `.claude/phases/phase-*/index.md` to enumerate existing stubs
   - Pick a phase pattern (greenfield / migration / library / internal-tool / platform) from the `phase-template` skill
   - Adjust the pattern to project specifics
   - **Edit** each phase `index.md` in place with: number ID (`Phase 1`, `Phase 2`, …), one-sentence goal, single testable exit criterion, estimated milestone count, dependencies, agents-involved rollup, quality gates checklist, cross-milestone agent rollup, allocated milestone IDs (M1, M2, … globally numbered)
   - **Edit** top-level `phases/index.md` — fill goal/exit-criterion columns, add Status column, append milestone-allocation + agents-engaged + cross-phase-risks tables
   - **Write** any net-new phase folders if `bnac-planner` was skipped (`phase-<N>-<slug>/index.md`)
   - Recommend `/bnac-milestone-plan phase-<N>` next

3. After completion, append a log entry to `.claude/log.md`.

## Output that lands on disk

```
.claude/phases/
├── index.md                              ← edited (Status column added, allocation + agents-engaged tables appended)
├── phase-1-<slug>/index.md               ← edited (goal, exit criterion, agents involved, quality gates, milestone allocation)
├── phase-2-<slug>/index.md               ← edited
└── phase-N-<slug>/index.md               ← edited
```

Phase folders still contain only `index.md` — no `m<N>-<slug>.md` milestone files yet. That's `/bnac-milestone-plan`'s job.

## Guarantees

- **Edits in place.** Existing folder slugs are preserved; only `index.md` content + top-level columns are updated.
- **Bounded blast radius.** The agent only writes under `.claude/phases/**` and appends to `.claude/log.md`.
- **Idempotent.** Re-running enriches the same files — no duplicate phase folders.

## Examples

```
/bnac-phase-plan phase-1                       → enrich Phase 1 only
/bnac-phase-plan .claude/phases/index.md → enrich every phase in the skeleton
/bnac-phase-plan ./prds/payment-service/       → derive phases from PRD (creates skeleton if missing)
/bnac-phase-plan migrate auth to OIDC          → phase a free-text scope
/bnac-phase-plan                               → auto-detect existing skeleton or PRD
```

## Next step after running

Run `/bnac-milestone-plan phase-<N>` for each phase to write `m<N>-<slug>.md` milestone files flat into each phase folder.
