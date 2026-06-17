# Phase Format Reference

Every phase document follows this structure. The phase document is the source of truth for a phase's goal and exit criterion; milestones inside it are referenced by ID and live as **flat `m<N>-<slug>.md` files in the same folder** (no `milestones/` subfolder).

## On-disk shape

```
project/.claude/phases/phase-<N>-<slug>/
├── index.md                 ← the phase plan (this format applies)
├── m<a>-<slug>.md           ← milestone (written by /bnac-milestone-plan)
└── m<b>-<slug>.md
```

## Required fields

| Field | Required | Notes |
|---|---|---|
| `# Phase <N>: <Title>` | yes | Heading — number ID + descriptive title |
| `Goal` | yes | One sentence — what "done" looks like |
| `Exit criterion` | yes | Single objectively testable condition (compound with `AND every milestone … Approved AND every agent … signed off`) |
| `Estimated milestones` | yes | Count or range (e.g., "3", "3–5") |
| `Depends on` | yes | Prior phase IDs or "none" |
| `Agents involved` | yes | Per-agent role rollup across milestones in the phase |
| `Milestones in this phase` table | yes | List of milestone IDs + titles + filenames + status + estimated task counts |
| `Quality gates` checklist | yes | Per-milestone gates that must hold across every milestone |
| `Cross-milestone agent rollup` table | yes | Per-milestone duty + phase-exit sign-off, per agent |
| `Risks specific to this phase` | yes | Bullet list — risk → mitigation |
| `Out of scope` | optional | Items deferred and which phase picks them up |

## Field rules

### Goal
- **One sentence.** If you need two, split the phase.
- Active voice. "Foundation laid: scaffold, CI, tests passing" — not "The foundation will be set up."
- States the *outcome*, not the *activity*. "User auth working in staging" — not "Build user auth."

### Exit criterion
- A single, *objectively testable* condition, compounded with the standard tail:
  `AND every milestone in this phase is Approved AND every agent listed below has signed off across all milestones.`
- The lead condition can be verified by a script, CI run, or `bnac-quality-gate`.
- Bad: "Authentication is solid", "Performance is acceptable", "Code is clean."
- Good: "All UCs in PRD Section 04 pass automated tests", "P95 latency < 200ms on staging", "0 critical findings from `/bnac-code-review`".

### Estimated milestones
- Use a range when uncertain (`3–5`).
- Pin to a number once `bnac-milestone-planner` has run.

### Depends on
- List previous phase IDs that must complete before this phase starts.
- `phase-1` always says `none`.
- Cross-phase parallelism is OK — but state it explicitly.

### Agents involved
- Use the conventional `@agent` names: `@architect`, `@code-developer`, `@test-engineer`, `@code-reviewer`, `@doc-writer`, `@status-manager`. Add `@security-auditor`, `@perf-optimizer`, `@devops-engineer` when in scope.
- One bullet per agent with their phase-wide responsibility.

### Milestones table
- IDs continue across phases — `M1, M2, M3` go in `phase-1`; `M4, M5` go in `phase-2`.
- Don't reset to `M1` per phase. Milestones are project-globally numbered.
- `File` column names the future `m<N>-<slug>.md` flat in this folder.
- `Status` defaults to `Not Started` and progresses through `In Progress → Review Pending → Approved`.

### Quality gates
- A standard checklist that applies to every milestone in the phase: tests, coverage, lint, type check, no secrets, doc comments, activity log entries.
- Each box flips to `- [x]` only after every milestone in the phase has met it.

### Cross-milestone agent rollup
- One row per agent.
- `Per-milestone duty` describes what the agent closes inside each milestone (e.g., PR review).
- `Phase-exit sign-off` describes the phase-wide audit that gates `Approved` (e.g., final SOLID + naming sweep across all M-files).
- Both columns are required — they are different work.

### Risks
- Specific to this phase. Project-wide risks belong in the top-level plan.
- Format: `<Risk> → <mitigation>` — both halves required.

### Out of scope
- Optional but recommended for any phase with ambiguous boundaries.
- Format: `<Item> → <phase that picks it up>`. Nothing is "out of scope forever" — name where it goes, or argue for cutting it.

## Template

```markdown
# Phase <N>: <Title>

**Goal:** <one sentence — outcome, not activity>
**Exit criterion:** <one testable condition>
                   AND every milestone in this phase is `Approved`
                   AND every agent listed below has signed off across all milestones.
**Estimated milestones:** <count or range>
**Depends on:** <prior phase IDs, or "none">

## Agents involved (rolled up across milestones in this phase)
- **@architect** — <role>
- **@code-developer** — <role>
- **@test-engineer** — <role + coverage target>
- **@code-reviewer** — <role>
- **@doc-writer** — <role>
- **@status-manager** — <role>

## Milestones in this phase
| ID | Title | File | Status | Estimated tasks |
|----|-------|------|--------|-----------------|
| M<n> | <one-line title> | m<n>-<slug>.md | Not Started | <count or range> |

## Quality gates (apply across every milestone in the phase)
- [ ] All tests pass
- [ ] Coverage ≥ 80 %
- [ ] Lint passes
- [ ] Type checking passes
- [ ] No secrets in code
- [ ] All public functions have doc comments
- [ ] Activity log entries for every task closure

## Cross-milestone agent rollup (all must be ✓ before phase is `Approved`)
| Agent | Per-milestone duty | Phase-exit sign-off |
|-------|--------------------|---------------------|
| @architect | Design review per milestone | Phase-wide SOLID + interface design audit |
| @code-reviewer | PR review per milestone | Phase-wide SOLID + naming + pattern audit |
| @test-engineer | ≥ 80 % coverage per milestone | Phase-wide coverage report ≥ 80 % |
| @doc-writer | README + docstring per milestone | Architecture docs cover all phase deliverables |
| @status-manager | Status update per milestone | Phase status flipped to Approved |

## Risks specific to this phase
- <Risk> → <mitigation>

## Out of scope (deferred)
- <Item> → <which phase picks it up>
```

## Anti-patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| Phase with no exit criterion | Can't tell when it's done | Add an objectively testable condition |
| "Setup" phase that doesn't ship anything | Pure ceremony; project stalls | Combine with first deliverable phase |
| 12-phase project | Too many — likely small phases that are really milestones | Roll up into 4–6 phases |
| Phase boundaries shift mid-project | Initial sizing was wrong | Re-run `bnac-planner` to re-size |
| Milestone numbers reset per phase | Confuses tracking; same M1 means different things | Keep milestone IDs globally numbered |
| Letter phase IDs (`Phase A`, `Phase B`) | Old convention | Use number IDs (`Phase 1`, `Phase 2`) |
| Missing cross-milestone agent rollup | Phase appears complete but agents owe phase-wide audits | Always include both per-milestone duty + phase-exit sign-off columns |
| Creating a `milestones/` subfolder | Breaks the flat shape | Milestone .md files sit flat in the phase folder |
