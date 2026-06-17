# Current-State File Format

The current state lives in `project/.claude/pipeline-state.md`. It is the single source of truth for "where is this pipeline run right now."

## File template

```markdown
# Pipeline State

> Auto-managed by `bnac-pipeline-state-tracker`. Do not edit by hand — use `/bnac-pipeline-stage <action>`.

## Current

| Field | Value |
|---|---|
| run_id | `run-2026-05-22-001` |
| current_state | `code-gen` |
| entered_at | `2026-05-22T10:14:00Z` |
| entered_by | `@bnac-developer` |
| evidence | `prds/payment-service/VALIDATION_REPORT.md` |
| time_budget_remaining | `36h` (advisory, not enforced) |
| frozen | `false` |

## History

| # | From | Action | To | At | By | Evidence | Result |
|---|---|---|---|---|---|---|---|
| 1 | uninitialized | init | spec-intake | 2026-05-20T09:00:00Z | @vinod.singh | — | OK |
| 2 | spec-intake | advance ai-spec | ai-spec | 2026-05-20T11:30:00Z | @vinod.singh | prds/payment-service/brief.md | OK |
| 3 | ai-spec | advance md-files | md-files | 2026-05-21T15:45:00Z | @pag-doc-writer | prds/payment-service/prd-payment.md | OK |
| 4 | md-files | advance code-gen | code-gen | 2026-05-22T10:14:00Z | @pag-doc-verifier | prds/payment-service/VALIDATION_REPORT.md (PROCEED) | OK |

## Rejected attempts

| # | From | Action | Attempted At | By | Reason |
|---|---|---|---|---|---|
| 1 | md-files | advance release-prod | 2026-05-22T09:55:00Z | @vinod.singh | Illegal transition; legal actions from `md-files`: `advance code-gen`, `rollback ai-spec`, `freeze`, `abort` |

## Notes

(Operator-readable. Optional. Use for "we paused here because X.")
```

## Field rules

- **`run_id`** — Format: `run-<YYYY-MM-DD>-<NNN>` where NNN is a per-day counter. Never reused.
- **`current_state`** — Must be one of the 11 states defined in [states-and-transitions.md](states-and-transitions.md).
- **`entered_at`** — ISO 8601 UTC.
- **`entered_by`** — `@<actor>` where actor is a user (`@vinod.singh`), an agent name (`@bnac-developer`), or `@system` for automated transitions.
- **`evidence`** — Relative path from project root to the file that satisfied the entry guard for the current state. Required for every state except `uninitialized` and `aborted`.
- **`time_budget_remaining`** — Optional, advisory. Format: `<N><unit>` (e.g., `48h`, `5d`). The state machine does NOT enforce this; operators use it.
- **`frozen`** — `true` only when current state is `frozen`. When `false`, `current_state` is the actual state.

## History append rules

- Append-only. Never edit a history row.
- Numbered sequentially from 1.
- One row per accepted transition.
- Rollbacks and unfreezes get their own rows with `Action` = `rollback <prev>` / `unfreeze`.

## Rejected attempts append rules

- Every illegal transition request gets logged here, even if the operator immediately retries with the correct action.
- This is the audit trail for "the operator tried to skip security."

## Multiple runs

A project with multiple active pipeline runs uses one file per run:

- `pipeline-state.md` — the **active** run (single source of truth for "what state are we in right now")
- `pipeline-state-<run_id>.md` — archived prior runs

The active file is rotated on `init` (T14) from a terminal state — the prior `pipeline-state.md` is renamed to `pipeline-state-<run_id>.md` and a new `pipeline-state.md` is created.

## What the tracker reads / writes

The `bnac-pipeline-state-tracker` agent:

- **Reads** the current `pipeline-state.md`, the evidence files referenced by guards, and the transition table
- **Writes** the `## Current` block, appends to `## History`, appends to `## Rejected attempts`
- **Never modifies** other project files, the rules / skill bodies, evidence files, or the PRD

If the file is missing or malformed, the tracker reports an explicit error and refuses to act until the operator runs `/bnac-pipeline-stage init` or repairs the file.
