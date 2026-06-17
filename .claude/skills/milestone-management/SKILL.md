---
name: milestone-management
description: Milestone planning, tracking, and completion — chunking work into phases, tracking progress, managing transitions
user-invocable: true
argument-hint: "<milestone-id>"
---

Manage milestone `$ARGUMENTS` — check status, start, or complete it.

## Additional resources

- [reference/milestone-workflow.md](reference/milestone-workflow.md) — full milestone lifecycle and best practices

## Milestone lifecycle

```
PLAN → START → EXECUTE → COMPLETE → NEXT
  │       │        │          │         │
  │       │        │          │         └─ Activate next milestone
  │       │        │          └─ Verify all tasks done, archive, update status
  │       │        └─ Developer works tasks, marks [x] as done, logs progress
  │       └─ Load tasks into milestone-status.md, set as active
  └─ Break scope into 3-7 task milestones with clear exit criteria
```

## Key file: `project/.claude/milestone-status.md`

This is the single source of truth for milestone progress. It contains:
- **Frontmatter:** project name, last update timestamp, active milestone ID
- **Progress table:** all milestones with task counts and status
- **Active milestone detail:** task checklist for current work
- **Completed milestones:** archived detail from finished milestones
- **Quality gate history:** pass/fail records per milestone

## Milestone sizing rules

| Guideline | Target |
|-----------|--------|
| Tasks per milestone | 3–7 (ideal: 5) |
| Duration | 1–3 sessions |
| Scope | One coherent deliverable |
| Exit criteria | Clear, testable, verifiable |

Too many tasks → split into two milestones.
Too few tasks → merge with adjacent milestone.

## Task checklist format

```markdown
### M<N> — <Title>
- [ ] Task description (specific, actionable output)
- [ ] Task description
- [x] Completed task (checked when done)
```

Each task must describe a **concrete output** — not "work on X" but "create X file" or "implement X function".

## Progress tracking

When working on a milestone:
1. Read `milestone-status.md` before starting work
2. Check off `[x]` each task immediately when done
3. Update the progress count in the table (`3/5` → `4/5`)
4. Log progress to `project/.claude/log.md`
5. When all tasks are checked, run `/bnac-milestone complete`

## Completion checklist

Before marking a milestone complete:
- [ ] All tasks checked `[x]`
- [ ] Build passes (`/bnac-quality-gate` recommended)
- [ ] Activity logged
- [ ] milestone-status.md updated with completion
- [ ] Next milestone identified

## Commands

| Command | Action |
|---------|--------|
| `/bnac-milestone start M<N>` | Activate milestone, load tasks |
| `/bnac-milestone status` | Show progress of active milestone |
| `/bnac-milestone complete` | Complete active milestone, archive, activate next |
| `/bnac-milestone` (no action) | Defaults to `status` |

## Rules

- ONE active milestone at a time — finish or abort before starting another
- NEVER skip a milestone without explicit user approval
- ALWAYS archive completed milestone detail (don't delete)
- ALWAYS recommend quality gate before completion
- ALWAYS log milestone transitions
