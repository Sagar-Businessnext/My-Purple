---
name: milestone-template
description: Canonical structure for milestones — globally-numbered ID, status, phase reference, goal, single acceptance test, agents involved, high-level tasks, embedded tasks placeholder, deliverables, acceptance criteria, dependencies, definition of done, risks. Used by bnac-milestone-planner. Files sit FLAT in the phase folder (no milestones/ subfolder), and atomic tasks live INSIDE the milestone .md (no separate task files).
user-invocable: false
argument-hint: ""
---

Define the canonical shape of a milestone: an integer ID (`M1, M2, …` globally numbered), a status field, a one-line goal, a single objective acceptance test, an agents-involved list, a high-level task table, a placeholder for embedded atomic tasks, deliverables, acceptance criteria, dependencies on prior milestones, and a Definition of Done checklist.

## Additional Resources

- [reference/milestone-format.md](reference/milestone-format.md) — milestone document structure and required fields
- [reference/acceptance-tests.md](reference/acceptance-tests.md) — how to write a milestone's acceptance test (what makes a good one)

## On-disk shape (NON-NEGOTIABLE)

Milestone `.md` files sit **flat** inside the phase folder — there is no `milestones/` subfolder.

```
project/.claude/phases/phase-<N>-<slug>/
├── index.md                  ← phase plan
├── m<a>-<slug>.md            ← milestone (this skill defines its shape)
├── m<b>-<slug>.md
└── m<c>-<slug>.md
```

Atomic tasks live **inside** each `m<N>-<slug>.md` as a `## Tasks (todo list)` checklist after `/bnac-task-plan` runs. There are no separate task files.

## Format

```markdown
# M<N>: <Title>

**Phase:** phase-<N>-<slug>
**Status:** Not Started        ← Not Started → In Progress → Review Pending → Approved
**Goal:** <one-sentence outcome>
**Acceptance test:** <single objective condition that proves "done">
**Estimated tasks:** <count or range> (+1 human review checkpoint)
**Depends on:** <prior milestone IDs, or "none">

## Agents involved
- **Architect Agent** — <role for this milestone>
- **Code Developer Agent** — <role>
- **Test Engineer Agent** — <role + coverage target>
- **Code Reviewer Agent** — <role>
- **Documentation Writer Agent** — <role>
- **Status Manager Agent** — <role>

## High-level tasks
| # | Task | Type | Complexity |
|---|------|------|------------|
| 1 | ... | create / modify / configure / test | S / M / L |
| 2 | ... | ... | ... |

## Tasks (todo list — populated by /bnac-task-plan)
_(empty — `/bnac-task-plan M<N>` will fill this with the atomic checklist with @agent attribution and a final HUMAN REVIEW CHECKPOINT)_

## Deliverables
- <file or artifact 1>
- <file or artifact 2>

## Acceptance criteria
- [ ] <observable check 1>
- [ ] <observable check 2>
- [ ] Human reviewer approves milestone

## Dependencies
- <prior milestone ID, or "None (first milestone in the phase)">

## Definition of Done
- [ ] All atomic tasks complete (`- [x]` in the Tasks section)
- [ ] Acceptance test passes
- [ ] `bnac-quality-gate` runs clean
- [ ] Documentation updated
- [ ] Activity log entries for all tasks
- [ ] Human review checkpoint approved

## Risks
- <Risk → mitigation>
```

## Example

```
# M1: Service Scaffold

**Phase:** phase-1-foundation
**Status:** Not Started
**Goal:** Empty payment-service runs `npm start` and answers `/health` with 200.
**Acceptance test:** `curl localhost:3000/health` returns 200 + JSON `{ "status": "ok" }` after `npm install && npm start`.
**Estimated tasks:** 6 (+1 human review checkpoint)
**Depends on:** none
```

## Rules

- **Acceptance test is one condition** — Multiple conditions = milestone is too broad. Split it.
- **Goal is the outcome, not the work** — "Users can log in" not "Implement login endpoint".
- **High-level tasks are signals, not contracts** — Detailed task breakdown is `bnac-task-planner`'s job (and lives inside this same `.md` after it runs).
- **`## Tasks (todo list)` placeholder is mandatory** — `/bnac-task-plan` needs the section to exist before it can fill it.
- **Definition of Done is a checklist** — Standard items + milestone-specific additions + human review checkpoint.
- **Status field is mandatory** — Every milestone starts at `Not Started` and progresses through `In Progress → Review Pending → Approved`.
- **Milestone IDs are project-globally numbered** — `M1, M2, …` continue across phases. Never reset.
- **5–8 high-level tasks per milestone is the sweet spot** — Fewer means too small, more means too broad.
- **Dependencies must be explicit** — If M3 needs M2, say so. Don't assume the reader will figure it out.
- **Files sit flat in the phase folder** — No `milestones/` subfolder; filename is `m<N>-<slug>.md`.
