Invoke the **bnac-planner** agent to produce the top-level project plan, scaffold `.claude/phases/`, and recommend the next downstream planner.

**Agent:** `bnac-planner`
**Target:** `$ARGUMENTS` (PRD path, project description, or existing plan reference; optional — auto-detects PRD folder if omitted)
**Output folder:** Always `.claude/phases/` in the current project root. `$ARGUMENTS` is the *scope source*, never the output destination.

> **Path convention.** Every `.claude/...` path below is **relative to the current working directory** — the folder you ran `/bnac-plan` from. The planner agent must write directly into `<cwd>/.claude/`. **Never create a literal `project/` folder** — if you see `project/.claude/...` anywhere on disk, that's a bug. Distinct from `~/.claude/` (your home-directory global BNAC content).

## What to do

1. Delegate to the `bnac-planner` agent with these instructions:
   - If `$ARGUMENTS` is a PRD file/folder path → decompose the full PRD scope
   - If `$ARGUMENTS` is a project description → decompose the described scope
   - If `$ARGUMENTS` is an existing plan path (`.claude/phases/index.md`, legacy `MILESTONES.md`, etc.) → re-evaluate sizing and propose adjustments
   - If no arguments → auto-detect: look for `./prds/`, `./functional-specification/prd/`, `.claude/phases/index.md`, then `MILESTONES.md`

2. The bnac-planner agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, `.claude/CLAUDE.md`, `SUMMARY.md`, `milestone-status.md`)
   - **Read** the PRD or scope source thoroughly
   - **Glob** `.claude/phases/` for any existing skeleton — edit, don't overwrite
   - Apply sizing signals from the `project-planning` skill (`reference/scope-decomposition.md`)
   - Score scope-size + risk + anti-signals → resolve to small / medium / large tier
   - Decide decomposition depth (phases → milestones → tasks, milestones → tasks, or tasks only)
   - **Scaffold** the phase-level skeleton at `.claude/phases/`:
     - `index.md` — top-level plan with sizing tier, phase map, next steps (lowercase filename)
     - `phase-<N>-<slug>/index.md` — one stub per phase with placeholders for goal + exit criterion
   - For medium / small projects → create a single wrapper phase `phase-1-<project-slug>/` so the downstream tree shape stays consistent.
   - Recommend the next command to invoke

3. After completion, append a log entry to `.claude/log.md` (command, tier, files written).

## Output skeleton (flat — invariant)

```
.claude/phases/
├── index.md                             ← top-level plan
├── phase-1-<slug>/
│   └── index.md                         ← phase stub (goal + exit criterion placeholders)
├── phase-2-<slug>/
│   └── index.md
└── phase-N-<slug>/
    └── index.md
```

**Rules of the shape:**
- `phase-<N>-<slug>/` — `<N>` is a **number** (1, 2, 3, …), not a letter.
- No `milestones/` subfolder — milestones will be written flat into each phase folder by `/bnac-milestone-plan` as `m<N>-<slug>.md`.
- No task files anywhere — tasks live as a checklist **inside** each milestone `.md` after `/bnac-task-plan` runs.

## Guarantees

- **Idempotent.** Re-running `/bnac-plan` edits existing `index.md` files; it never overwrites enriched content from downstream planners.
- **Bounded blast radius.** The agent only writes under `.claude/phases/**` and appends to `.claude/log.md`. Source code is never touched.
- **Slugs are stable.** Phase folder names are `phase-<N>-<kebab-slug>` derived from the phase title; renaming requires a manual move + re-run.

## Examples

```
/bnac-plan ./prds/payment-service/        → plan from PRD folder, write phases/ skeleton
/bnac-plan docs/SCOPE.md                  → plan from a scope document
/bnac-plan add multi-region failover      → plan from a free-text description
/bnac-plan .claude/phases/index.md → re-evaluate an existing plan, propose adjustments
/bnac-plan                                → auto-detect PRD folder or existing index.md
```

## Next steps after running

| Tier | Run next |
|------|----------|
| Large | `/bnac-phase-plan` to enrich each phase's `index.md` with goals + exit criteria, then `/bnac-milestone-plan phase-<N>` per phase |
| Medium | `/bnac-milestone-plan` to fill the wrapper phase with `m<N>-*.md` files |
| Small | `/bnac-task-plan` to embed the inline task checklist in the wrapper milestone's `.md` |
