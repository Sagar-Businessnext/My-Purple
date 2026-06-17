# Task Format Reference

Each atomic task in a milestone task plan is a **checkbox embedded inside the milestone `.md`** — not a separate file. Tasks are pickable and finishable in one developer session.

## On-disk shape

```
project/.claude/phases/phase-<N>-<slug>/
└── m<N>-<slug>.md      ← `## Tasks (todo list)` section contains the checklist
```

There is **no `tasks/` subfolder, no per-task `.md` file, no `INDEX.md` for tasks**. Every task is a `- [ ] M<N>.<i>` checkbox inside the milestone .md.

## Required fields per task

| Field | Required | Notes |
|---|---|---|
| `ID` | yes | `M<N>.<i>` — milestone ID + sequential within milestone (e.g., `M3.1`, `M3.2`). Resets per milestone. |
| `@agent` | yes (except final HUMAN REVIEW CHECKPOINT) | One of the agents in the milestone's `## Agents involved`. Format: `(@code-developer)` immediately after the bold ID. |
| `Title` | yes | One-line imperative — "Add login endpoint to `auth.controller.ts`" |
| `Files` | yes | Explicit file paths created or modified, on the line below the title |
| `Complexity` | yes | S / M / L (see `reference/complexity-tiers.md`); `—` for the HUMAN REVIEW CHECKPOINT |
| `Depends on` | yes | Prior task IDs, comma-separated, or `—` for none |
| `Steps` | optional | Indented sub-bullets for multi-step tasks (max ~5 steps before it should be split) |

## Task line format (canonical — follow exactly)

Each task is a `- [ ]` checkbox. The header is `**M<N>.<i>** (@agent) — <Title>`. Subsequent metadata lives on indented lines below the header.

```markdown
- [ ] **M<N>.1** (@architect) — <Design / interface / contract task>
       Files: `<exact paths>`
       Complexity: S · Depends on: —

- [ ] **M<N>.2** (@code-developer) — <Implementation task>
       Files: `<exact paths>`
       Complexity: S · Depends on: M<N>.1

- [ ] **M<N>.<i>** (@code-developer) — <Multi-step task>
       Files: `<exact paths>`
       Complexity: M · Depends on: M<N>.<j>
       Steps:
         1. <step>
         2. <step>

- [ ] **M<N>.<test>** (@test-engineer) — <Test work>
       Files: `<test paths>`
       Complexity: S · Depends on: M<N>.<j>

- [ ] **M<N>.<review>** (@code-reviewer) — Review SOLID, naming, structured logging
       Files: review-only (no code changes)
       Complexity: S · Depends on: M<N>.<test>

- [ ] **M<N>.<doc>** (@doc-writer) — Author README setup section
       Files: `README.md`
       Complexity: S · Depends on: M<N>.<j>

- [ ] **M<N>.<status>** (@status-manager) — Update milestone status, change log, progress tracking
       Files: `project/.claude/milestone-status.md`, `CHANGELOG.md`
       Complexity: S · Depends on: M<N>.<doc>

- [ ] **M<N>.<final>** — **HUMAN REVIEW CHECKPOINT** (gates milestone completion)
       Files: review-only
       Complexity: — · Depends on: M<N>.<status>

**Complexity mix:** <count>×S + <count>×M + <count>×L + 1×review  (matches "<small/medium/large> milestone" feel ✓)
```

Notes:
- Indent metadata lines with 7 spaces so they render as a continuation of the bullet under most Markdown renderers.
- Use `·` (middle dot) between metadata fields for readability.
- The `Complexity mix:` summary line is mandatory after the last task — it's a sanity-check artifact.

## Field rules

### ID
- `M<N>.<i>` — milestone ID + sequential.
- Don't reset across milestones — `M3.1` and `M4.1` are independent.
- Don't skip numbers when re-planning — `M3.1, M3.3` is forbidden. Renumber if needed.
- The HUMAN REVIEW CHECKPOINT takes the next sequential number (e.g., `M3.13`).

### @agent
- Pull from the milestone's `## Agents involved`. Conventional names:
  - `@architect`
  - `@code-developer`
  - `@test-engineer`
  - `@code-reviewer`
  - `@doc-writer`
  - `@status-manager`
  - `@security-auditor` (if engaged)
  - `@perf-optimizer` (if engaged)
  - `@devops-engineer` (if engaged)
- Every listed agent must own at least one task.
- The HUMAN REVIEW CHECKPOINT has **no** `@agent` — humans, not agents, close it.

### Title
- Imperative, one line. No "and" — split into a sibling task instead.
- Bad: "Login endpoint" (not imperative)
- Bad: "Implement authentication features" (too broad)
- Good: "Implement `POST /api/auth/login` endpoint"

### Files
- Exact relative paths from project root, on the line below the title (prefixed with `Files:`).
- Backtick-quote each path.
- One task = one cluster of related files. If files span unrelated modules, split.
- For review-only or human-review tasks: `Files: review-only (no code changes)`.

### Complexity
- S — < 4 hours, well-understood pattern
- M — 4 hours – 2 days, some unknowns
- L — > 2 days, significant unknowns or research
- See `reference/complexity-tiers.md` for signals.
- The HUMAN REVIEW CHECKPOINT uses `—`.

### Depends on
- Comma-separated task IDs — `M3.1, M3.2`.
- `—` for none.
- A task can depend on tasks in earlier milestones — `M2.5` is valid as a dependency.

### Steps (optional)
- Use when the task has more than one moving part inside a single agent's session.
- Max ~5 steps; if you have more, split the task.

## Verification map (mandatory section)

Append directly after `## Tasks (todo list)`:

```markdown
## Verification map
Every condition in M<N>'s acceptance test must trace to ≥1 task.

| Acceptance test condition                       | Tasks verifying it     |
|--------------------------------------------------|------------------------|
| <condition derived from acceptance test>        | M<N>.<a>, M<N>.<b>     |
| <condition>                                     | M<N>.<c>               |
| Human reviewer approves                         | M<N>.<final>           |
```

Every line in the milestone's `## Acceptance criteria` checklist (or the conditions inside the acceptance test) must appear as a row. The HUMAN REVIEW CHECKPOINT row is mandatory.

## Anti-patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| Creating per-task `.md` files in a `tasks/` folder | Breaks the embedded-tasks shape | Tasks live inside the milestone `.md` as a checklist |
| Task without explicit file paths | Developer has to guess scope | List exact paths |
| Task "implement X feature" | Not atomic; not finishable in one session | Decompose into create/modify/test tasks |
| 20+ tasks in one milestone | Milestone is too broad | Re-run `bnac-milestone-planner` to split |
| All tasks marked S | Probably wrong; check complexity signals | Re-evaluate per `complexity-tiers.md` |
| Circular dependencies (`M3.1` depends on `M3.2` which depends on `M3.1`) | Impossible to schedule | Refactor task boundaries |
| Acceptance test condition with no corresponding task | Milestone can't pass | Add the missing task or fix the acceptance test |
| Research task with no output file | Research finishes in someone's head; nobody else benefits | Add an output deliverable (notes file, decision record) |
| Missing `@agent` on a non-review task | Self-routing breaks; nobody picks up the task | Add `@agent` |
| Missing HUMAN REVIEW CHECKPOINT | Milestone has no human gate | Always include the final task with no `@agent` |
| Missing `Complexity mix:` summary line | Sum check skipped | Append it after the last task |
| Missing `## Verification map` | Acceptance conditions untraceable | Append after `## Tasks (todo list)` |
