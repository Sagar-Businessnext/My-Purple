---
name: phase-template
description: Canonical structure for project phases — number-ID, goal, single objective exit criterion, agents-involved rollup, quality gates, cross-milestone agent rollup, and globally-numbered milestone allocation. Used by bnac-phase-planner to break a large project into phase-1, phase-2, ...
user-invocable: false
argument-hint: ""
---

Define the canonical shape of a phase: a numeric ID (`phase-1`, `phase-2`, …), a one-sentence goal, a single objective exit criterion, an agents-involved rollup, a quality gates checklist, a cross-milestone agent rollup, and a list of globally-numbered milestones contained within.

## Additional Resources

- [reference/phase-format.md](reference/phase-format.md) — phase document structure and required fields
- [reference/phase-naming.md](reference/phase-naming.md) — phase ID conventions, common phase patterns by project type

## On-disk shape (NON-NEGOTIABLE)

```
project/.claude/phases/phase-<N>-<slug>/
└── index.md                ← the phase plan (this skill defines its shape)
```

There is **no `milestones/` subfolder**. Milestone files (`m<N>-<slug>.md`) sit flat inside the phase folder once `/bnac-milestone-plan` runs.

## Format

```markdown
# Phase <N>: <Title>

**Goal:** <one-sentence outcome of this phase>
**Exit criterion:** <single objective testable condition>
                   AND every milestone in this phase is `Approved`
                   AND every agent listed below has signed off across all milestones.
**Estimated milestones:** <count or range, e.g., "3–5">
**Depends on:** <prior phase IDs, or "none">

## Agents involved (rolled up across milestones in this phase)
- **@architect** — <role>
- **@code-developer** — <role>
- **@test-engineer** — <role + coverage target>
- **@code-reviewer** — <role>
- **@doc-writer** — <role>
- **@status-manager** — <role>
- (add @security-auditor / @perf-optimizer / @devops-engineer if engaged)

## Milestones in this phase
| ID | Title                   | File                          | Status        | Estimated tasks |
|----|-------------------------|-------------------------------|---------------|-----------------|
| M<a> | <title>               | m<a>-<slug>.md                | Not Started   | <range>         |
| M<b> | <title>               | m<b>-<slug>.md                | Not Started   | <range>         |

## Quality gates (apply across every milestone in the phase)
- [ ] All tests pass (per-milestone)
- [ ] Coverage ≥ 80 %
- [ ] Lint passes
- [ ] Type checking passes
- [ ] No secrets in code
- [ ] All public functions have doc comments
- [ ] Activity log entries for every task closure

## Cross-milestone agent rollup (all must be ✓ before phase is `Approved`)
| Agent             | Per-milestone duty                 | Phase-exit sign-off                                          |
|-------------------|------------------------------------|--------------------------------------------------------------|
| @architect        | Design review per milestone        | All interfaces + base classes match SOLID at phase boundary  |
| @code-reviewer    | PR review per milestone            | Final phase-wide SOLID + naming + pattern audit              |
| @test-engineer    | ≥ 80 % coverage per milestone      | Phase-wide coverage report ≥ 80 %; integration suite green   |
| @doc-writer       | README + docstring per milestone   | Architecture docs cover all phase deliverables               |
| @status-manager   | Status update per milestone        | Phase status flipped to `Approved` in `phases/index.md`      |

## Risks specific to this phase
- <Risk → mitigation>

## Out of scope (deferred to later phases)
- <Item → which phase picks it up>
```

## Example

```
# Phase 1: Foundation

**Goal:** Project scaffold, CI green, baseline tests passing.
**Exit criterion:** `bnac-quality-gate` runs clean on a hello-world deployment to staging
                   AND every milestone in this phase is `Approved`
                   AND every agent listed below has signed off across all milestones.
**Estimated milestones:** 3
**Depends on:** none

## Milestones in this phase
| ID | Title                   | File                          | Status        | Estimated tasks |
|----|-------------------------|-------------------------------|---------------|-----------------|
| M1 | Service scaffold        | m1-service-scaffold.md        | Not Started   | 5–8             |
| M2 | DB + migration baseline | m2-db-migration-baseline.md   | Not Started   | 4–6             |
| M3 | CI pipeline             | m3-ci-pipeline.md             | Not Started   | 5–7             |
```

## Rules

- **Phase IDs are numbers, milestone IDs are integers** — `Phase 1`, `M1`, `M2`. Don't use letters.
- **One sentence per goal** — Multi-sentence goals indicate the phase is too broad.
- **Exit criterion must be objectively testable** — "auth feels good" is not an exit criterion. "All UCs in Section 04 produce green tests" is.
- **Phases are vertical slices** — Each phase delivers something testable end-to-end. No phase exists only to "set up" for the next.
- **No more than 8 phases** — If you need more, the project should split into multiple projects.
- **Phase 1 is always Foundation** — Every project's first phase is the buildable, testable scaffold.
- **Milestones are globally numbered** — `M1, M2, M3` go in `phase-1`; `M4, M5` go in `phase-2`. Never reset to `M1` per phase.
- **Per-milestone duty ≠ phase-exit sign-off** — The cross-milestone rollup table makes both columns explicit. An agent can close milestone work yet still owe a phase-wide audit.
- **No `milestones/` subfolder** — Milestone `.md` files live flat inside the phase folder.
