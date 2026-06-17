Invoke phase lifecycle: `complete` rolls a fully-Approved phase up into `index.summary.md`; `status` reports per-phase milestone progress. Action-driven mirror of `/bnac-milestone`.

**Agents:**
- `complete` → `bnac-context-compactor` (phase mode, trigger=complete)
- `status` → `bnac-phase-planner` (read-only status report — same agent that enriches phase indexes)

**Target:** `$ARGUMENTS` — `<action> [phase-id-or-folder]`
**Actions:** `complete` · `status`

## Action map

| Action | Arg shape | What it does |
|---|---|---|
| `complete <phase-id>` | required | Roll up a phase into `phases/phase-<N>-<slug>/index.summary.md` (≤1500 tokens) + mark phase `Approved` in `phases/index.md` + rebuild `carry-forward.md` (child milestone summaries now elided in favor of the phase summary) |
| `status [phase-id]` | optional (defaults to all phases) | Report per-phase milestone progress: how many milestones done / in-progress / blocked / not-started, and whether the phase is ready for `complete` |

If `action` is omitted, default to `status`.

## Phase reference shape

`<phase-id>` accepts any of:

- The phase folder name verbatim: `phase-1-foundation`, `phase-cmm-context-memory`
- The numeric ID: `phase-1`, `phase-2`
- The ID without `phase-` prefix: `1`, `2`, `cmm`
- The phase's letter ID (when letter-prefixed): `CMM`, `P3`

The command resolves to the folder name via Glob `project/.claude/phases/phase-*/` matching.

## What to do

1. Parse `<action>` from `$ARGUMENTS` (first positional). If absent → `status`.
2. Parse `<phase-id>` (second positional). For `complete`, required; for `status`, defaults to all phases.
3. Resolve the phase reference to a folder name via Glob.
4. Delegate per the action.

### When action = `complete`

1. **Resolve** the phase folder; abort with a clear message if not found.
2. **Read** `project/.claude/phases/index.md` — confirm the phase exists in the allocation table and read its current status + milestone allocation.
3. **Read** the phase's `index.md` and `milestone-status.md` — enumerate every milestone in the phase and its status.
4. **Pre-check (NON-NEGOTIABLE):** every milestone in the phase MUST be `Approved`. If ANY milestone is in another state (`Not Started`, `In Progress`, `Review Pending`, `Blocked`):
   - **Refuse the action.** Print the offending milestones with their current state.
   - Suggest: "Run `/bnac-milestone complete <M#>` for any remaining work, then re-run `/bnac-phase complete <phase-id>`."
   - Exit without writing anything.
5. **Re-check that no milestone in this phase is currently active.** If `milestone-status.md` lists an active milestone in this phase, refuse and suggest completing/closing it first.
6. **Idempotency check:** if `index.summary.md` already exists for this phase AND `phases/index.md` already shows the phase as `Approved`, warn that the phase appears already rolled up and offer to re-run as a refresh (which overwrites the summary). Default to refusing; require an explicit confirm.
7. **Delegate to `bnac-context-compactor`** with `{mode: "phase", target: "<folder-name>", trigger: "complete"}`. The compactor:
   - Reads every milestone *detail* (NOT summary — CMM-D4) in the phase folder, plus log.md slice for the phase period, plus optional git diff
   - Composes the phase summary per the `compact-phase-template` skill (≤1500 tokens, 6 required sections)
   - Self-validates + retries on over-budget, truncates with marker on final fallback
   - Writes `project/.claude/phases/<folder>/index.summary.md`
   - Rebuilds `carry-forward.md` — the new phase summary now replaces the child milestone summaries per the updated stitching strategy
   - Returns stats
8. **Update `phases/index.md`:**
   - Set the phase row's `Status` column to `Approved` with the completion date (e.g., `Approved 2026-05-21`)
   - If the top-level index has a project-wide phase progress indicator, advance it
9. **Output** the completion summary: phase ID + title, summary file path, token count, milestones rolled up, carry-forward stats (blocks included, blocks elided, total tokens), child milestone summaries now skipped in carry-forward.
10. **Suggest next:** if there's a next phase in `phases/index.md`, recommend "Run `/bnac-milestone start <next M#>` to begin the next phase's first milestone."
11. **Log to `.claude/log.md`:** phase completed, summary file path, token count, carry-forward stats, timestamp. Activity-type `milestone` (the log schema doesn't have a separate `phase` type yet — note "phase rollup" in the brief description).

### When action = `status`

1. **Read** `project/.claude/phases/index.md` and `milestone-status.md`.
2. If `<phase-id>` is provided, scope the report to that phase; otherwise iterate every phase.
3. **For each phase**, compute:
   - Phase status (from `phases/index.md` Status column)
   - Milestone breakdown: Not Started / In Progress / Review Pending / Approved counts
   - Active milestone in this phase (if any)
   - Whether `index.summary.md` exists
   - Whether the phase is ready for `/bnac-phase complete` (all milestones Approved, no active, no summary yet OR summary exists but phase status not yet `Approved`)
4. **Delegate to `bnac-phase-planner`** in status-only mode (the agent already knows how to read `phases/index.md` per its planning duties; here it composes the report instead of enriching). Alternatively, this command may compose the report directly — implementation choice; the contract is the output below.
5. **Output** the report:
   ```
   📊 Phase status

   Phase 1 — Foundation                Approved 2026-04-30  (4/4 milestones · summary ✅)
   Phase CMM — Context & Memory        In Progress           (2/5 milestones Approved · M-CMM-3 ACTIVE · no summary yet)
     → Run `/bnac-phase complete phase-cmm-context-memory` once all milestones are Approved

   Phase 2 — Vertical                  Not Started           (0/4 milestones)
   ```
6. **Log to `.claude/log.md`:** phase status check, scope (single or all), timestamp.

## Rules (for `complete`)

- **NEVER complete a phase with non-Approved milestones** — list the offending ones and refuse. The phase summary is built from milestone details under the implicit assumption that the milestone work is settled; running on in-progress milestones would produce summaries that misrepresent the state.
- **NEVER complete a phase that has an active milestone** — close the milestone first (`/bnac-milestone complete <M#>`).
- **ALWAYS delegate composition to `bnac-context-compactor`** — this command does not author summaries directly; it orchestrates the pre-check + status flip and delegates writing.
- **ALWAYS update `phases/index.md` Status to `Approved`** — without this, the stitching strategy won't switch from milestone summaries to phase summary.
- **Idempotency:** re-running `complete` on an already-rolled-up phase refuses by default; user must opt into refresh (which ships in M-CMM-4 as `/bnac-context refresh P<N>`).

## Rules (for `status`)

- **Read-only** — `status` never writes summaries, never flips phase status, never modifies `phases/index.md`.
- **Always log the status check** — even read-only actions are part of the activity record.

## Examples

```
/bnac-phase complete phase-1-foundation         → roll up phase 1
/bnac-phase complete phase-cmm-context-memory   → roll up Phase CMM
/bnac-phase complete 1                          → shorthand for phase-1
/bnac-phase complete CMM                        → shorthand for phase-cmm-*
/bnac-phase status                              → report on every phase
/bnac-phase status phase-1-foundation           → report on a single phase
/bnac-phase                                     → defaults to status (all phases)
```

## Distinct from `/bnac-phase-plan`

This command **operates** on phases (lifecycle: complete + status). To **define / enrich** phases from scope, use `/bnac-phase-plan` — it routes to `bnac-phase-planner` and enriches each `phase-<N>-<slug>/index.md` with goal, exit criterion, milestone allocation, and agent rollup. That command writes; this command rolls up.

## Distinct from `/bnac-milestone`

`/bnac-milestone` operates on milestones (start / status / complete). `/bnac-phase complete` is what you run AFTER every milestone in a phase has been completed via `/bnac-milestone complete` and approved by human review.

The lifecycle order:

```
/bnac-milestone start M1     →  /bnac-milestone complete M1   (milestone summary written)
/bnac-milestone start M2     →  /bnac-milestone complete M2
...
/bnac-milestone complete M<last-in-phase>
/bnac-phase complete <phase>                                   (phase summary written; child milestone summaries elided in carry-forward)
/bnac-milestone start M<first-of-next-phase>
```
