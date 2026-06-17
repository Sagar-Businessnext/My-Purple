---
name: context-carry-forward
description: How `bnac-context-compactor` assembles `project/.claude/context/carry-forward.md` from completed milestone/phase `.summary.md` files. Defines the stitching algorithm, ordering, eligibility rules, token-budget enforcement (≤5000 total), and stale-warning header. Read by every agent that loads project history per context-first.md step 6.
user-invocable: false
argument-hint: ""
---

Define how `project/.claude/context/carry-forward.md` is built — the auto-stitched compact-history file that loads on every session per [context-first.md](../../rules/context-first.md) step 6.

## Additional resources

- [reference/stitching-strategy.md](reference/stitching-strategy.md) — full pseudocode for the stitch, edge cases, sort order, elision rules when over budget

## On-disk shape

```
project/.claude/context/
├── carry-forward.md           ← stitched compact history (this skill defines its shape)
└── load-manifest.json         ← internal — tracks which summaries were included and when
```

There is **no `compact/` or `history/` subfolder**. Summary files themselves live next to their detail in `phases/phase-<N>-<slug>/`; this skill's job is to stitch them into one loadable document.

## Sources

The stitcher reads:

1. **All `*.summary.md` files** under `project/.claude/phases/**`
2. **Active milestone pointer** from `project/.claude/milestone-status.md` (frontmatter `active:` field)
3. **`phases/index.md`** to determine phase ordering and completion status

It does NOT read:
- Milestone detail `.md` files (those are loaded directly by agents when needed per the opt-up guard)
- `log.md` (different lifecycle — actions, not history)
- `memory/` (different store — facts, not work product)

## Token budget (HARD)

- **Target total:** ≤5000 tokens for the entire `carry-forward.md`
- **When exceeded:** elide oldest milestone summaries first, replacing each with a single pointer line (see [reference/stitching-strategy.md](reference/stitching-strategy.md) for the elision algorithm)

## Stitched output shape

```markdown
# Carry-Forward Context

> Auto-stitched by `bnac-context-compactor` from completed `.summary.md` files.
> Loaded per `~/.claude/rules/context-first.md` step 6.
> Last rebuilt: YYYY-MM-DD HH:mm. Active milestone: M<N> — <Title>.

---

{{stale_warnings_if_any}}

## Phase 1: Foundation (Approved)

{inline phase summary if `phases/phase-1-foundation/index.summary.md` exists}
                                — OR —
{inline each milestone summary if phase is not yet complete}

## Phase 2: Vertical Slice (In Progress)

### M5 — Slim Core (Approved)
{inline `m5-slim-core.summary.md`}

### M6 — Project Context (Approved)
{inline `m6-project-context.summary.md`}

### M7 — React Stack (In Progress — ACTIVE)
_Active milestone — detail loaded separately. See `phases/phase-2-vertical-slice/m7-react-stack.md`._

## Phase 3: Pipeline (Not Started)
_(no completed milestones — not yet loaded)_
```

## Stitching rules

### Phase-level vs. milestone-level inclusion

For each phase, pick ONE of these strategies based on its status:

| Phase status | Strategy |
|---|---|
| **Approved** (all milestones Approved AND `index.summary.md` exists) | Load `phases/phase-<N>-<slug>/index.summary.md` inline; skip child milestone summaries |
| **Approved** (all milestones Approved, no phase summary yet) | Load each child `*.summary.md` inline; warn user to run `/bnac-phase complete` |
| **In Progress** | Load only completed child `*.summary.md`s; for the active milestone, write a pointer line ("Active — detail loaded separately") |
| **Not Started** | Skip entirely; write a single "Not yet loaded" placeholder line |

Per CMM-D4: phase summaries (when present) replace their child milestone summaries — not augment them.

### Section ordering

- Phases in numeric order (or letter order if letter-prefixed, e.g., `phase-cmm-*`)
- Within a phase, milestones in their listed order from `phases/index.md`'s allocation table
- Newest information is **NOT** at the top; chronological order is the contract so readers can trace the project's evolution

### Active milestone handling

The currently-active milestone is **NEVER** summarized in `carry-forward.md` — only a pointer line:

```markdown
### M<N> — <Title> (In Progress — ACTIVE)
_Active milestone — detail loaded separately. See [m<N>-<slug>.md](../phases/phase-<N>-<slug>/m<N>-<slug>.md)._
```

The agent already loads the active milestone's detail via the existing milestone-status.md chain (context-first step 4). Carry-forward should not duplicate it.

### Stale warnings (CMM-D7 / M-CMM-4)

Before stitching, the compactor runs `check-stale` on every summary slated for inclusion. If any are stale (git mtime of an artifact is newer than the summary's mtime), it prepends a warning block:

```markdown
> ⚠️ Stale summaries detected (3 of 12):
> - `m1-cli-scaffold.summary.md` — artifact `src/bin/bnac.ts` modified 2026-05-18 (summary dated 2026-05-15)
> - `m3-http-helper.summary.md` — 2 artifacts newer than summary
> - `m4-state-tracking.summary.md` — artifact `src/scripts/lib/state.ts` modified after summary
>
> Run `/bnac-context refresh` to update affected summaries.
```

(Drift detection ships in M-CMM-4. Until then, the stale warning header is just a placeholder — `## Stale warnings` section is omitted.)

## Rebuild triggers

`carry-forward.md` is rebuilt whenever:

| Trigger | Invoked by |
|---|---|
| Milestone completed (`/bnac-milestone complete`) | `bnac-milestone-tracker` → delegates to `bnac-context-compactor` |
| Milestone activated (`/bnac-milestone start <M#>`) | `bnac-milestone-tracker` → delegates to `bnac-context-compactor` |
| Phase completed (`/bnac-phase complete`) | `bnac-phase-tracker` → delegates to `bnac-context-compactor` (added in M-CMM-3) |
| Manual refresh (`/bnac-context refresh`) | `bnac-context-compactor` directly (added in M-CMM-4) |

The compactor is responsible for the rebuild; tracker agents only trigger it. The stitch happens after detail files are updated, so it always reflects the post-action state.

## Load manifest

`project/.claude/context/load-manifest.json` tracks what's in the current carry-forward:

```json
{
  "rebuilt_at": "2026-05-21T14:30:00Z",
  "active_milestone": "M7",
  "included_summaries": [
    {
      "phase": "phase-1-foundation",
      "kind": "phase",
      "file": "phases/phase-1-foundation/index.summary.md",
      "size_tokens": 1340
    },
    {
      "phase": "phase-2-vertical-slice",
      "kind": "milestone",
      "milestone": "M5",
      "file": "phases/phase-2-vertical-slice/m5-slim-core.summary.md",
      "size_tokens": 420
    }
  ],
  "elided": [],
  "total_tokens": 1760,
  "budget": 5000,
  "stale_count": 0
}
```

`/bnac-context show` reads this to report state without re-parsing the stitched output.

## Eligibility rules

A `.summary.md` is **eligible** for inclusion if:

- [ ] Its parent milestone's status in `milestone-status.md` is `Approved`
- [ ] The summary file exists and is non-empty
- [ ] The summary's frontmatter-equivalent header (`Phase`, `Completed`, `Detail`) parses cleanly
- [ ] The summary is not marked tombstone (`<!-- TOMBSTONE: ... -->`)

A `.summary.md` is **excluded** if:

- Its milestone is the active one (use pointer line instead)
- Its phase's `index.summary.md` exists AND the phase is Approved (use phase summary instead)
- Its parent phase is Not Started (skip the whole phase block)

## Token-budget enforcement

If sum of included summaries > 5000 tokens:

1. **Elide phase by phase, oldest first** — replace an entire phase block with:
   ```markdown
   ## Phase 1: Foundation (Approved) — Elided
   _3 milestone summaries omitted to fit budget. See [phases/phase-1-foundation/](../phases/phase-1-foundation/) for full record._
   ```
2. Update `load-manifest.json`'s `elided` array
3. If still over budget after eliding all complete phases, elide oldest milestones within active phases

The full record stays on disk — elision is purely about the stitched view.

## Rules

- **Active milestone is a pointer, never a block** — its detail loads separately
- **Phase summary REPLACES milestone summaries when present** — never both for the same phase
- **Chronological order** — phases in numeric/letter order, milestones in plan order; never re-sort by recency
- **Hard token budget** — elide before exceeding 5000
- **Rebuild is idempotent** — same inputs always produce same output (deterministic)
- **Stale warnings at top** — surfaced as a quote block before any phase content
- **Sources are summary files only** — never load detail `.md` into carry-forward (defeats the purpose)
- **Load manifest mirrors stitched state** — JSON is the audit trail; the stitched MD is the consumed artifact
