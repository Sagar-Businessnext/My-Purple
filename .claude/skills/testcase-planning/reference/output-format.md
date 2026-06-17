# Test Case Plan — Output Format

Used by `bnac-task-planner` when invoked via `/bnac-task-plan --lens testcase`.

## Document shape

```markdown
## Test Case Plan: <feature / area>

### Input
- Source: <PRD path / description / code path>
- Test framework: <detected from project — e.g., Jest, xUnit, pytest, flutter_test>

### Coverage Summary
| Area | Happy Path | Edge Cases | Error Cases | Total |
|------|-----------|------------|-------------|-------|
| ... | 3 | 2 | 2 | 7 |

### Test Cases

#### Area: <feature area name>

| # | ID | Scenario | Type | Steps | Expected Result | Priority |
|---|-----|----------|------|-------|-----------------|----------|
| 1 | TC-001 | Valid login with correct credentials | Happy | 1. Enter valid email 2. Enter valid password 3. Submit | Redirect to dashboard, JWT token set | P1 |
| 2 | TC-002 | Login with invalid password | Error | 1. Enter valid email 2. Enter wrong password 3. Submit | Show error message, no redirect | P1 |
| 3 | TC-003 | Login with empty fields | Edge | 1. Leave fields empty 2. Submit | Validation errors shown | P2 |

### Test Data Requirements
- Fixtures, mocks, seed data needed

### Dependencies
- External services to mock
- Database state required
- Auth tokens needed

### Notes
- Patterns to follow from existing tests
- Framework-specific considerations
```

## Test case types

| Type | Meaning |
|------|---------|
| **Happy** | Normal flow, expected inputs, successful outcome |
| **Edge** | Boundary values, empty inputs, max lengths, special characters, unicode, off-by-one |
| **Error** | Invalid inputs, network failures, permission denied, timeouts, missing prerequisites |
| **Security** | Injection (SQL/XSS/command), auth bypass, privilege escalation, sensitive data exposure |
| **Performance** | Load, large datasets, concurrent access, memory pressure |

## Priority levels

| Priority | Meaning |
|----------|---------|
| **P1** | Must have — core functionality, blocks release if failing |
| **P2** | Should have — important scenarios, likely to catch real bugs |
| **P3** | Nice to have — rare edge cases, minor improvements |

## ID convention

- `TC-<NNN>` — globally sequential within a plan
- Don't reset across areas; one area's TC-007 and another's TC-008 must be unique
- When re-planning, do not skip numbers — renumber if needed

## Field rules

### Scenario
- One imperative line.
- Bad: "Login test" (not a scenario)
- Good: "Login with expired JWT returns 401"

### Steps
- Numbered, terse, actionable.
- Each step is observable from outside the system (UI action, API call, DB state).

### Expected Result
- Concrete, observable. Not "works correctly".
- Good: "Response 200 with `{ token: <jwt> }`; cookie `session` set with HttpOnly + Secure"

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Scenario = "test X works" | Specify input + outcome explicitly |
| Expected result = "no error" | State what the system should return / display |
| Only Happy cases | Add at least one Edge and one Error per area |
| 100% P1 | Prioritize honestly; everything-is-critical = nothing-is-critical |
| No test data section | Always include — fixtures and mocks make the plan executable |
