---
name: task-estimation
description: Patterns for breaking a milestone into atomic tasks and assigning complexity (S/M/L), `@agent` attribution, and dependencies. Tasks are EMBEDDED inside the milestone `.md` as a `## Tasks (todo list)` checklist — there are no separate task files. Used by bnac-task-planner.
user-invocable: false
argument-hint: ""
---

Decompose a milestone's high-level task list into atomic tasks. Each task names exact files, depends on prior tasks explicitly, gets a complexity tier (S/M/L) based on observable signals, and carries an `@agent` attribution so the milestone is self-routing. Tasks live as `- [ ] M<N>.<i>` checkboxes inside the same milestone `.md` — they are not separate files.

## Additional Resources

- [reference/task-format.md](reference/task-format.md) — task line structure, required fields per task, verification-map shape
- [reference/complexity-tiers.md](reference/complexity-tiers.md) — S / M / L complexity definitions and signals

## On-disk shape (NON-NEGOTIABLE)

```
project/.claude/phases/phase-<N>-<slug>/
└── m<N>-<slug>.md      ← edited by bnac-task-planner: ## Tasks (todo list) filled, ## Verification map appended
```

**No `tasks/` subfolder. No per-task `.md` files.** Every atomic task is a checkbox inside the milestone `.md`.

## Steps

1. **Read the milestone** — extract `## Agents involved`, the `## High-level tasks` table, the acceptance test, and the `## Acceptance criteria` checklist.
2. **Decompose each high-level task** into atomic tasks:
   - One verifiable unit of work per task
   - Each touches a specific set of files
   - Each is something a developer can pick up and finish in one session
3. **Assign `@agent` attribution** — pull from the milestone's `## Agents involved`. Conventional names: `@architect`, `@code-developer`, `@test-engineer`, `@code-reviewer`, `@doc-writer`, `@status-manager`, `@security-auditor`, `@perf-optimizer`, `@devops-engineer`. Every listed agent must own at least one task.
4. **Assign complexity** using `reference/complexity-tiers.md`:
   - S — < 4 hours, well-understood pattern
   - M — 4 hours – 2 days, some unknowns
   - L — > 2 days, significant unknowns or research
5. **Map dependencies** — which tasks must complete before this one starts (intra-milestone or cross-milestone).
6. **Add a final HUMAN REVIEW CHECKPOINT** — last task ID `M<N>.<final>`, no `@agent`, depends on the last work task, gates milestone completion.
7. **Verify against acceptance criteria** — every box in `## Acceptance criteria` (or condition derived from the acceptance test) must trace to ≥1 task.
8. **Edit the milestone `.md`:**
   - Replace the `## Tasks (todo list)` placeholder with the filled checklist (using the format in `reference/task-format.md`)
   - Append `## Verification map` after `## Tasks (todo list)`

## Rules

- **One verifiable unit per task** — If the task description has "and", split it.
- **Files are explicit** — "Add login endpoint to `src/api/auth.controller.ts`" — not "add login endpoint".
- **`@agent` attribution mandatory** — Every non-review task names exactly one `@agent`. Only the HUMAN REVIEW CHECKPOINT has no `@agent`.
- **Complexity is a signal, not a contract** — S/M/L is for relative sizing. Don't try to convert to hours / days at the task level.
- **Dependencies are atomic** — Task 5 depends on tasks 2 and 3 — list both explicitly with task IDs.
- **Sum check** — Sum of task complexities should match the milestone's overall feel. 8 S-tasks for a milestone marked Large is suspicious.
- **No "research" tasks without an output file** — If the task is "investigate X", state where the findings will be recorded.
- **No separate task files** — Tasks are checkboxes inside the milestone `.md`. Anyone creating a `tasks/` folder is doing it wrong.
- **Task IDs reset per milestone** — `M3.1, M3.2, …` and `M4.1, M4.2, …` are independent.
