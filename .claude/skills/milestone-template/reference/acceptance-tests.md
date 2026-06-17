# Writing Milestone Acceptance Tests

A milestone's acceptance test is the *single, objective condition* that proves "done." It's the difference between a milestone you can track and one that drifts.

## Properties of a good acceptance test

| Property | Meaning |
|---|---|
| **Single condition** | One thing to verify. If you need "and" between conditions, split the milestone. |
| **Objective** | Two people would agree on pass/fail without discussion. |
| **Reproducible** | Can be re-run later (in CI, by a reviewer, by the milestone-tracker). |
| **Outcome-oriented** | Tests what users / consumers experience, not internal implementation. |
| **Bounded** | Has a clear stopping point. Not "performance is good" but "P95 < 200ms". |

## Acceptance test shapes

### Shape 1: API behavior

```
POST /api/auth/login with {"email":"x@y.com","password":"valid"}
  → 200 + JSON body containing `token`
POST /api/auth/login with {"email":"x@y.com","password":"wrong"}
  → 401 + error JSON
```

### Shape 2: UI behavior

```
On the dashboard page, clicking "Add widget" opens a modal with
  name + type fields. Submitting valid input adds a widget card to
  the dashboard within 2 seconds.
```

### Shape 3: Data condition

```
After running the migration script, every row in `users` has a
  non-null `created_at` matching the original `signup_date` value
  (or `2020-01-01` if `signup_date` was null).
```

### Shape 4: Test suite condition

```
All test files matching `**/*.auth.test.ts` pass with 0 failures
  on `npm test -- --testPathPattern=auth`.
```

### Shape 5: CI / quality-gate condition

```
`bnac-quality-gate` reports PASS on the full project (build, type,
  lint, test all green).
```

### Shape 6: Performance condition

```
P95 latency for `/api/search?q=*` is < 200ms when the database has
  100k indexed records (measured with the existing benchmark script).
```

### Shape 7: Documentation condition

```
README has a "Getting Started" section that, when followed verbatim
  on a clean machine, produces a running dev server within 10 minutes.
```

### Shape 8: Migration / cutover condition

```
On staging, 100% of read traffic for /api/users is served from the
  new system; legacy reads dropped to 0 in the metric dashboard for
  3 consecutive days.
```

## Bad acceptance tests (and how to fix)

| Bad | Why bad | Fix |
|---|---|---|
| "Authentication is solid" | Subjective | "POST /api/auth/login returns 200 + JWT for valid creds, 401 for invalid" |
| "Code is clean" | Subjective + not testable | "0 critical findings from `/bnac-code-review`" |
| "Tests pass and code reviewed" | Two conditions | Split or pick the load-bearing one (usually tests) |
| "All tasks marked done" | Tautological — doesn't verify outcome | Write the real outcome test |
| "It works" | Unverifiable | Write the specific behavior that proves it works |
| "Users like the new feature" | Not measurable in milestone scope | Use a UX test like "5/5 usability test users complete the task without help" |

## Acceptance test by milestone type

| Milestone type | Best test shape |
|---|---|
| Feature delivery | API or UI behavior |
| Refactor / cleanup | Test suite + quality-gate (no behavior change) |
| Migration | Data condition or migration condition |
| Performance work | Performance condition with explicit metric |
| Documentation | Documentation condition (run-it test) |
| Bug fix milestone | "Reproducer X no longer reproduces" + relevant test added |
| Infrastructure / setup | Quality-gate condition or "deploy hits hello-world endpoint" |

## When the test feels wrong

If you can't write a single, objective, reproducible acceptance test for a milestone, that's the milestone telling you something:

- **Goal is too broad** → split the milestone
- **Goal is too vague** → clarify with the requestor before planning
- **Goal is internal-only** ("refactor module X") → either pick a test-suite condition, or accept that the milestone is about non-functional change and write a quality-gate condition

A milestone with no acceptance test is a milestone that can't be completed. Don't ship it.
