# Release Approval Record Format

Canonical on-disk format of `project/.claude/release-approval.md`. The pipeline state tracker (gap #2) reads this file as the guard on T07 (acceptance-testing → release-prod).

## File template

```markdown
# Release Approval

> Managed by `bnac-go-nogo-approver`. Do not edit Decisions by hand — use `/bnac-go-nogo <action>`.

## Decision (consolidated)

| Field | Value |
|---|---|
| Overall decision | `GO` |
| Decided at | `2026-05-22T14:30:00Z` |
| Release tier | `minor` |
| Target environment | `prod-eu-west-1` |
| Deploy window | `2026-05-23T08:00:00Z – 2026-05-23T10:00:00Z` |
| Run id | `run-2026-05-22-001` |

## Request

| Field | Value |
|---|---|
| Requested by | Vinod Singh (`vinod.singh@businessnext.com`) |
| Requested at | `2026-05-22T11:00:00Z` |
| Release tier | `minor` |
| Change summary | Add idempotency layer to /payments POST + 3 new alerts |
| Target environment | `prod-eu-west-1` |
| Deploy window | `2026-05-23T08:00:00Z – 2026-05-23T10:00:00Z` |
| Required approvers | tech-lead, product-owner, qa-lead |

## Evidence

| Artifact | Path | Status | mtime |
|---|---|---|---|
| Quality-gate report | `project/.claude/quality-gate-report.md` | PASS | 2026-05-22T10:45:00Z |
| Validation report | `prds/payment-service/VALIDATION_REPORT.md` | PROCEED (44/44) | 2026-05-22T09:30:00Z |
| Security review | `project/.claude/security-review.md` | PASS | 2026-05-22T10:55:00Z |
| UAT sign-off | `project/.claude/uat-signoff.md` | SIGNED | 2026-05-22T13:15:00Z |

## Approvers

### tech-lead — Asha Rao

| Field | Value |
|---|---|
| Email | asha.rao@businessnext.com |
| Decision | `GO` |
| Decided at | `2026-05-22T14:00:00Z` |
| Evidence reviewed | quality-gate-report.md, VALIDATION_REPORT.md, security-review.md |
| Comment | Idempotency contract correctly enforced in CR-011. |

### product-owner — Rahul Mehta

| Field | Value |
|---|---|
| Email | rahul.mehta@businessnext.com |
| Decision | `GO` |
| Decided at | `2026-05-22T14:20:00Z` |
| Evidence reviewed | VALIDATION_REPORT.md, uat-signoff.md |
| Comment | UAT confirms the three Critical UCs run end-to-end. |

### qa-lead — Priya Iyer

| Field | Value |
|---|---|
| Email | priya.iyer@businessnext.com |
| Decision | `GO` |
| Decided at | `2026-05-22T14:30:00Z` |
| Evidence reviewed | quality-gate-report.md, uat-signoff.md |
| Comment | Test coverage gate met (87% — target ≥ 80%). |

## History (append-only)

| # | At | Actor | Action | Detail |
|---|---|---|---|---|
| 1 | 2026-05-22T11:00:00Z | Vinod Singh | request | Tier=minor, env=prod-eu-west-1 |
| 2 | 2026-05-22T14:00:00Z | Asha Rao | approve | tech-lead GO |
| 3 | 2026-05-22T14:20:00Z | Rahul Mehta | approve | product-owner GO |
| 4 | 2026-05-22T14:30:00Z | Priya Iyer | approve | qa-lead GO; consolidated decision → GO |
```

## Field rules

- **Overall decision** — Computed from the Approvers section per the aggregation rules in [approval-tiers.md](approval-tiers.md). Never edited by hand.
- **Decided at** — The timestamp of the last signature that produced the consolidated decision.
- **Release tier** — One of `hotfix` / `patch` / `minor` / `major`. Set at request time; immutable after first approval.
- **Run id** — Cross-reference to the pipeline state tracker's run_id. Required so the state tracker can confirm this approval belongs to the active run.
- **Required approvers** — Set at request time based on the tier ladder; immutable after first approval.
- **Evidence rows** — One row per required-evidence artifact for the tier. Each row's status and mtime are evaluated by `bnac-go-nogo-approver` before allowing sign-off.
- **Approver decision** — One of `GO` / `NO-GO` / `CONDITIONAL-GO`. `CONDITIONAL-GO` requires a `Conditions` sub-block listing each condition + a re-check owner.

## NO-GO and CONDITIONAL-GO blocks

### NO-GO example

```markdown
### tech-lead — Asha Rao

| Field | Value |
|---|---|
| Decision | `NO-GO` |
| Decided at | `2026-05-22T14:00:00Z` |
| Reason | quality-gate-report.md mtime is 9 days old; needs re-run on current main |
| Re-request requirement | Re-run quality-gate after merging latest main, then re-request approval |
```

A `NO-GO` from any required approver immediately sets the consolidated decision to `NO-GO`. The pipeline state tracker rejects T07. To proceed, the release requestor must address the reason and create a **new** request — this rotates the current `release-approval.md` to `release-approval-<run_id>-<attempt-number>.md`.

### CONDITIONAL-GO example

```markdown
### product-owner — Rahul Mehta

| Field | Value |
|---|---|
| Decision | `CONDITIONAL-GO` |
| Decided at | `2026-05-22T14:20:00Z` |
| Comment | Approve subject to monitoring being in place before traffic shift |

#### Conditions

| # | Condition | Re-check owner | Re-check by |
|---|---|---|---|
| 1 | New alert `payment.idempotency.collision_rate` must be live in Grafana before 50% traffic | @priya.iyer (qa-lead) | 2026-05-23T07:00:00Z |
```

If every required approver signed `GO` or `CONDITIONAL-GO` (none `NO-GO`), the consolidated decision is `CONDITIONAL-GO`. The pipeline state tracker rejects T07 until all listed conditions are marked `met` (a second pass of `/bnac-go-nogo check-conditions` confirms each one and flips the consolidated decision to `GO`).

## Rotation policy

When a new request is opened after a NO-GO (or after a consolidated GO release has been deployed and the run advances past `release-prod`):

1. Rename the current `release-approval.md` to `release-approval-<run_id>-<attempt_number>.md`.
2. Create a new `release-approval.md` with a fresh `## Request` block.
3. The pipeline state tracker reads only `release-approval.md` (the active attempt).
