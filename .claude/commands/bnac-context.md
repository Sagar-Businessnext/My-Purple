---
description: Manage the auto-stitched carry-forward.md — refresh summaries, show current state, force a rebuild, or report drift.
argument-hint: "<refresh|show|load|check-stale> [target]"
---

Invoke the **bnac-context-compactor** agent to operate on the carry-forward / summary subsystem: re-run compaction (`refresh`), force a stitch rebuild (`load`), report drift (`check-stale`), or print the current carry-forward (`show`).

**Agent:** `bnac-context-compactor`
**Target:** `$ARGUMENTS` — `<action> [target]`
**Actions:** `refresh` · `show` · `load` · `check-stale`

## Action map

| Action | Arg shape | Read/Write | What it does |
|---|---|---|---|
| `refresh [M#\|P#\|phase-folder\|all]` | optional; defaults to `all` | write | Re-run compactor for one milestone, one phase, or every summary in the project. Routes to `bnac-context-compactor` with `{mode, target, trigger: "refresh"}`. |
| `show` | none | read-only | Print current `project/.claude/context/carry-forward.md` to stdout. No agent delegation; no log entry. |
| `load` | none | write (stitch only) | Force rebuild `carry-forward.md` for the current active milestone. Routes to `bnac-context-compactor` with `{mode: "stitch-only", target: null, trigger: "refresh"}`. No new summaries written. |
| `check-stale` | none | read-only | List every `*.summary.md` whose listed artifacts have a newer git mtime than the summary file. Routes to `bnac-context-compactor` with `{mode: "check-stale", target: null, trigger: "refresh"}`. No log entry. |

If `action` is omitted, default to `show` (read-only is the safest default).

## What to do

1. Parse `<action>` from `$ARGUMENTS` (first positional). If absent → `show`.
2. Parse `<target>` (second positional). Only meaningful for `refresh`.
3. Dispatch to the per-action procedure below.

### When action = `refresh`

1. **Parse `<target>`.** If absent → `all`. Resolve per [Target parsing rules](#target-parsing-rules-for-refresh) — must produce one of:
   - `{kind: "milestone", id: "M<N>"}`  (single milestone)
   - `{kind: "phase", folder: "phase-<N>-<slug>"}`  (single phase)
   - `{kind: "all"}`  (every summary)
2. **Verify** `project/.claude/context/` exists. If not, abort with: `No carry-forward subsystem yet. Run /bnac-milestone start <M#> first.`
3. **For `kind: "milestone"`:**
   - Glob `project/.claude/phases/**/m<N>-*.summary.md` matching the target ID.
   - If 0 matches → abort with: `No summary exists for <M#>. Run /bnac-milestone complete <M#> first to generate one.`
   - Read `milestone-status.md` and confirm the milestone is `Approved`. If not → abort with: `<M#> is not Approved (status: <X>). Refresh only works on Approved milestones.`
   - Delegate to `bnac-context-compactor` with `{mode: "milestone", target: "<M#>", trigger: "refresh"}`.
4. **For `kind: "phase"`:**
   - Resolve the phase folder via Glob `project/.claude/phases/<folder>/`. If folder doesn't exist → abort with: `No such phase folder: <folder>.`
   - Read `project/.claude/phases/index.md` and confirm every milestone in this phase is `Approved` AND the phase itself is `Approved`. If either condition fails → abort with: `Phase <folder> is not fully Approved. Refresh only works on Approved phases; run /bnac-phase complete <folder> first.`
   - Delegate to `bnac-context-compactor` with `{mode: "phase", target: "<folder>", trigger: "refresh"}`.
5. **For `kind: "all"`:**
   - Glob every `*.summary.md` under `project/.claude/phases/**`.
   - Group by kind (milestone vs phase) per filename pattern.
   - For each Approved milestone with an existing milestone summary, delegate `{mode: "milestone", target: "<M#>", trigger: "refresh"}`.
   - For each Approved phase with an existing `index.summary.md`, delegate `{mode: "phase", target: "<folder>", trigger: "refresh"}`.
   - Each delegation produces a fresh summary; `carry-forward.md` is rebuilt once at the end (the compactor pairs each summary write with a stitch; the final rebuild reflects the cumulative state).
6. **Collect** the compactor's per-target output (file path, token count, retries) and emit a combined report.
7. **Edit** `project/.claude/log.md`: append a `command` entry with action `/bnac-context refresh <target>`, list of summaries refreshed, total tokens, carry-forward rebuilt stats, timestamp.

### When action = `show`

1. **Read** `project/.claude/context/carry-forward.md`.
2. If the file doesn't exist, print: `No carry-forward yet. Run /bnac-milestone start <M#> first to bootstrap the subsystem.` and exit.
3. If the file exists but is empty, print: `carry-forward.md is empty — no completed milestones to stitch. Run /bnac-milestone complete <M#> after closing your first milestone.` and exit.
4. **Print** the file contents verbatim to stdout. Optionally precede with a one-line freshness header from the `Last rebuilt:` line for quick orientation.
5. **Do NOT log.** `show` is a read-only inspection; logging it would pollute `log.md` on every glance.

### When action = `load`

1. **Verify** `project/.claude/context/` exists. If not, abort with: `No carry-forward subsystem yet. Run /bnac-milestone start <M#> first.`
2. **Verify** `project/.claude/milestone-status.md` exists and has an `active:` frontmatter field. If not, abort with: `No active milestone — nothing to stitch. Run /bnac-milestone start <M#> first.`
3. **Delegate to `bnac-context-compactor`** with `{mode: "stitch-only", target: null, trigger: "refresh"}`. The compactor:
   - Re-reads every `*.summary.md` under `phases/**`
   - Re-applies the stitching algorithm per `context-carry-forward` skill
   - Active milestone becomes a pointer line
   - Phase summaries replace child milestone summaries where present (CMM-D4 precedence)
   - Writes `project/.claude/context/carry-forward.md` and `load-manifest.json`
4. **Collect** the compactor's stats (blocks included, blocks elided, total tokens, stale count).
5. **Output** the rebuild summary.
6. **Edit** `project/.claude/log.md`: append a `command` entry with action `/bnac-context load`, included/elided counts, total tokens, timestamp.

### When action = `check-stale`

1. **Verify** `project/.claude/context/` exists. If not, abort with: `No carry-forward subsystem yet. Run /bnac-milestone start <M#> first.`
2. **Delegate to `bnac-context-compactor`** with `{mode: "check-stale", target: null, trigger: "refresh"}`. The compactor:
   - Globs every `*.summary.md` under `phases/**`
   - For each, parses its Artifacts section and runs `git log -1 --format=%ct -- <path>` per artifact (falls back to filesystem mtime if git is unavailable)
   - Compares each artifact's mtime to the summary file's own mtime
   - Marks the summary stale if any artifact is newer
   - Emits a report; **does NOT write any file**
3. **Print** the compactor's stale report. Shape:
   ```
   ⚠️ Stale summaries detected (3 of 12):
   - m1-cli-scaffold.summary.md — src/bin/bnac.ts modified 2026-05-18 (summary dated 2026-05-15)
   - m3-http-helper.summary.md — 2 artifacts newer than summary
   - phase-1-foundation/index.summary.md — child milestone artifacts newer

   Run `/bnac-context refresh <M#>` to update individual summaries
   or `/bnac-context refresh all` to refresh everything.
   ```
   If no drift: print `✅ All 12 summaries are fresh (no artifacts newer than their summary file).`
4. **Do NOT log.** `check-stale` is read-only.

## Target parsing rules (for `refresh`)

`<target>` accepts any of these shapes — same parsing as `/bnac-phase`:

| Input | Resolves to |
|---|---|
| `M9`, `m9`, `M-CMM-2`, `m-cmm-2` | `{kind: "milestone", id: "<as typed, normalized>"}` |
| `phase-1-foundation`, `phase-cmm-context-memory` | `{kind: "phase", folder: "<verbatim>"}` |
| `phase-1`, `phase-cmm` (prefix match against folder list) | `{kind: "phase", folder: "<resolved folder>"}` |
| `P1`, `P-CMM`, `1`, `cmm` | `{kind: "phase", folder: "<resolved folder>"}` — match against `phases/index.md` Phase ID column, then folder Glob |
| `all`, `` (empty) | `{kind: "all"}` |

Resolution failure (no Glob match for the typed form) → abort with: `Cannot resolve "<target>". Use M<N>, m-cmm-<N>, phase-<N>-<slug>, P<N>, or "all".`

## Rules

- **`show` and `check-stale` never write** — neither files nor `log.md`. They are pure inspection.
- **`refresh` and `load` always log** — append a `command` entry per `~/.claude/rules/activity-logging.md`.
- **Refusal-on-not-Approved** — `refresh M<N>` on a non-Approved milestone, and `refresh <phase>` on a non-Approved phase, must abort. Refresh is not a substitute for completion.
- **Atomic stitch pair** — every summary write triggered by `refresh` is followed by a `carry-forward.md` rebuild. The compactor enforces this; the command does not need to re-trigger.
- **One agent** — every action routes to `bnac-context-compactor`. The stitching algorithm itself lives in the `context-carry-forward` skill, which the compactor loads; this command never invokes the skill directly.
- **Idempotency** — `refresh all` is safe to re-run; same inputs produce the same outputs (modulo the freshness timestamp).
- **Defaults are safe** — bare `/bnac-context` runs `show`, not `refresh`. Writes require an explicit action verb.

## Forward dependencies

The `{mode: "check-stale"}` payload referenced by the `check-stale` action ships in **M-CMM-4.2** — the `bnac-context-compactor` agent does not yet implement that mode at the time this command file is authored (M-CMM-4.1). Until M-CMM-4.2 lands, `/bnac-context check-stale` will hit an "unknown mode" path in the compactor. After M-CMM-4.2 + M-CMM-4.3 ship, the stale warning header in `carry-forward.md` will also be populated by the stitcher (it currently emits an empty placeholder per the skill reference).

## Distinct from `/bnac-milestone complete`

`/bnac-milestone complete <M#>` is the **lifecycle event** that produces a milestone summary for the first time — it flips milestone status to `Approved` and invokes the compactor with `{trigger: "complete"}`. `/bnac-context refresh <M#>` is the **manual re-run** for an already-Approved milestone whose summary needs regeneration (e.g., because drift was detected, or the template changed). Use `/bnac-milestone complete` once per milestone; use `/bnac-context refresh` whenever the summary needs to be redone.

## Distinct from `/bnac-phase complete`

Same relationship at phase level. `/bnac-phase complete <folder>` rolls up a fully-Approved phase the first time; `/bnac-context refresh <folder>` (or `refresh P<N>`) re-runs the rollup against the existing `index.summary.md`. Refresh requires the phase to be `Approved` in `phases/index.md`; if it isn't, run `/bnac-phase complete` first.

## Distinct from `/bnac-memory`

`/bnac-memory` manages the **typed long-term memory store** at `project/.claude/memory/` (user / feedback / project / reference facts that survive sessions). `/bnac-context` manages the **work-product compact history** at `project/.claude/context/carry-forward.md` and the sibling `.summary.md` files in `phases/**`. Different stores, different writers, different lifetimes per CMM-D9. See [memory-management rule](../rules/memory-management.md) for the boundary.

## Examples

```
/bnac-context                                   → defaults to show (print current carry-forward)
/bnac-context show                              → print project/.claude/context/carry-forward.md

/bnac-context refresh M5                        → re-run compactor on M5 summary
/bnac-context refresh M-CMM-2                   → re-run compactor on a letter-prefixed milestone
/bnac-context refresh phase-1-foundation        → re-run phase rollup
/bnac-context refresh P-CMM                     → shorthand for phase-cmm-context-memory
/bnac-context refresh all                       → refresh every Approved summary in the project
/bnac-context refresh                           → same as `refresh all` (default target)

/bnac-context load                              → force rebuild carry-forward.md (no new summaries)
/bnac-context check-stale                       → list summaries whose artifacts are newer (read-only report)

# Combined drift-repair flow:
/bnac-context check-stale                       → "m3-http-helper.summary.md is stale (2 artifacts newer)"
/bnac-context refresh M3                        → regenerates the M3 summary + rebuilds carry-forward
/bnac-context check-stale                       → "✅ All 12 summaries are fresh"
```
