# Milestone Format Reference

Every milestone document follows this structure. The milestone is the unit of project tracking — `bnac-milestone-tracker` activates / completes / reports on milestones using this shape.

## On-disk shape

Milestone `.md` files sit **flat** inside the phase folder. There is **no `milestones/` subfolder** and there are **no separate task files** — atomic tasks live inside this same `.md` as a checklist after `/bnac-task-plan` runs.

```
project/.claude/phases/phase-<N>-<slug>/
├── index.md
├── m<a>-<slug>.md         ← this format applies
└── m<b>-<slug>.md
```

## Required fields

| Field | Required | Notes |
|---|---|---|
| `# M<N>: <Title>` | yes | Heading — integer ID + descriptive title (globally numbered) |
| `Phase` | yes | `phase-<N>-<slug>` (or "none" if project has no phases) |
| `Status` | yes | `Not Started` (default) → `In Progress` → `Review Pending` → `Approved` |
| `Goal` | yes | One-sentence outcome |
| `Acceptance test` | yes | Single objective condition (see `reference/acceptance-tests.md`) |
| `Estimated tasks` | yes | Count or range, plus the human review checkpoint |
| `Depends on` | yes | Prior milestone IDs or "none" |
| `Agents involved` | yes | Per-agent role bullets for this milestone |
| `High-level tasks` | yes | Table of task title + type + complexity (5–8 rows) |
| `Tasks (todo list)` | yes | Placeholder section — `/bnac-task-plan` fills it |
| `Deliverables` | yes | Files or artifacts produced |
| `Acceptance criteria` | yes | Observable checklist items derived from the acceptance test |
| `Dependencies` | yes | Prose statement of dependency on prior milestones |
| `Definition of Done` | yes | Checklist (standard items + milestone-specific + human review) |
| `Risks` | yes | Bullet list — risk → mitigation |

## Scope filter (NON-NEGOTIABLE)

The milestone is shaped by the `--scope` flag on `/bnac-milestone-plan` (default `code`). Lines tagged `[code]`, `[test]`, `[doc]` are emitted **only when that value is in the resolved scope set**. Lines tagged `[any]` are always emitted.

| Scope value (resolved set member) | Adds these lines / rows / agents                                                                                          |
|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| `code` (always default)           | Architect / Code Developer / Code Reviewer / Status Manager agents; `create`/`modify`/`configure`/`migrate`/`research` rows; "Quality gate clean" + "Activity log entries" DoD lines. |
| `test`                            | Test Engineer Agent; `test` rows; "Acceptance test passes" / "Tests pass" / "Test coverage" DoD lines.                    |
| `doc`                             | Documentation Writer Agent; `docs` rows; "Documentation updated" DoD line.                                                |
| (any)                             | "Human reviewer approves milestone" — always included regardless of scope.                                                |

**When scope = `code` only (the default), the milestone .md MUST NOT contain any `[test]` or `[doc]` lines.** Do not include Test Engineer Agent, Documentation Writer Agent, doc/test high-level rows, "Tests pass", or "Documentation updated" — those belong to other scopes.

Do not include the bracket tags in the final file output — they are guidance for which lines apply.

## Field rules

### Status
- Five states: `Not Started`, `In Progress`, `Review Pending`, `Approved`, (`Blocked` allowed transiently).
- `bnac-milestone-planner` writes `Not Started`. Status transitions are owned by `bnac-milestone-tracker` (and the Status Manager Agent).

### Goal
- One sentence. State the *outcome*.
- Bad: "Implement authentication"
- Good: "Users can sign in with email/password and stay logged in across sessions"

### Acceptance test
- Single objective condition. See `reference/acceptance-tests.md` for examples.
- Must be reproducible — script, curl command, test invocation, manual check with clear pass/fail.
- Bad: "Auth is solid"
- Good: "POST /api/auth/login returns 200 + JWT for valid credentials, 401 for invalid"

### Agents involved
- Use the conventional agent names (`Architect Agent`, `Code Developer Agent`, `Test Engineer Agent`, `Code Reviewer Agent`, `Documentation Writer Agent`, `Status Manager Agent`). Add `Security Auditor Agent`, `Perf Optimizer Agent`, `DevOps Engineer Agent` when relevant.
- One bullet per agent describing what they specifically do for THIS milestone (more concrete than the phase-level rollup).

### High-level tasks
- 5–8 rows is the sweet spot.
- "Type" column: `create / modify / configure / test / migrate / document / research`.
- "Complexity": S (< 1 day), M (1–3 days), L (3+ days). Pulled from the `task-estimation` skill.
- Don't write atomic-task detail here — that's `bnac-task-planner`'s job (and it lives inside `## Tasks (todo list)` further down).

### Tasks (todo list)
- This section is a **placeholder** when `bnac-milestone-planner` writes the file. Use this exact text:
  ```
  ## Tasks (todo list — populated by /bnac-task-plan)
  Scope: <resolved-scope, e.g., code>
  _(empty — `/bnac-task-plan M<N>` will fill this with the atomic checklist with @agent attribution and a final HUMAN REVIEW CHECKPOINT. It defaults to the Scope above; pass `--scope ...` to override.)_
  ```
- The `Scope:` line records the resolved scope set so `/bnac-task-plan` defaults to the same scope. Always emit it — for the default plan, it reads `Scope: code`.
- After `/bnac-task-plan` runs, this section contains `- [ ] M<N>.<i>` checkboxes.

### Deliverables
- Concrete files or artifacts the milestone produces. Used by `bnac-quality-gate` and reviewers to know what to check.

### Acceptance criteria — observable checklist
- Derived from the acceptance test — each line is one observable that, taken together, proves the test passes.
- Always include `- [ ] Human reviewer approves milestone` as the last item.

### Definition of Done — scope-filtered checklist
Always include `[any]` lines. Include `[test]` / `[doc]` lines only when their scope is in the resolved set.

- [ ] All atomic tasks complete (`- [x]` in the Tasks section)        [any]
- [ ] `bnac-quality-gate` runs clean (build / type / lint)            [any]
- [ ] Activity log entries for all tasks                              [any]
- [ ] Human review checkpoint approved                                [any]
- [ ] Acceptance test passes                                          [test]
- [ ] Tests pass                                                      [test]
- [ ] Documentation updated                                           [doc]

**Default (`--scope code`) emits only the `[any]` lines.** Do not include "Acceptance test passes", "Tests pass", or "Documentation updated" in a code-only milestone.

Add milestone-specific items as needed (always `[any]` unless they're inherently test/doc work):
- [ ] Migration script tested on staging data
- [ ] Security review passed (if auth/data milestone)
- [ ] Performance benchmark within target (if perf-sensitive)

### Depends on / Dependencies
- `Depends on:` (in the front-matter style header) is the comma-separated list of prior milestone IDs.
- `## Dependencies` is the prose section — same content, more readable. Use both.

### Risks
- Specific to this milestone.
- Format: `<Risk> → <mitigation>`.

## Template

Lines tagged `[code]`, `[test]`, `[doc]` are emitted only when in the resolved scope set. Lines tagged `[any]` are always emitted. **Do not include the bracket tags in the final file output.** A default `--scope code` plan strips every `[test]` and `[doc]` line.

```markdown
# M<N>: <Title>

**Phase:** phase-<N>-<slug>
**Status:** Not Started
**Goal:** <one-sentence outcome>
**Acceptance test:** <single objective condition>
**Estimated tasks:** <count or range> (+1 human review checkpoint)
**Depends on:** <prior milestone IDs, or "none">

## Agents involved
- **Architect Agent** — <role>                                         [code]
- **Code Developer Agent** — <role>                                    [code]
- **Code Reviewer Agent** — <role>                                     [code]
- **Status Manager Agent** — <role>                                    [code]
- **Test Engineer Agent** — <role>                                     [test]
- **Documentation Writer Agent** — <role>                              [doc]

## High-level tasks
| # | Task | Type | Complexity |
|---|------|------|------------|
| 1 | <title> | create / modify / configure / migrate / research | S / M / L |   [code]
| 2 | <title> | test                                              | S / M / L |   [test]
| 3 | <title> | docs                                              | S / M / L |   [doc]

## Tasks (todo list — populated by /bnac-task-plan)
Scope: <resolved-scope, e.g., code>
_(empty — `/bnac-task-plan M<N>` will fill this with the atomic checklist with @agent attribution and a final HUMAN REVIEW CHECKPOINT. It defaults to the Scope above; pass `--scope ...` to override.)_

## Deliverables
- <code artifact>                                                      [code]
- <test artifact, e.g., "src/foo/__tests__/foo.spec.ts">               [test]
- <doc artifact, e.g., "docs/foo/README.md">                           [doc]

## Acceptance criteria
- [ ] <observable code/behavior check>                                 [code]
- [ ] <test-coverage / regression check>                               [test]
- [ ] <doc presence / accuracy check>                                  [doc]
- [ ] Human reviewer approves milestone                                [any]

## Dependencies
- <prior milestone, or "None (first milestone in the phase)">

## Definition of Done
- [ ] All atomic tasks complete                                        [any]
- [ ] `bnac-quality-gate` runs clean                                   [any]
- [ ] Activity log entries for all tasks                               [any]
- [ ] Human review checkpoint approved                                 [any]
- [ ] Acceptance test passes                                           [test]
- [ ] Documentation updated                                            [doc]

## Risks
- <Risk> → <mitigation>
```

### What a default (`--scope code`) milestone looks like after filtering

```markdown
# M1: <Title>

**Phase:** phase-1-foundation
**Status:** Not Started
**Goal:** <one-sentence outcome>
**Acceptance test:** <single objective condition>
**Estimated tasks:** <count> (+1 human review checkpoint)
**Depends on:** none

## Agents involved
- **Architect Agent** — <role>
- **Code Developer Agent** — <role>
- **Code Reviewer Agent** — <role>
- **Status Manager Agent** — <role>

## High-level tasks
| # | Task    | Type     | Complexity |
|---|---------|----------|------------|
| 1 | <title> | create   | S          |
| 2 | <title> | modify   | S          |
| 3 | <title> | configure| M          |

## Tasks (todo list — populated by /bnac-task-plan)
Scope: code
_(empty — `/bnac-task-plan M1` will fill this with the atomic checklist with @agent attribution and a final HUMAN REVIEW CHECKPOINT. Defaults to `Scope: code`; pass `--scope ...` to override.)_

## Deliverables
- <code artifact>

## Acceptance criteria
- [ ] <observable code/behavior check>
- [ ] Human reviewer approves milestone

## Dependencies
- None (first milestone in the phase)

## Definition of Done
- [ ] All atomic tasks complete
- [ ] `bnac-quality-gate` runs clean
- [ ] Activity log entries for all tasks
- [ ] Human review checkpoint approved

## Risks
- <Risk> → <mitigation>
```

No Test Engineer Agent, no Documentation Writer Agent, no `test`/`docs` rows, no "Acceptance test passes" / "Documentation updated" DoD lines. That is the contract for `--scope code` (the default).

## Anti-patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| Multi-condition acceptance test | "Done" becomes ambiguous | Split into two milestones |
| Goal is an activity, not an outcome | Can't tell when it's done | Restate as outcome |
| 12 tasks in one milestone | Too broad — likely two milestones | Split |
| 2 tasks in one milestone | Too small — should be inside another milestone | Merge or convert to a single task in another milestone |
| Resetting milestone IDs per phase | Confuses tracking | Keep IDs project-globally numbered |
| Acceptance test = "all tasks checked" | Tautological — doesn't verify outcome | Write a real, observable condition |
| Missing `## Tasks (todo list)` placeholder | `/bnac-task-plan` has nothing to fill | Always include the placeholder section |
| Emitting `[test]` / `[doc]` lines when `--scope` doesn't include them | Default `code` plan becomes a code-plus-test-plus-doc plan and the user gets work they didn't ask for | Always filter by the resolved scope set; a default plan is code-only |
| Missing `Scope:` line under `## Tasks (todo list)` placeholder | `/bnac-task-plan` can't default to the same scope | Always emit `Scope: <resolved-scope>` (default: `Scope: code`) |
| Writing per-task `.md` files in a `tasks/` subfolder | Breaks the embedded-tasks shape | Tasks live inside this `.md` as a checklist |
| Putting milestone files under a `milestones/` subfolder | Breaks the flat shape | Files go directly in `phase-<N>-<slug>/` |
| Skipping `Status` field | Tracker can't transition state | Always include `**Status:** Not Started` |
| Skipping `Acceptance criteria` checklist | DoD has nothing to verify the acceptance test against | Derive observable boxes from the acceptance test |
