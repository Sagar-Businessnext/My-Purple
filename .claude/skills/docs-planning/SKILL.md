---
name: docs-planning
description: Output template for documentation plans — code/PRD → doc inventory, audience, content outline, and implementation tasks. Used by bnac-task-planner when invoked via /bnac-task-plan --lens doc.
user-invocable: false
argument-hint: ""
---

Produce a documentation plan from a PRD, source code, or scope description. Distinct from the generic task plan: a docs plan first decides **which documents are needed**, **for whom**, and **what content goes in each** — content strategy, not just task list.

## Additional Resources

- [reference/output-format.md](reference/output-format.md) — full output document shape, doc types, audience matrix

## Steps

1. **Read the source** — PRD / spec / code path
2. **Inventory existing docs** — Glob for `README.md`, `docs/`, `CONTRIBUTING.md`, JSDoc / docstrings
3. **Read source code** — public APIs, components, exported symbols (Grep for `export`, public methods, route handlers)
4. **Identify gaps** — what's missing, what's outdated, what's stale
5. **For each doc**, identify: audience, purpose, content outline (3–7 bullets)
6. **Decompose into implementation tasks** with files, complexity, dependencies (per `task-estimation` skill)
7. **Output** in the shape from `reference/output-format.md`

## Rules

- **Audience first** — Every doc has a reader. Write for them, not for completeness.
- **Gaps over rewrites** — Identify what's missing before rewriting what exists.
- **Code is the truth** — Docs must reflect actual code, not aspirational design.
- **Scannable** — Headings, tables, code blocks. Nobody reads walls of text.
- **Maintainable** — Prefer auto-generated API docs over hand-written ones where possible.
- **Existing docs are inventoried, not silently overwritten** — Always list current docs and call out which are outdated, before proposing new ones.
