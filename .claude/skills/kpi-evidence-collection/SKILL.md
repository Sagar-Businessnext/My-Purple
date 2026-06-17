---
name: kpi-evidence-collection
description: Runtime KPI evidence collection protocol — registers PRD §16 KPIs into a tracking spec, defines per-category evidence sources, and produces periodic evidence reports. Used by bnac-kpi-tracker.
user-invocable: false
argument-hint: ""
---

PRD §16 declares KPIs at authoring time — baseline, target, timeframe, measurement method. But without a runtime tracker, those numbers never get evidence; the loop from PRD intent to production reality never closes. This skill defines how the tracker registers KPIs, collects evidence, and reports — closing gap #9 from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

**Authoritative source:** This skill body. The per-project registry (`project/.claude/kpi-registry.md`) and the evidence files (`project/.claude/kpi-evidence/`) are the per-project instances.

## Additional Resources

- [reference/kpi-categories.md](reference/kpi-categories.md) — the 4 PRD §16 categories (business / technical / user / operational), their evidence sources, and the review cadences
- [reference/evidence-record-format.md](reference/evidence-record-format.md) — registry file format + evidence file format

## Steps

1. **Register PRD KPIs** — read PRD §16, extract every KPI row (`KPI-XXX` ID, category, baseline, target, timeframe, measurement method), and write each into `project/.claude/kpi-registry.md`. Operator confirms the extraction; the agent does not silently invent KPIs.
2. **Validate measurement source** — for each KPI, confirm the measurement method names a concrete tooling source (Grafana dashboard, APM tool, uptime monitor, query, etc.) AND that the source is reachable (file path, URL, or named system). KPIs with no concrete source are flagged `unmeasurable` and excluded from the active registry until updated.
3. **Initialize evidence files** — one file per KPI in `project/.claude/kpi-evidence/<kpi-id>.md`. Each file contains the baseline, target, cadence, and an empty `## Observations` table.
4. **Collect evidence per cadence** — at each KPI's review cadence (weekly / monthly / quarterly per [`kpi-categories.md`](reference/kpi-categories.md)), append a new observation row with: observed_at, observed_value, source (link or query), evidence_path (optional supporting artifact), and a delta vs target.
5. **Compute KPI status** — for each KPI, compute current status based on the most recent observation vs target:
   - `on-track` — current value meets or exceeds target
   - `at-risk` — within 80% of target (configurable per KPI)
   - `off-track` — below 80% of target
   - `no-data` — no observation yet for this cycle
6. **Generate a cycle report** — at the end of each review cycle (weekly / monthly / quarterly), produce a summary report listing per-KPI status, comparison to last cycle, and flagged at-risk / off-track KPIs.
7. **Mark a cycle complete** — set the cycle's status to `cycle-N-complete` in the registry. This is the entry guard the pipeline state tracker (gap #2) reads on T09 (post-release-monitoring → released-archived).

## Rules

- **One KPI registered = one evidence file** — `kpi-evidence/<kpi-id>.md`. The 1-to-1 mapping is non-negotiable; it keeps each KPI's history auditable in isolation.
- **Baselines are immutable** — Once registered, the baseline is fixed. If the PRD changes the baseline, the agent refuses to silently update; it asks the operator to confirm and records a `baseline-revised` event in the evidence file's history.
- **Observations are append-only** — Never edit a past observation. Errors are corrected by appending a new observation row with a `corrects=<prior-row-id>` field and a comment.
- **Manual entry is allowed; automated polling is preferred** — Where the measurement method points to a queryable source (Grafana / SQL / API), the agent runs the query (via Bash where authorized) and records the result. Where the source is human-supplied (CSAT survey, sales report), the operator pastes the value into a `collect` call; the agent validates the format and records it.
- **No silent extrapolation** — Missing observations are recorded as `no-data`, not interpolated. The cycle report explicitly lists `no-data` KPIs.
- **Status thresholds are per-KPI** — Default at-risk threshold is 80% of target, but a KPI's PRD row can override (e.g., uptime KPI may want 95% of 99.9% target as `at-risk`, not 80%).
- **The cycle-complete flag is the gap-#2 entry guard** — Pipeline T09 reads `kpi-registry.md` and looks for `Cycle N status: cycle-N-complete` matching the run_id. The flag is only set after the cycle report is produced.
- **Stale evidence is surfaced, not auto-refreshed** — If an evidence file's most recent observation is older than 2× the cadence interval, the agent flags it `stale`. It does not poll automatically.
- **KPIs trace back to PRD §02 objectives** — Every KPI must cite at least one PRD §02 business objective (or be marked `vanity` and flagged in the cycle report). This is the `CR-006` check at runtime.
