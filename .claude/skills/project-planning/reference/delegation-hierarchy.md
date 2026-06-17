# Delegation Hierarchy — How `bnac-planner` Routes Work

The BNAC planning hierarchy decomposes a project from coarse to fine. `bnac-planner` is the top — every other planning agent reports up through it. Each level **edits the same on-disk tree** rather than producing standalone documents.

## The hierarchy

```
bnac-planner            ← project root (PRD or scope)
  ├─ bnac-phase-planner    ← phases (phase-1, phase-2, …) for large projects
  │    └─ bnac-milestone-planner    ← milestones (M1, M2, …) per phase, written FLAT in the phase folder
  │         └─ bnac-task-planner    ← tasks per milestone, EMBEDDED inside the milestone .md
  ├─ bnac-changelog-agent           ← parallel: maintains CHANGELOG.md
  └─ bnac-status-update-agent       ← parallel: writes status updates
```

Vertical = decomposition. Horizontal (changelog/status) = reporting; runs alongside, not below.

## Canonical on-disk shape (every level edits the same tree)

```
project/.claude/phases/                          ← bnac-planner creates the folder
├── index.md                                     ← bnac-planner writes (top-level plan)
├── phase-1-foundation/                          ← bnac-planner creates the phase folder
│   ├── index.md                                 ← bnac-planner writes a stub; bnac-phase-planner enriches it
│   ├── m1-service-scaffold.md                   ← bnac-milestone-planner writes; bnac-task-planner edits to add tasks
│   ├── m2-db-migration-baseline.md
│   └── m3-ci-pipeline.md
├── phase-2-core-payments/
│   ├── index.md
│   ├── m4-...md
│   └── ...
└── phase-N-<slug>/
    ├── index.md
    └── m<N>-<slug>.md
```

**Invariants:**
- `phase-<N>-<slug>/` — number, not letter (`phase-1`, not `A`).
- Milestones are **single `.md` files flat inside the phase folder** — no `milestones/` subfolder.
- **Tasks are NOT separate files** — they live as a `## Tasks (todo list)` checklist inside `m<N>-<slug>.md`.
- IDs: phase numbered from 1; milestones globally numbered (`M1, M2, … M16`); tasks per-milestone (`M1.1, M1.2, … M2.1`).

## Who delegates to whom

| Caller | Delegates to | When |
|---|---|---|
| `bnac-planner` | `bnac-phase-planner` | Large project — needs phases |
| `bnac-planner` | `bnac-milestone-planner` | Medium project — phases not needed (single wrapper phase) |
| `bnac-planner` | `bnac-task-planner` | Small project — milestones not needed (single wrapper phase + milestone) |
| `bnac-phase-planner` | `bnac-milestone-planner` | After phases are enriched, fill milestones per phase |
| `bnac-milestone-planner` | `bnac-task-planner` | After milestones are written, embed atomic tasks in each milestone .md |
| `bnac-task-planner` | (terminal) | Edits the milestone .md to embed tasks — no further delegation |

## Each agent's contract

### `bnac-planner`
- **Input:** PRD, project description, or scope reference
- **Writes:** `phases/index.md` + one `phase-<N>-<slug>/index.md` stub per phase (placeholders for goal/exit criterion)
- **Does NOT:** Write phase enrichment, milestones, or tasks

### `bnac-phase-planner`
- **Input:** Existing skeleton (or large project scope from `bnac-planner`)
- **Edits:** each `phase-<N>-<slug>/index.md` (goal, single objective exit criterion, agents-involved rollup, quality gates, milestone allocation) + top-level `phases/index.md` (status column, milestone allocation table, project-wide agents rollup)
- **Does NOT:** Write milestone files or tasks

### `bnac-milestone-planner`
- **Input:** A phase (from `bnac-phase-planner`) OR a medium project (from `bnac-planner`)
- **Writes:** one `m<N>-<slug>.md` flat in the phase folder per allocated milestone (Status, Goal, single Acceptance Test, Agents involved, 5–8 high-level tasks, Deliverables, Acceptance criteria, DoD, Risks)
- **Edits:** parent phase `index.md` to link real milestone files
- **Does NOT:** Embed atomic tasks (leaves `## Tasks (todo list)` as placeholder)

### `bnac-task-planner`
- **Input:** A milestone (from `bnac-milestone-planner`) OR a small project (from `bnac-planner`)
- **Edits:** the existing `m<N>-<slug>.md` to fill `## Tasks (todo list)` with `- [ ] M<N>.<i>` checkboxes (each with `@agent` attribution, files, complexity, dependencies, optional steps) plus a final HUMAN REVIEW CHECKPOINT task; appends `## Verification map` table linking each acceptance condition → task IDs
- **Does NOT:** Write new files. **No separate task files.**

## Output linking

Each level edits or links into the same tree. The level above references the level below by relative path:

```markdown
# Project Plan: <name>             ← phases/index.md
## Phases
| Folder              | …
| phase-1-foundation/ | …          ← clickable link to phase-1-foundation/index.md
```

```markdown
# Phase 1: Foundation              ← phase-1-foundation/index.md
## Milestones in this phase
| ID | Title       | File
| M1 | Scaffold    | [m1-service-scaffold.md](./m1-service-scaffold.md)
```

This keeps each document focused and avoids the "huge file with everything" anti-pattern.

## Re-planning

When scope changes mid-project, the hierarchy re-runs from the affected level down:

| Change | Re-runs from |
|---|---|
| New requirement added | `bnac-milestone-planner` (or `bnac-task-planner` for the affected milestone) |
| Whole new phase needed | `bnac-phase-planner` |
| Project sizing changed (medium → large) | `bnac-planner` |
| Single task estimate wrong | `bnac-task-planner` (just that milestone .md) |

Never re-run from the top unless scope materially changed.

## Anti-patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| `bnac-planner` writes the whole task list | Bypasses the hierarchy; loses delegation value | Decompose, then delegate |
| `bnac-task-planner` invents milestones | Tasks are within a milestone, not creating one | Caller must already have a milestone |
| Skipping `bnac-milestone-planner` for a medium project | Tasks without milestone context lose acceptance criteria | Always go through milestones for medium / large |
| Embedding full task detail in the project plan | File explodes; multiple sources of truth | Link only; let task detail live inside the milestone .md |
| Creating a `milestones/` subfolder | Breaks the flat shape; downstream agents expect milestones flat in the phase folder | Write `m<N>-<slug>.md` directly in the phase folder |
| Writing per-task `.md` files | Breaks the embedded-tasks shape | Tasks belong in `## Tasks (todo list)` inside the milestone .md |
| Using letter phase IDs (`A`, `B`) | Old convention; no longer canonical | Use `phase-1`, `phase-2`, … |
