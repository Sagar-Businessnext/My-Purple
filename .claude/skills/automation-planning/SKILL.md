---
name: automation-planning
description: Output template for test automation strategy — what to automate, framework, CI integration, and implementation tasks. Used by bnac-task-planner when invoked via /bnac-task-plan --lens automation.
user-invocable: false
argument-hint: ""
---

Produce a test automation strategy from a test plan, PRD, or code area. Distinct from the generic task plan: an automation plan decides **what to automate vs leave manual**, **which framework**, and **how it plugs into CI** — strategy, not just task list.

## Additional Resources

- [reference/output-format.md](reference/output-format.md) — full output document shape, automation pyramid, CI integration patterns

## Steps

1. **Read the source** — test plan, PRD, or code area
2. **Detect existing infrastructure** — Glob for CI configs (`.github/workflows/`, `azure-pipelines.yml`, `.gitlab-ci.yml`), test files, framework
3. **Read existing test files** — understand current patterns (assertion library, mocking style, fixtures)
4. **Categorize** what to automate (unit / integration / E2E) and what stays manual (visual regression, exploratory, accessibility audit)
5. **Decide on framework** — match existing infrastructure unless there is a strong reason to introduce a new one (justify in plan)
6. **Plan CI integration** — when each tier runs, what can parallelize, how failures are reported
7. **Decompose into implementation tasks** with files, complexity, dependencies (per `task-estimation` skill)
8. **Output** in the shape from `reference/output-format.md`

## Rules

- **Automate high-value first** — Prioritize tests that catch real bugs, not vanity coverage.
- **Match existing infrastructure** — Don't introduce a new framework if the project already has one. Justify if you must.
- **Fast feedback loop** — Unit first, E2E last. CI must fail fast.
- **Realistic scope** — Not everything needs automation. Manual testing has its place; declare it explicitly.
- **Maintainability over coverage** — 50 well-structured tests beat 200 brittle ones.
- **Manual list is mandatory** — Always declare what is NOT being automated and why; otherwise scope is implicit.
