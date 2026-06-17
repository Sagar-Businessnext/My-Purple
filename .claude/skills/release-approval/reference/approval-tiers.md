# Release Tiers and Approver Matrix

Different release sizes need different levels of human review. This file defines the tier ladder and the minimum approver set per tier.

## Tier ladder

| Tier | Trigger | Risk | Required approvers (minimum) | Required evidence (minimum) |
|---|---|---|---|---|
| `hotfix` | Production issue, < 4h fix-to-deploy | Low (small surface) | (1) On-call engineer + (2) Tech lead | quality-gate ✅; security-review.md PASS; incident reference |
| `patch` | Bug fixes, minor improvements, no schema change | Low | (1) Tech lead + (2) Product owner | quality-gate ✅; VALIDATION_REPORT PROCEED (if PRD changed); security-review.md PASS |
| `minor` | New feature(s), backward-compatible API change | Medium | (1) Tech lead + (2) Product owner + (3) QA lead | All of `patch` + UAT sign-off (`uat-signoff.md`) |
| `major` | Breaking API change, schema migration, or significant new capability | High | All of `minor` + (4) Engineering manager + (5) Change Advisory Board representative | All of `minor` + perf-test report + change-advisory-board minutes |

## Approver field requirements

Every approver row in `release-approval.md` must have:

| Field | Required | Format |
|---|---|---|
| name | Yes | Full name |
| role | Yes | One of: `on-call`, `tech-lead`, `product-owner`, `qa-lead`, `engineering-manager`, `cab-rep` |
| email | Yes | Org email address |
| decision | Yes | `GO` \| `NO-GO` \| `CONDITIONAL-GO` |
| decided_at | Yes | ISO 8601 UTC |
| evidence_reviewed | Yes | List of file paths the approver reviewed |
| conditions | If `CONDITIONAL-GO` | List of explicit conditions + a re-check owner |
| comment | Optional | Free text |

## Decision aggregation rules

| Approver pattern | Overall decision |
|---|---|
| All required approvers signed `GO` | `GO` |
| Any required approver signed `NO-GO` | `NO-GO` (overrides) |
| All required approvers signed but at least one is `CONDITIONAL-GO` (none `NO-GO`) | `CONDITIONAL-GO` — listed conditions must be addressed before pipeline T07 reads the file as a guard |
| One or more required approvers have not signed yet | `PENDING` (T07 guard fails) |

## Evidence requirements in detail

### `quality-gate ✅`

The latest `project/.claude/quality-gate-report.md` must show all four lines passing (Build ✅, Type check ✅, Lint ✅ or ⚠️, Tests ✅). The file mtime must be ≤ 7 days old at sign-off time.

### `VALIDATION_REPORT PROCEED`

The `prds/<product>/VALIDATION_REPORT.md` Summary table must show `Status | PROCEED` (i.e., Critical 44/44). Only required when the release contains PRD changes.

### `security-review.md PASS`

`project/.claude/security-review.md` Status field = `PASS`. Required for every tier.

### `uat-signoff.md`

`project/.claude/uat-signoff.md` exists, names the UAT lead, and references the test plan. Required for `minor` and `major`.

### Perf-test report

`project/.claude/perf-test-report.md` shows the latest load test passing every NFR with a numeric SLO target (PRD §09 + §20). Required for `major`.

### Change Advisory Board minutes

`project/.claude/cab-minutes-<date>.md` records the CAB decision + attendees. Required for `major`.

## When this tier ladder does NOT apply

- **Pre-prod environments (dev / staging)** — Tier ladder is for production releases. Lower-environment deploys do not need a `release-approval.md`. Pipeline state tracker T07 only requires the file when advancing to `release-prod`.
- **Read-only or shadow deploys** — A deploy that takes no production traffic does not need a release approval. The deploy receipt is still recorded.
- **Operator-driven freeze** — During a `frozen` pipeline state (gap #2 T11), no approval is consumed. The freeze itself does not require an approval record.
