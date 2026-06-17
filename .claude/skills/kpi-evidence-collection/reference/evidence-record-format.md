# Registry and Evidence Record Format

Two file types: the central registry (`kpi-registry.md`) and per-KPI evidence files (`kpi-evidence/<kpi-id>.md`).

## Registry — `project/.claude/kpi-registry.md`

```markdown
# KPI Registry

> Managed by `bnac-kpi-tracker`. Do not edit by hand — use `/bnac-kpi <action>`.

## Source

| Field | Value |
|---|---|
| PRD path | `prds/payment-service/prd-payment.md` |
| Registered at | `2026-05-22T16:00:00Z` |
| Registered by | `@vinod.singh` |
| Run id | `run-2026-05-22-001` |

## KPIs (registered)

| ID | Category | Description | Baseline | Target | Timeframe | Cadence | Source kind | Owner | Status |
|---|---|---|---|---|---|---|---|---|---|
| KPI-001 | business | Loan processing time | 5d | 1d | 6m post-launch | monthly | data-warehouse query | product-owner | active |
| KPI-002 | technical | API p95 latency | 800ms | < 300ms | day-1 prod | weekly | APM dashboard | tech-lead | active |
| KPI-003 | technical | Uptime | 98.5% | 99.9% | rolling 3m | weekly | uptime-monitor | tech-lead | active |
| KPI-004 | user | Adoption rate | 0% | 80% of target users | 90d post-launch | monthly | auth logs | product-owner | active |
| KPI-005 | user | Task completion rate | — | 85% | 90d post-launch | monthly | product analytics | product-owner | unmeasurable |
| KPI-006 | operational | MTTR | — | < 4h | rolling 6m | weekly | PagerDuty | engineering-manager | active |
| KPI-007 | operational | Test coverage | 0% | ≥ 80% | sprint-1 | on-deployment | coverage report | tech-lead | active |

## Excluded

| ID | Reason | Excluded at |
|---|---|---|
| KPI-005 | Source kind = manual but no survey tool named in PRD §16; mark active when source is identified | 2026-05-22T16:00:00Z |

## Cycles

| Cycle | Window | Status | Report |
|---|---|---|---|
| 1 | 2026-05-23 → 2026-06-23 | in-progress | — |
```

### Registry field rules

- **PRD path** — Source of truth. The agent re-reads PRD §16 only when the operator runs `/bnac-kpi register` again.
- **Status** — One of `active` / `unmeasurable` / `excluded` / `retired`. Only `active` KPIs are tracked.
- **Cycles table** — Append-only history of review cycles. Status flips `in-progress` → `cycle-N-complete` only when the cycle report is written and the operator confirms.

## Evidence file — `project/.claude/kpi-evidence/<kpi-id>.md`

```markdown
# KPI-002 — API p95 latency

> Managed by `bnac-kpi-tracker`. Do not edit observations by hand — use `/bnac-kpi collect KPI-002 <value> [--source <link>]`.

## Spec

| Field | Value |
|---|---|
| Category | technical |
| Description | API p95 latency |
| Baseline | 800ms |
| Target | < 300ms |
| Timeframe | day-1 prod, ongoing |
| Cadence | weekly |
| Source kind | APM dashboard |
| Source link | https://apm.businessnext.io/services/payments?dashboard=p95 |
| Owner | tech-lead |
| At-risk threshold | 95% (uptime-style override per `kpi-categories.md`) |
| Parent objective(s) | OBJ-1 (Reduce payment failure tail), OBJ-2 (Improve customer experience) |

## Observations (append-only)

| # | observed_at | observed_value | source_evidence | delta_vs_target | status | comment |
|---|---|---|---|---|---|---|
| 1 | 2026-05-30T09:00:00Z | 850ms | https://apm.../snapshot-2026-05-30 | +183% (over target) | off-track | First week post-deploy; expected during canary; re-check after full traffic shift |
| 2 | 2026-06-06T09:00:00Z | 420ms | https://apm.../snapshot-2026-06-06 | +40% | at-risk | Improvement but still over the 300ms target |
| 3 | 2026-06-13T09:00:00Z | 295ms | https://apm.../snapshot-2026-06-13 | -1.6% (under target) | on-track | Stable for 7 days; target met |

## History (registry events)

| # | At | Event | Detail |
|---|---|---|---|
| 1 | 2026-05-22T16:00:00Z | registered | from PRD §16 |
| 2 | 2026-05-30T09:00:00Z | observation-1 | 850ms / off-track |
| 3 | 2026-06-06T09:00:00Z | observation-2 | 420ms / at-risk |
| 4 | 2026-06-13T09:00:00Z | observation-3 | 295ms / on-track |
```

### Observation field rules

- **observed_at** — ISO 8601 UTC. Never edited.
- **observed_value** — Numeric + unit (e.g., `295ms`, `99.92%`, `4.1h`).
- **source_evidence** — A link, a path to a captured artifact, or a query string. Required.
- **delta_vs_target** — Computed by the agent on insert; never hand-edited.
- **status** — Computed per the at-risk threshold rule on insert; never hand-edited.
- **comment** — Optional free text.

### Corrections

If an observation was wrong (e.g., the query returned stale data), append a new observation with `comment` starting `corrects=<row-#>: <explanation>`. The original observation stays in place; the correction is the most recent observation and is what the cycle report uses.

## Cycle report — `project/.claude/kpi-evidence/kpi-cycle-<N>-report.md`

```markdown
# KPI Cycle 1 Report

**Window:** 2026-05-23 → 2026-06-23
**Generated at:** 2026-06-23T10:00:00Z
**Run id:** run-2026-05-22-001

## Status counts

| Status | Count |
|---|---|
| on-track | 4 |
| at-risk | 1 |
| off-track | 1 |
| no-data | 0 |
| unmeasurable | 1 (KPI-005) |

## KPIs

| ID | Description | Current | Target | Status | Parent objective |
|---|---|---|---|---|---|
| KPI-001 | Loan processing time | 1.3d | 1d | at-risk | OBJ-3 |
| KPI-002 | API p95 latency | 295ms | < 300ms | on-track | OBJ-1, OBJ-2 |
| KPI-003 | Uptime | 99.92% | 99.9% | on-track | OBJ-2 |
| KPI-004 | Adoption rate | 45% | 80% | off-track | OBJ-4 |
| KPI-006 | MTTR | 3.5h | < 4h | on-track | OBJ-5 |
| KPI-007 | Test coverage | 87% | ≥ 80% | on-track | OBJ-5 |

## Flagged KPIs

### KPI-004 — Adoption rate — off-track
- Current: 45% (target 80% by 90 days)
- Parent objective: OBJ-4 (Drive product adoption among target user segment)
- Narrative: 90-day window is half-elapsed; need 8% / week to recover. Marketing recommends paid acquisition push.

### KPI-001 — Loan processing time — at-risk
- Current: 1.3d (target 1d by 6 months post-launch)
- Parent objective: OBJ-3 (Reduce manual loan processing effort)
- Narrative: Manual review queue is the bottleneck; engineering investigating async pre-review.

## Unmeasurable

- KPI-005 (Task completion rate) — source kind = manual; survey tool not named in PRD §16. Recommend updating PRD or excluding from this product.

## Cycle status

`cycle-1-complete` — recorded in registry. Pipeline T09 (post-release-monitoring → released-archived) entry guard is now satisfied for run-2026-05-22-001.
```

The cycle report is the artifact that flips the registry's Cycle row from `in-progress` to `cycle-N-complete`.
