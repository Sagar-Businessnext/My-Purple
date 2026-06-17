---
name: pipeline-stage-machine
description: Formal 8-stage state machine for the BN AI Dark Factory pipeline. Defines states, transitions, guards, terminal states, and the on-disk current-state file format. Used by bnac-pipeline-state-tracker.
user-invocable: false
argument-hint: ""
---

The BN AI Dark Factory pipeline is a sequence of 8 gated stages — each transition must satisfy explicit entry / exit guards. This skill defines the FSM that `bnac-pipeline-state-tracker` enforces. Without a formal state machine, transitions are implicit and stages can be skipped or re-entered incorrectly — exactly the gap identified as #2 in [gap-v2-bn-harness/v2-vs-v3-comparison.md](../../../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

**Authoritative source:** This skill body. The current-state file (`project/.claude/pipeline-state.md`) is the per-project instance.

## Additional Resources

- [reference/states-and-transitions.md](reference/states-and-transitions.md) — full state table, entry guards, exit guards, side effects per transition
- [reference/current-state-format.md](reference/current-state-format.md) — on-disk format of `project/.claude/pipeline-state.md`

## Steps

1. **Read the current-state file** — `project/.claude/pipeline-state.md`. If missing, the pipeline has not been initialized for this project; treat as state `uninitialized`.
2. **Determine requested action** — `status` (read-only), `advance <target-state>`, `rollback <prev-state>`, `freeze` (pause at current state), `init` (create the file at `spec-intake`).
3. **Look up the transition** in [reference/states-and-transitions.md](reference/states-and-transitions.md) — `(current, action) → next` plus the entry/exit guards on both ends.
4. **Evaluate guards** — every guard is either a file-existence check, a status flag check (e.g., `VALIDATION_REPORT.md` status = `PROCEED`), or an explicit human-approval marker. Guards that cannot be evaluated automatically default to FAIL.
5. **If guards pass** — update the current-state file with new state, transition timestamp, actor (system / user / agent), and any guard evidence (the file path that satisfied the guard).
6. **If guards fail** — refuse the transition, return the list of unsatisfied guards, and do not modify the state file.
7. **Log the action** to `project/.claude/log.md` regardless of pass/fail.

## Rules

- **No implicit transitions** — A stage advances only when an agent or human explicitly invokes `advance`. Code generation completing does not auto-advance to Security; the operator must call `/bnac-pipeline-stage advance security`.
- **Forward-only by default, rollback is explicit** — `rollback` is a separate action and must name the prior state. Rollback past a `frozen` state requires an unfreeze first.
- **Terminal states are sticky** — Once at `released-archived` or `aborted`, no transition is allowed except `init` (which creates a new pipeline run with a new ID).
- **Concurrent runs are independent** — Each pipeline run has a unique `run_id`; the current-state file tracks the active run. Multiple runs require multiple state files (`pipeline-state-<run-id>.md`).
- **Never silently fix a guard failure** — Surface the unsatisfied guard exactly; do not attempt to retry, regenerate, or repair the missing artifact.
- **Time budgets are advisory, not enforced** — The state machine records `entered_at` and `time_budget_remaining`, but does not auto-advance on timeout. Timeout handling is operator-driven.
- **`bnac-quality-gate` ✅ is NOT sufficient for production release** — The transition `acceptance-testing → release-prod` requires a separate `bnac-go-nogo-approver` artifact (gap #8 closure). The state machine enforces this by requiring `release-approval.md` with status `GO` as an entry guard on `release-prod`.
