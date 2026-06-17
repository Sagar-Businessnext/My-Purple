# Automation Plan — Output Format

Used by `bnac-task-planner` when invoked via `/bnac-task-plan --lens automation`.

## Document shape

```markdown
## Automation Plan: <scope>

### Input
- Source: <test plan path / PRD path / description>
- Current stack: <detected — language, framework, CI provider>

### Current State
- Test framework: <e.g., Jest, xUnit, pytest>
- Existing coverage: <summary of what's already automated>
- CI/CD: <current pipeline status — provider, triggers, runtime>

### Automation Strategy

#### What to Automate
| # | Area | Type | Framework | Priority | Reason |
|---|------|------|-----------|----------|--------|
| 1 | API endpoints | Integration | supertest + Jest | P1 | Core business logic, high change rate |
| 2 | Form validation | Unit | Jest + RTL | P1 | User-facing, frequent regressions |
| 3 | Auth flow | E2E | Playwright | P2 | Critical path, low-frequency change |

#### What Stays Manual
| Area | Reason |
|------|--------|
| Visual regression | Needs human eye for brand compliance |
| Accessibility audit | Requires assistive technology testing |
| Exploratory | Catches issues fixed-script tests miss |

### Test Infrastructure
- **Framework:** <recommended or existing>
- **Helpers to create:** <shared utilities, custom matchers, factories>
- **Fixtures / mocks:** <test data setup needed>
- **Environment:** <test DB, mock servers, env vars>

### CI/CD Integration
- **When to run:** <on PR / on merge / nightly / scheduled>
- **Pipeline steps:** <lint → unit → integration → E2E>
- **Parallelization:** <what can run in parallel — by suite, by file, by shard>
- **Reporting:** <coverage reports, failure notifications, flaky-test tracking>

### Implementation Tasks
| # | Task | Files | Depends On | Complexity |
|---|------|-------|------------|------------|
| 1 | Set up test infrastructure | `jest.config.ts`, `tests/setup.ts` | — | M |
| 2 | Create shared test utilities | `tests/utils/*` | 1 | S |
| 3 | Write unit tests for ... | `tests/unit/*` | 2 | M |
| 4 | Write integration tests for ... | `tests/integration/*` | 2 | L |
| 5 | Configure CI pipeline | `.github/workflows/test.yml` | 1 | M |

### Risks
- Risk 1: <concrete failure mode> → <mitigation>
- Risk 2: <concrete failure mode> → <mitigation>
```

## The automation pyramid

| Tier | Speed | Cost | Coverage | When to use |
|---|---|---|---|---|
| **Unit** | ms | low | narrow | Pure logic, validators, formatters, reducers |
| **Integration** | seconds | medium | wider | API + DB, service composition, hooks + components |
| **E2E** | minutes | high | broadest | Critical user journeys only — 5–10 max |

Pyramid shape: many unit tests → fewer integration tests → very few E2E tests. Inverted pyramid (E2E-heavy) is a smell.

## CI integration patterns

| Pattern | When |
|---|---|
| **Run on every PR** | Unit + integration. Must complete in < 10 min. |
| **Run on merge to main** | Full suite including E2E. Allowed to take longer. |
| **Run nightly** | Visual regression, performance, long-running E2E. |
| **Run on schedule (cron)** | Smoke tests against production / staging. |

## Field rules

### What to Automate
- "Reason" must be concrete: a real failure mode, a refactor risk, a high change rate.
- "Bad: "to improve quality" is not a reason. Good: "validators changed 8x last quarter; regressions caught manually 3x".

### What Stays Manual
- Always populate. Empty manual list = automation pretends to cover everything = false confidence.

### Implementation Tasks
- Use `task-estimation` skill rules for complexity and file paths.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Inverted pyramid (E2E-heavy) | Push tests down: unit / integration where possible |
| Empty manual list | Always declare what stays manual and why |
| New framework without justification | Match existing; justify only if a clear gap |
| CI step "run all tests" with no parallelization plan | Specify shards / matrix / parallel groups |
| Reason column = "improve quality" | State the concrete failure mode being prevented |
