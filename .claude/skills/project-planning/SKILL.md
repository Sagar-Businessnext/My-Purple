---
name: project-planning
description: High-level scope-to-plan decomposition — decides whether a project needs phases, just milestones, or just tasks, and how the planner agents delegate. Defines the canonical flat folder shape (phases/phase-<N>-<slug>/m<N>-<slug>.md) used across the BNAC planning hierarchy.
user-invocable: false
argument-hint: ""
---

Decompose a project scope into the right shape — phases, milestones, or tasks — and route through the BNAC planning hierarchy. Used by `bnac-planner` as the top-level orchestrator.

## Additional Resources

- [reference/scope-decomposition.md](reference/scope-decomposition.md) — signals that determine whether a project needs phases vs milestones vs tasks
- [reference/delegation-hierarchy.md](reference/delegation-hierarchy.md) — how `bnac-planner` delegates to `bnac-phase-planner`, `bnac-milestone-planner`, `bnac-task-planner`, plus the canonical on-disk folder shape

## Steps

1. **Read the scope** — PRD, project description, or scope reference
2. **Size the project** using the signals in `reference/scope-decomposition.md` (small / medium / large)
3. **Choose the decomposition depth:**
   - **Large** (>15 milestones, multi-quarter) → phases → milestones → tasks
   - **Medium** (5–15 milestones, 1–3 months) → milestones → tasks (single wrapper phase)
   - **Small** (<5 milestones, <1 month) → tasks only (single wrapper phase + milestone)
4. **Delegate to the right planner** per `reference/delegation-hierarchy.md`
5. **Synthesize the top-level plan** — one document (`phases/index.md`) linking down to per-phase, per-milestone, per-task detail
6. **Output structured plan** — phases or milestones with clear exit criteria, the recommended next planner to invoke

## Canonical on-disk shape (NON-NEGOTIABLE)

Every BNAC project plan lands at exactly this layout — flat, no nested `milestones/` subfolder:

```
project/.claude/phases/
├── index.md                              ← top-level plan
├── phase-1-<slug>/
│   ├── index.md                          ← phase plan
│   ├── m1-<slug>.md                      ← milestone (FLAT in phase folder)
│   ├── m2-<slug>.md
│   └── m3-<slug>.md
├── phase-2-<slug>/
│   ├── index.md
│   └── m4-<slug>.md
└── phase-N-<slug>/
    ├── index.md
    └── m<N>-<slug>.md
```

| Element | Form | Rule |
|---|---|---|
| Phase ID | `phase-1`, `phase-2`, … | Number, not letter. Always start at 1; never skip. |
| Milestone ID | `M1`, `M2`, … | **Globally numbered** — continues across phases, never resets. |
| Task ID | `M<N>.<i>` | `<i>` resets per milestone. **Tasks are NOT separate files** — they live as a checklist inside each `m<N>-<slug>.md`. |

## Rules

- **Decompose, don't prescribe** — `bnac-planner` decides the shape and delegates. The detail comes from the lower planners. Don't write all the tasks yourself.
- **One source of truth** — The top-level plan references downstream plans by relative path; it does not duplicate them.
- **Read existing state first** — Check `project/.claude/phases/index.md`, `project/.claude/milestone-status.md`, and any existing plans before producing a new one.
- **Cite assumptions explicitly** — If sizing depends on assumptions (e.g., team size, deadline), state them at the top of the plan so the user can correct.
- **Never skip signals** — All sizing signals in `reference/scope-decomposition.md` must be evaluated, even if briefly.
- **Flat shape is invariant** — Even medium and small projects use a single wrapper phase folder so the downstream tree shape stays consistent.
