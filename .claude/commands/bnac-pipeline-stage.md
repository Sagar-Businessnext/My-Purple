Invoke the **bnac-pipeline-state-tracker** agent to manage the formal 8-stage pipeline state machine.

**Agent:** `bnac-pipeline-state-tracker`
**Target:** `$ARGUMENTS` (one of: `status`, `init`, `advance <target>`, `rollback <prev>`, `freeze [reason]`, `unfreeze`, `abort <reason>`)

## What to do

1. Delegate to the `bnac-pipeline-state-tracker` agent with `$ARGUMENTS`.

2. The agent will:
   - **Read** the `pipeline-stage-machine` skill (FSM definition + state file format)
   - **Read** `project/.claude/pipeline-state.md` (the active run, if any)
   - **Look up** the requested action in the transition table
   - **Evaluate guards** by reading the evidence files (VALIDATION_REPORT.md, quality-gate-report.md, security-review.md, release-approval.md, kpi-evidence/, etc.)
   - **Update** `pipeline-state.md` if the transition is legal and all guards pass — Current block + append to History
   - **Reject** if the transition is illegal or any guard fails — append to Rejected Attempts, print the unsatisfied guards
   - **Print** a short table showing the before/after state + legal next actions

3. After completion, log results to `project/.claude/log.md`.

## Actions

| Action | Meaning |
|--------|---------|
| `status` | Read-only — print current state + legal next actions |
| `init` | Create a new pipeline run at `spec-intake` (rotates a terminal run to archive first) |
| `advance <target>` | Move forward to `<target>` if the transition is legal and guards pass |
| `rollback <prev>` | Move backward to a previously visited state in this run |
| `freeze [reason]` | Pause the run; preserves the prior state for `unfreeze` |
| `unfreeze` | Resume from the state prior to freeze |
| `abort <reason>` | Terminate the run; writes `abort-reason.md` |

## Examples

```
/bnac-pipeline-stage status                          → print current state + legal actions
/bnac-pipeline-stage init                            → start a new run at spec-intake
/bnac-pipeline-stage advance ai-spec                 → move spec-intake → ai-spec
/bnac-pipeline-stage advance md-files                → move ai-spec → md-files (PRD now must validate)
/bnac-pipeline-stage advance code-gen                → requires VALIDATION_REPORT PROCEED
/bnac-pipeline-stage advance release-prod            → requires quality-gate PASS + release-approval GO
/bnac-pipeline-stage rollback ai-spec                → return to ai-spec to fix PRD
/bnac-pipeline-stage freeze "waiting on legal review" → pause the run with reason
/bnac-pipeline-stage abort "scope cancelled by sponsor" → terminate the run
```

## Why this exists

The BN AI Dark Factory contract demands explicit gated transitions across 8 stages — without an enforcement engine, transitions become implicit and stages get silently skipped. This command closes **gap #2** from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

The state machine sits on top of, not in place of, the existing per-stage tools — `/bnac-pag-verify` still validates PRDs, `/bnac-quality-gate` still runs tests, `/bnac-go-nogo` (gap #8) still records release approval, `/bnac-kpi register` (gap #9) still tracks KPIs. This command coordinates them.
