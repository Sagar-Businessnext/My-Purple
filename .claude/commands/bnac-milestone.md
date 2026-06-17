Invoke the **bnac-milestone-tracker** agent for milestone lifecycle: `start`, `status`, or `complete`. One command, action-driven — replaces `/bnac-milestone-start`, `/bnac-milestone-status`, and `/bnac-milestone-complete`.

**Agent:** `bnac-milestone-tracker`
**Target:** `$ARGUMENTS` — `<action> [milestone-id]`
**Actions:** `start` · `status` · `complete`

## Action map

| Action | Arg shape | Replaces legacy command | What it does |
|---|---|---|---|
| `start <M#>` | required | `/bnac-milestone-start` | Activate a milestone, load tasks from the plan into `milestone-status.md` |
| `status [M#]` | optional (defaults to active) | `/bnac-milestone-status` | Report progress on the active or named milestone |
| `complete [M#]` | optional (defaults to active) | `/bnac-milestone-complete` | Verify all tasks checked, archive, advance to next milestone |

If `action` is omitted, default to `status`.

## What to do

1. Parse `<action>` from `$ARGUMENTS` (first positional). If absent → `status`.
2. Parse `<milestone-id>` (second positional, e.g., `M3` or a title).
3. Delegate to the `bnac-milestone-tracker` agent with the resolved action + milestone reference.

### When action = `start`

1. Read `.claude/milestone-status.md` to understand current state.
2. Read the project's milestone plan (PRD, MILESTONES.md, `.claude/phases/**/m*.md`) to get task details for the requested milestone.
3. Verify no other milestone is currently active. If one is, warn and ask to complete or abort it first.
4. Update `.claude/milestone-status.md`:
   - Set `active:` frontmatter to the new milestone ID
   - Set `updated:` to current timestamp
   - Mark the new milestone row as `<- ACTIVE` in the Progress table
   - Populate "Active Milestone Detail" with task checklist from the plan (`- [ ]` items)
5. Delegate to `bnac-context-compactor` (stitch-only mode) to rebuild `.claude/context/carry-forward.md` — the newly-active milestone becomes a pointer line, not a block. Skip silently if `.claude/context/` doesn't exist (legacy project).
6. Output confirmation (tasks loaded, goal, next steps).
7. Log to `.claude/log.md`: milestone activated, task count, carry-forward rebuilt, timestamp.

### When action = `status`

1. Read `.claude/milestone-status.md` for the active milestone and task list.
2. Read `.claude/SUMMARY.md` for project context (if present).
3. If `<milestone-id>` is provided, show that milestone's details; otherwise the active one.
4. Output a progress report: completed/total tasks, status (IN PROGRESS / BLOCKED / READY FOR QG), task list with the current item flagged, blockers, next steps.
5. Log the status check to `.claude/log.md`.

### When action = `complete`

1. Read `.claude/milestone-status.md` to identify the active (or named) milestone.
2. Verify ALL tasks are checked `[x]`. If any are unchecked, list them and **do not complete** — ask user to finish or skip them.
3. Recommend running `/bnac-quality-gate` before completing. If it hasn't been run, warn but allow completion.
4. Update `.claude/milestone-status.md`:
   - Move the active milestone detail to the "Completed Milestones" section
   - Mark the milestone row as `DONE` in the Progress table
   - Set the next milestone as `<- ACTIVE` (if one exists)
   - Clear the "Active Milestone Detail" section for the next milestone
   - Update `active:` frontmatter and `updated:` timestamp
5. Delegate to `bnac-context-compactor` (milestone mode, trigger=complete):
   - Writes `<phase-folder>/<milestone-file>.summary.md` per the compact-milestone-template skill (≤500 tokens)
   - Rebuilds `.claude/context/carry-forward.md`
   - Skip silently if `.claude/context/` doesn't exist (legacy project) — milestone still completes.
6. Output completion summary (tasks completed, quality gate status, summary written + carry-forward rebuilt stats, next milestone hint).
7. Log to `.claude/log.md`: milestone completed, task count, summary file path, carry-forward stats, next milestone, timestamp.

## Rules (for `complete`)

- NEVER complete a milestone with unchecked tasks — list remaining work instead.
- ALWAYS recommend quality gate before completion.
- ALWAYS archive completed milestone detail (don't delete; move to Completed section).
- ALWAYS activate the next milestone in sequence if one exists.

## Examples

```
/bnac-milestone start M1                    → activate milestone 1
/bnac-milestone start M3                    → activate milestone 3
/bnac-milestone start "User Authentication" → activate by title
/bnac-milestone status                      → progress of the active milestone
/bnac-milestone status M3                   → progress of M3 specifically
/bnac-milestone                              → defaults to status (active milestone)
/bnac-milestone complete                    → complete the active milestone
/bnac-milestone complete M3                 → complete M3 specifically
```

## Distinct from `/bnac-milestone-plan`

This command **operates** on milestones (lifecycle). To **define** milestones from scope, use `/bnac-milestone-plan` — it writes `m<N>-<slug>.md` files under `.claude/phases/phase-<N>-<slug>/`. That command wires to `bnac-milestone-planner`, not `bnac-milestone-tracker`.
