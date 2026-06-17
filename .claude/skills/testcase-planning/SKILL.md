---
name: testcase-planning
description: Output template for test case plans — PRD/feature/code → structured test cases with scenarios, expected results, and priority. Used by bnac-task-planner when invoked via /bnac-task-plan --lens testcase.
user-invocable: false
argument-hint: ""
---

Produce a structured test case plan from a PRD, feature description, or existing source code. Distinct from the generic task plan: a test case plan describes **what should be verified**, not what code to write — its readers are QA and product, not developers.

## Additional Resources

- [reference/output-format.md](reference/output-format.md) — full output document shape, test case types, priority levels

## Steps

1. **Read the source** — PRD / spec / source code
2. **Extract every requirement and acceptance criterion** from the PRD; or every code path and validation rule from source
3. **Glob existing tests** — discover the test framework and patterns already in use
4. **Categorize** test cases by feature area (logical grouping, not file structure)
5. **For each requirement / code path**, plan Happy + Edge + Error cases — and Security / Performance where relevant
6. **Assign priority** — P1 / P2 / P3 per `reference/output-format.md`
7. **Output** in the shape from `reference/output-format.md`

## Rules

- **Derive from requirements** — Every test case must trace back to a requirement, acceptance criterion, or code path. No vanity tests.
- **Cover all paths** — Happy, Edge, Error for every feature; Security and Performance where the domain warrants it.
- **Be specific** — "Test login" is useless. Specify the exact scenario, input, and expected output.
- **Prioritize by risk** — Critical paths and user-facing features are P1. Rare edge cases are P3.
- **Match project patterns** — If the project uses given/when/then naming, follow it. Don't introduce a new convention.
- **Test data is mandatory** — Every plan ends with what fixtures, mocks, and seed data are needed.
