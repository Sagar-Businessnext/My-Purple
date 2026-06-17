# KPI Categories — Evidence Sources and Cadences

PRD §16 declares four categories. Each has different evidence sources and a default review cadence.

## Categories

| Category | Examples | Default cadence | Typical measurement source | Owner |
|---|---|---|---|---|
| `business` | Revenue per user, processing time, automation rate, ARR | Monthly | BI tool / data warehouse query | Product Owner |
| `technical` | API p95 latency, uptime, deployment frequency, error rate | Weekly | APM (Datadog / New Relic), uptime monitor, CI/CD metrics | Tech Lead |
| `user` | Adoption rate, task completion rate, CSAT, NPS | Monthly | Auth logs, product analytics, survey tool | Product Owner |
| `operational` | MTTR, on-call incident rate, test coverage, deploy lead time | Weekly | Incident tool (PagerDuty), test report, deploy log | Engineering Manager |

## Cadence overrides

A KPI's PRD §16 row may declare a non-default cadence in the "KPI Review Cadence" sub-table. Examples:

| Cadence override | When to use |
|---|---|
| `daily` | Critical SLOs that page on breach (e.g., availability for a payment system) |
| `weekly` | Default for technical and operational KPIs |
| `monthly` | Default for business and user KPIs |
| `quarterly` | Strategic / strategic-review KPIs reviewed by the steering committee |
| `on-deployment` | KPIs that only make sense to measure right after a release (deploy frequency, change failure rate) |

## Measurement source classification

| Source kind | How the tracker collects |
|---|---|
| Queryable (SQL, PromQL, API) | Agent invokes the query via Bash (when authorized); records numeric result + query text |
| Dashboard URL (Grafana, Looker, Tableau) | Agent records the URL + a manual observed_value from the operator; cannot auto-poll a rendered dashboard |
| Manual / survey | Operator pastes the value into `/bnac-kpi collect <kpi-id> <value>`; agent validates format |
| File-based (e.g., `coverage-report.json`) | Agent reads the file directly and extracts the metric |
| Unmeasurable / aspirational | Flagged `unmeasurable`; excluded from active registry; surfaces in cycle report so PRD §16 can be revised |

## At-risk thresholds

Default: a KPI is `at-risk` when current ≤ 80% of (baseline + (target - baseline) × elapsed_fraction). The elapsed_fraction accounts for the timeframe — if a KPI targets 99.9% uptime over a 12-month window and 3 months have elapsed, the at-risk line is computed proportionally, not at the final target.

Per-KPI overrides:

| Override | Example KPI | Reason |
|---|---|---|
| `at-risk: <95%>` | Uptime, availability | 80% of 99.9% is meaningless; uptime KPIs need tighter bands |
| `at-risk: <50%>` | Adoption rate (early launch) | First-quarter adoption is naturally far below 12-month target; a tighter at-risk band creates false alarms |
| `at-risk: na` | Aspirational KPIs | Mark as no-status; report on observed value only |

## Cycle report contents

At the end of each cycle, the tracker produces `kpi-cycle-<N>-report.md` containing:

- Cycle window (start → end timestamps)
- KPI count by status (on-track / at-risk / off-track / no-data / unmeasurable)
- Per-KPI rows with status, current value, target, delta, source link
- Flagged KPIs (at-risk + off-track) with a short narrative for each
- Cross-references to PRD §02 objectives — every off-track KPI's parent objective is named

## Cycle-complete signal

The cycle report's existence is not enough. The tracker explicitly marks the cycle complete in `kpi-registry.md`:

```markdown
## Cycles
| Cycle | Window | Status | Report |
|---|---|---|---|
| 1 | 2026-05-23 → 2026-06-23 | cycle-1-complete | kpi-evidence/kpi-cycle-1-report.md |
```

The `cycle-N-complete` flag is what `bnac-pipeline-state-tracker` T09 reads as its entry guard.
