---
project: {{PROJECT_NAME}}
updated: {{TIMESTAMP}}
active: M1
---

# Milestone Status

> **Project:** {{PROJECT_NAME}}
> **Last updated:** {{TIMESTAMP}}
> **Active milestone:** M1

## Progress

| # | Milestone | Tasks | Status |
|---|-----------|-------|--------|
| M1 | {{MILESTONE_1_TITLE}} | 0/0 | <- ACTIVE |
| M2 | {{MILESTONE_2_TITLE}} | 0/0 | UPCOMING |
| M3 | {{MILESTONE_3_TITLE}} | 0/0 | UPCOMING |

<!-- Add more rows as milestones are planned -->
<!-- Status values: <- ACTIVE | UPCOMING | DONE | SKIPPED | BLOCKED -->

---

## Active Milestone Detail

### M1 — {{MILESTONE_1_TITLE}}

**Goal:** <!-- One sentence describing what this milestone delivers -->

**Exit criteria:** <!-- How do you know this milestone is done? -->

#### Tasks
- [ ] Task 1 — specific, actionable output
- [ ] Task 2 — specific, actionable output
- [ ] Task 3 — specific, actionable output

<!-- Each task must describe a concrete output, not "work on X" -->
<!-- Check [x] immediately when a task is done -->
<!-- Update the progress count in the table above after each completion -->

#### Blockers
<!-- List anything blocking progress. Remove when resolved. -->
- None

---

## Completed Milestones

<!-- Milestones move here when `/bnac-milestone complete` is run -->
<!-- Format:
### M<N> — <Title> (completed <date>)
- [x] Task 1
- [x] Task 2
- [x] Task 3
-->

---

## Quality Gate History

<!-- Record quality gate results when milestones are completed -->
<!-- Run `/bnac-quality-gate` before completing a milestone -->

| Milestone | Build | Types | Lint | Tests | Result |
|-----------|-------|-------|------|-------|--------|
<!-- | M1 | pass | pass | pass | pass | PASS | -->
