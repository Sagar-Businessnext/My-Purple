---
name: feature-planning
description: Output template for feature implementation plans — PRD/description → goal, architecture decisions, risks, and atomic tasks. Used by bnac-task-planner when invoked via /bnac-task-plan --lens feature.
user-invocable: false
argument-hint: ""
---

Produce a feature implementation plan from a PRD or feature description. Distinct from the generic task plan: a feature plan adds **Goal**, **Architecture Decisions**, and **Risks** sections so a tech lead can review the approach before any code is written.

## Additional Resources

- [reference/output-format.md](reference/output-format.md) — full output document shape, section-by-section

## Steps

1. **Read the source** — PRD path, feature description, or referenced spec
2. **Map current code** — Glob the target area, Read 2–3 reference files for existing patterns
3. **Identify what to create vs modify** — group by file cluster
4. **Decompose into 5–15 atomic tasks** with files, complexity, dependencies (per `task-estimation` skill)
5. **Capture architecture decisions** — for each non-obvious choice, state the alternatives and why this one
6. **Capture risks** — what could break, with concrete mitigation
7. **Output** in the shape from `reference/output-format.md`

## Rules

- **Read before planning** — Never plan from assumptions. Glob and Read first.
- **Tasks must be atomic** — One verifiable result per task. Use `task-estimation` skill rules.
- **Architecture decisions are explicit** — If you picked Approach X over Y, name Y and the reason.
- **Risks are actionable** — "Performance" is not a risk. "JSON parser is single-threaded; serializing 10MB payloads will block the event loop" is a risk.
- **Out-of-scope is mandatory** — Always list what was considered and excluded, so the plan is unambiguous.
- **Follow existing patterns** — Plan code that fits the project's conventions; do not introduce new patterns silently.
