# Documentation Plan — Output Format

Used by `bnac-task-planner` when invoked via `/bnac-task-plan --lens doc`.

## Document shape

```markdown
## Documentation Plan: <scope>

### Input
- Source: <PRD path / code path / description>
- Existing docs: <list of current documentation files>

### Documentation Inventory

#### Existing (review / update)
| Doc | Path | Status | Action Needed |
|-----|------|--------|---------------|
| README | `README.md` | Outdated | Update setup instructions for v2 |
| API docs | `docs/api.md` | Missing sections | Add new endpoints from M5 |

#### New (create)
| Doc | Path | Audience | Priority |
|-----|------|----------|----------|
| Getting Started | `docs/getting-started.md` | New developers | P1 |
| API Reference | `docs/api-reference.md` | API consumers | P1 |
| Architecture | `docs/architecture.md` | Team / new hires | P2 |
| Contributing | `CONTRIBUTING.md` | External contributors | P3 |

### Content Outlines

#### <Doc Name> (`<path>`)
**Audience:** <who reads this>
**Purpose:** <what they need to learn / accomplish>

1. Section 1 — <what to cover>
2. Section 2 — <what to cover>
3. Section 3 — <what to cover>

*Key content to include:*
- <specific thing from code / PRD>
- <specific thing from code / PRD>

### Implementation Tasks
| # | Task | Files | Depends On | Complexity |
|---|------|-------|------------|------------|
| 1 | Update README setup section | `README.md` | — | S |
| 2 | Write Getting Started guide | `docs/getting-started.md` | — | M |
| 3 | Document API endpoints | `docs/api-reference.md` | — | L |
| 4 | Write architecture overview | `docs/architecture.md` | 1 | M |

### Style Guidelines
- Follow existing doc patterns in the project
- Code examples must be runnable and tested
- Keep language concise and scannable
- Use the project's terminology consistently (check `glossary.md` if present)
```

## Documentation types

| Type | Audience | Purpose |
|------|----------|---------|
| **README** | Everyone | First impression, setup, quick start |
| **Getting Started** | New developers | Step-by-step onboarding to first running build |
| **API Reference** | Consumers | Endpoint / function / class documentation |
| **Architecture** | Team | System design, key decisions, patterns |
| **Contributing** | Contributors | How to contribute, conventions, PR process |
| **Changelog** | Users | What changed per version (see `bnac-changelog-agent`) |
| **Runbook** | Ops / oncall | How to deploy, monitor, troubleshoot, roll back |
| **ADR** | Team | Architecture Decision Records — frozen-in-time decisions |

## Audience matrix

| Audience | Cares about | Skips |
|---|---|---|
| **New developer** | Setup, first running build, where to find things | Architecture rationale, deep internals |
| **External contributor** | How to fork, run tests, submit PR | Internal team rituals |
| **API consumer** | Endpoints, request/response, auth, errors | Internal architecture |
| **Ops / oncall** | Deploy, rollback, alerts, runbook for known incidents | Implementation details |
| **Team / new hire** | Architecture, key decisions, why-not-X | Setup (they have a buddy) |
| **End user** | What's new (changelog), how to use features | Anything technical |

## Field rules

### Inventory
- Always include the existing-docs section — even if empty (write "none found")
- "Status" = current / outdated / missing-sections / stale / wrong
- "Action Needed" must be specific and actionable

### Content Outlines
- 3–7 bullets per doc. Outside this range = re-shape (split or merge).
- Each bullet = one section heading the writer will produce.

### Implementation Tasks
- Use `task-estimation` skill rules for complexity and file paths.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| No audience specified | Always declare — "everyone" is not an audience |
| Plan to rewrite README without listing what's currently there | Inventory first, gap-fill second |
| Content outline = "introduction, body, conclusion" | Specify actual section topics |
| Doc plan with no priority | P1 / P2 / P3 — be honest |
| 20-section doc | Split into multiple docs, each with one audience |
