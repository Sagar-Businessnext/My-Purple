Invoke the **bnac-go-nogo-approver** agent to manage stakeholder GO / NO-GO release approval on top of `bnac-quality-gate`.

**Agent:** `bnac-go-nogo-approver`
**Target:** `$ARGUMENTS` (one of: `status`, `request <tier>`, `approve <role> <decision> [conditions...]`, `reject <role> <reason>`, `check-conditions [--condition N=met ...]`, `rotate`)

## What to do

1. Delegate to the `bnac-go-nogo-approver` agent with `$ARGUMENTS`.

2. The agent will:
   - **Read** the `release-approval` skill (tier ladder + record format)
   - **Read** `project/.claude/release-approval.md` (the active attempt, if any)
   - **Read** `project/.claude/pipeline-state.md` (to bind to the active run_id)
   - **Read** the required evidence files (quality-gate-report.md, VALIDATION_REPORT.md, security-review.md, uat-signoff.md, perf-test-report.md, cab-minutes-*.md as required by tier)
   - **Apply** the requested action — open request, record approval, reject, check conditions, rotate
   - **Compute** the consolidated decision per the aggregation rules (any NO-GO overrides; all GO + any CONDITIONAL-GO → CONDITIONAL-GO; etc.)
   - **Update** `release-approval.md` — Request / Evidence / Approvers / Decision blocks + History
   - **Print** a short status table

3. After completion, log results to `project/.claude/log.md`.

## Actions

| Action | Meaning |
|--------|---------|
| `status` | Read-only — print current request + approvers + consolidated decision + evidence statuses |
| `request <tier>` | Open a new approval request at tier `hotfix` / `patch` / `minor` / `major` |
| `approve <role> <decision> [conditions...]` | Record an approver decision (`GO` / `NO-GO` / `CONDITIONAL-GO`); identity passed via operator |
| `reject <role> <reason>` | Shorthand for `approve <role> NO-GO <reason>` |
| `check-conditions` | Re-evaluate conditions from any `CONDITIONAL-GO`; flip to `GO` if all met |
| `rotate` | Archive the current attempt and clear the active file for a new request |

## Examples

```
/bnac-go-nogo status                                                  → print current approval status
/bnac-go-nogo request minor                                           → open a minor-release approval request
/bnac-go-nogo approve tech-lead GO                                    → record tech-lead GO (identity prompted)
/bnac-go-nogo approve product-owner CONDITIONAL-GO "deploy with monitoring in place first"
/bnac-go-nogo reject tech-lead "quality-gate is 9 days stale; re-run first"
/bnac-go-nogo check-conditions --condition 1=met                      → mark condition 1 met; recompute decision
/bnac-go-nogo rotate                                                  → archive current attempt; ready for new request
```

## Why this exists

`bnac-quality-gate` ✅ reports automated PASS / FAIL — necessary but **not sufficient** for a production release. Production cutover needs a named human owner. This command records that owner, the evidence they reviewed, and the timestamp of the decision — exactly what gap #8 from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8 demands.

The `release-approval.md` file produced by this command is the entry guard on `bnac-pipeline-state-tracker` T07 (acceptance-testing → release-prod) — the two bundles compose: this one records the human approval; the state tracker reads it as a transition guard.
