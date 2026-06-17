Invoke the **bnac-kpi-tracker** agent to register PRD §16 KPIs, collect observations, compute status, and produce cycle reports.

**Agent:** `bnac-kpi-tracker`
**Target:** `$ARGUMENTS` (one of: `register <prd-folder>`, `list`, `collect <kpi-id> <value> [--source ...] [--comment ...]`, `collect-auto <kpi-id>`, `status <kpi-id>`, `report`, `verify`)

## What to do

1. Delegate to the `bnac-kpi-tracker` agent with `$ARGUMENTS`.

2. The agent will:
   - **Read** the `kpi-evidence-collection` skill (categories + record format)
   - **Read** the active `kpi-registry.md` (if present) or PRD §16 (for `register`)
   - **Read** the active `pipeline-state.md` (for run_id binding)
   - **Apply** the requested action — register / list / collect / collect-auto / status / report / verify
   - **Update** the registry + evidence files as needed (append-only for observations)
   - **Print** a short status table

3. After completion, log results to `project/.claude/log.md`.

## Actions

| Action | Meaning |
|--------|---------|
| `register <prd-folder>` | Extract PRD §16 into `kpi-registry.md` + create one evidence file per active KPI |
| `list` | Read-only — print active KPIs with current status |
| `collect <kpi-id> <value>` | Append a manual observation to the named KPI |
| `collect-auto <kpi-id>` | Run the registered measurement query and append the result |
| `status <kpi-id>` | Read-only — print full observation history + computed trend for the KPI |
| `report` | Generate the cycle report and flip the cycle row to `cycle-N-complete` |
| `verify` | Read-only audit — confirm every active KPI traces to a PRD §02 objective; confirm sources are reachable |

## Examples

```
/bnac-kpi register prds/payment-service/                                    → extract PRD §16 into the registry
/bnac-kpi list                                                              → print active KPIs + current status
/bnac-kpi collect KPI-002 295ms --source https://apm.../snapshot-2026-06-13 → record manual observation
/bnac-kpi collect-auto KPI-002                                              → run registered Grafana query, record result
/bnac-kpi status KPI-002                                                    → show full observation history for KPI-002
/bnac-kpi report                                                            → close the active cycle and produce the cycle report
/bnac-kpi verify                                                            → audit KPI → §02 objective traces and source reachability
```

## Why this exists

PRD §16 declares KPIs at authoring time but produces no evidence in production. Without a runtime tracker, the loop from PRD intent to production reality never closes — exactly gap #9 from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

The cycle report this command produces is also the entry guard on `bnac-pipeline-state-tracker` T09 (post-release-monitoring → released-archived). Without `cycle-N-complete` in the registry, the pipeline run cannot reach the terminal `released-archived` state — so the KPI loop is mandatory for a fully closed pipeline.
