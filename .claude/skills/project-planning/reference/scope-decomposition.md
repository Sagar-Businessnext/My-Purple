# Scope Decomposition — Sizing Signals

How `bnac-planner` decides whether a project needs phases, milestones, or just tasks.

## Sizing tiers

| Tier | Milestones | Duration | Phases? | Lower planners to use |
|---|---|---|---|---|
| **Small** | < 5 | < 1 month | No | `bnac-task-planner` directly |
| **Medium** | 5–15 | 1–3 months | No | `bnac-milestone-planner` → `bnac-task-planner` |
| **Large** | > 15 | > 3 months | Yes | `bnac-phase-planner` → `bnac-milestone-planner` → `bnac-task-planner` |

## Signals to read

Evaluate every signal — even a small project with one large signal often needs medium-tier treatment.

### Scope size signals

| Signal | Small | Medium | Large |
|---|---|---|---|
| Distinct user stories / use cases | < 10 | 10–40 | > 40 |
| Entities / data models | < 5 | 5–15 | > 15 |
| Integrations (external systems) | 0–1 | 2–5 | > 5 |
| Tech stacks involved | 1 | 1–2 | > 2 |
| Stakeholder groups | 1 | 2–3 | > 3 |

### Risk signals (force a tier upgrade)

Any of these pushes a project up one tier:

- **Cross-team dependency** — work blocked on another team's deliverable
- **Compliance / regulatory deadline** — fixed external date
- **Migration of existing system** — any "rewrite" or "lift-and-shift"
- **New stack the team has not shipped before** — learning curve risk
- **Multi-region rollout** — staged delivery requires phasing
- **Public release / press milestone** — visibility raises the bar for verification

### Anti-signals (allow tier downgrade)

These pull a project down a tier:

- **Internal-only tool** — no external commitment
- **Pure refactor of stable code** — well-understood territory
- **Automation script / one-off CLI** — no UI, no users, finite scope

## Decision procedure

1. Score scope-size signals (count how many are at each tier)
2. Apply risk signals (each one bumps up by one tier; cap at large)
3. Apply anti-signals (each one drops by one tier; floor at small)
4. The resulting tier is the project's shape

## Worked examples

### Example 1: small
- 6 use cases, 3 entities, 1 integration, single stack — all small
- No risk signals
- One anti-signal: internal CLI tool
- **Result:** Small → tasks only via `bnac-task-planner`

### Example 2: medium
- 22 use cases, 8 entities, 3 integrations — all medium
- No risk signals
- No anti-signals
- **Result:** Medium → milestones via `bnac-milestone-planner` → tasks

### Example 3: large
- 12 use cases, 4 entities (medium) but
- 4 integrations, 2 stacks (medium edge)
- 2 risk signals: compliance deadline + new stack
- **Result:** Medium → bumped twice to Large (capped). Phases via `bnac-phase-planner` → milestones → tasks.

### Example 4: edge case
- 30 use cases, 12 entities — medium
- 1 risk signal (cross-team dep)
- 0 anti-signals
- **Result:** Medium → bumped to Large. Use phases.

## Common mistakes

| Mistake | Why it's wrong | Fix |
|---|---|---|
| Skipping phases on a large project | Loses the project's natural rhythm; milestones become incoherent without phase grouping | If > 15 milestones, force phases |
| Using phases on a small project | Adds ceremony without value | If < 5 milestones, no phases |
| Sizing by team size, not scope size | A team of 10 doesn't change the project's intrinsic complexity | Size on scope; team affects schedule, not shape |
| Ignoring risk signals | "This is just a CRUD app" + new stack = surprise blowup | Always apply risk signals |
