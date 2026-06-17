# Stitching Strategy Reference

The full algorithm `bnac-context-compactor` runs to build `project/.claude/context/carry-forward.md`. Pseudocode + edge cases + elision rules.

## Inputs

- `phases_root` = `project/.claude/phases/`
- `milestone_status` = parsed `project/.claude/milestone-status.md` (frontmatter + Progress table)
- `phases_index` = parsed `phases_root/index.md` (phase allocation table)
- `budget_tokens` = 5000

## High-level pseudocode

```
function build_carry_forward():
    eligible_milestone, eligible_phase = collect_eligible_summaries()   # see Eligibility (below)
    active = milestone_status.active                    # e.g. "M7"

    if not eligible_milestone and not eligible_phase and not active:
        return empty_carry_forward()                    # fresh project

    stale_report = check_stale_summaries(eligible_milestone + eligible_phase)
                                                        # M-CMM-4 — placeholder until then

    skipped_children = {}                                # phase_id → [milestone_summary_paths]
    blocks = []
    for phase in phases_index.sorted_by_id():
        block = build_phase_block(phase, eligible_milestone, eligible_phase, active)
        if block:
            blocks.append(block)
        # build_phase_block records skipped children via record_skipped_children() side-effect

    stitched = render_header(active, stale_report) + "\n\n" + "\n\n".join(blocks)

    if token_count(stitched) > budget_tokens:
        stitched = elide_until_under_budget(stitched, blocks, budget_tokens)

    manifest = build_load_manifest(blocks, stale_report, stitched, skipped_children)

    write("project/.claude/context/carry-forward.md", stitched)
    write("project/.claude/context/load-manifest.json", manifest)
```

## Eligibility

Two kinds of summary files exist on disk:

| Kind | Filename pattern | Source skill | Token budget |
|---|---|---|---|
| Milestone | `m<N>-<slug>.summary.md` | `compact-milestone-template` | ≤500 |
| Phase     | `index.summary.md`        | `compact-phase-template`    | ≤1500 |

Both are siblings of their respective detail files. The eligibility function categorizes by filename and validates Approval against the right status source.

```
function collect_eligible_summaries():
    found = glob("project/.claude/phases/**/*.summary.md")
    eligible_milestone = []
    eligible_phase = []
    for path in found:
        if is_tombstoned(path):                         # body starts with <!-- TOMBSTONE: ... -->
            continue
        if not has_valid_header(path):                  # Phase/Folder, Completed, Detail must parse
            log_warning("malformed summary: " + path)
            continue
        if basename(path) == "index.summary.md":
            phase_folder = parent_dir(path)
            if not phase_is_approved(phase_folder, phases_index):
                continue                                # phase Status must be Approved in phases/index.md
            eligible_phase.append(parse_phase_summary(path))
        else:
            milestone_id = derive_milestone_id(path)    # m5-slim-core.summary.md → "M5"
            if not is_approved(milestone_id, milestone_status):
                continue                                # status must be Approved in milestone-status.md
            eligible_milestone.append(parse_milestone_summary(path))
    return eligible_milestone, eligible_phase
```

## Phase summary precedence rule (M-CMM-3)

When a phase has both `index.summary.md` AND a status of `Approved` in `phases/index.md`, **the phase summary fully replaces the per-milestone summaries for that phase** in the stitched output. The stitcher does NOT inline child milestone summaries in addition to the phase summary — it inlines the phase summary alone.

This is the headline behavior of M-CMM-3: as a phase completes, its carry-forward footprint collapses from N milestone summary blocks to one phase summary block.

Implications:

- The per-milestone `.summary.md` files stay on disk forever (CMM-D10 opt-up access for debugging) — they're skipped from default stitching, not deleted.
- A milestone summary in an `Approved` phase is **only** loaded when the phase summary is missing (Case 2 below — temporary state between "last milestone Approved" and "phase rolled up via `/bnac-phase complete`").
- `load-manifest.json` records the skipped milestone summaries under `child_milestone_summaries_elided_in_favor_of_phase` so downstream tooling can audit what was traded away.

## Phase block construction

This is the heart of the stitcher — for each phase, decide which strategy to use.

```
function build_phase_block(phase, eligible_milestone, eligible_phase, active):
    phase_status = phase_status_in_index(phase)         # "Approved" | "In Progress" | "Not Started"
    phase_summary_path = phase.folder + "/index.summary.md"
    phase_summary = find_phase_summary(phase.id, eligible_phase)
    child_summaries = [s for s in eligible_milestone if s.phase == phase.id]

    # Case 1: phase fully done AND phase summary exists → use phase summary ONLY
    # (child milestone summaries are SKIPPED — the phase summary replaces them)
    if phase_status == "Approved" and phase_summary is not None:
        block = render_phase_summary_block(phase, phase_summary)
        record_skipped_children(phase.id, child_summaries)   # for load-manifest
        return block

    # Case 2: phase fully done BUT no phase summary yet → use milestone summaries; warn
    # (transient state — exists only between the last milestone being Approved
    #  and the user running `/bnac-phase complete`)
    if phase_status == "Approved" and phase_summary is None:
        block = render_header_for_phase(phase, status="Approved (no phase summary)")
        for s in child_summaries.sorted_by_milestone_id():
            block += render_milestone_summary_block(s)
        block += "\n> ⚠️ Phase is Approved but `index.summary.md` is missing. Run `/bnac-phase complete " + phase.folder + "` to roll up.\n"
        return block

    # Case 3: phase in progress → milestone summaries for completed, pointer for active
    # (phase summary is NEVER loaded for in-progress phases even if one somehow exists
    #  — it would misrepresent the still-evolving phase state)
    if phase_status == "In Progress":
        block = render_header_for_phase(phase, status="In Progress")
        for milestone in phase.milestones_in_order():
            if milestone.id == active:
                block += render_active_pointer(milestone)
            elif is_approved(milestone.id, milestone_status):
                s = find_summary(milestone.id, child_summaries)
                if s:
                    block += render_milestone_summary_block(s)
                else:
                    block += render_missing_summary_warning(milestone)
            # else: milestone not started yet — skip silently
        return block

    # Case 4: phase not started → single-line placeholder
    if phase_status == "Not Started":
        return render_not_started_placeholder(phase)

    return None
```

### Decision matrix

| Phase status | `index.summary.md` exists? | Child milestone summaries loaded? | Phase summary loaded? | Stale-check outcome | Header prepended |
|---|---|---|---|---|---|
| `Approved` | yes | **No** (skipped, recorded as elided) | Yes | `stale_count == 0` | _(none)_ |
| `Approved` | yes | **No** (skipped, recorded as elided) | Yes | `stale_count > 0` | `> [!WARNING] Stale summaries detected` (+ optional non-git note above) |
| `Approved` | no  | Yes (all eligible children) + warning to run `/bnac-phase complete` | No | any | Per `stale_count` rule above |
| `In Progress` | yes (stale — shouldn't happen but defensive) | Yes (Approved children only) + pointer for active | No | any | Per `stale_count` rule above |
| `In Progress` | no  | Yes (Approved children only) + pointer for active | No | any | Per `stale_count` rule above |
| `Not Started` | n/a | No | No | n/a (no summaries to check) | _(none)_ |
| _(any)_ | _(any)_ | _(any)_ | _(any)_ | check-stale errored | `> [!NOTE] Drift check unavailable this run` (stitcher continues — see edge cases) |

## Renderers

### Phase summary block

```markdown
## Phase {N}: {Title} (Approved)

{inline contents of phases/phase-{N}-{slug}/index.summary.md, skipping its own H1}
```

### Milestone summary block

```markdown
### M{N} — {Title} (Approved {YYYY-MM-DD})

{inline contents of phases/phase-{N}-{slug}/m{N}-{slug}.summary.md, skipping its own H1}
```

The H1 of each summary file is stripped during inlining because we use H2/H3 for stitched sections; otherwise heading hierarchy gets confused.

### Active milestone pointer

```markdown
### M{N} — {Title} (In Progress — ACTIVE)

_Active milestone — detail loaded separately via `milestone-status.md`. See [m{N}-{slug}.md](../phases/phase-{N}-{slug}/m{N}-{slug}.md)._
```

### Missing summary warning

```markdown
### M{N} — {Title} (Approved, summary missing)

_⚠️ Milestone is marked Approved in `milestone-status.md` but `.summary.md` file is missing. Run `/bnac-context refresh M{N}` to generate it._
```

### Not-started placeholder

```markdown
## Phase {N}: {Title} (Not Started)

_(no completed milestones — not yet loaded)_
```

## Elision

When stitched output exceeds `budget_tokens` (5000):

```
function elide_until_under_budget(stitched, blocks, budget):
    elided_phases = []
    while token_count(stitched) > budget and any_complete_phase_remains(blocks):
        oldest_complete = find_oldest_phase_with_no_active_milestone(blocks)
        blocks = replace_with_elision_marker(blocks, oldest_complete)
        elided_phases.append(oldest_complete.id)
        stitched = re_render(blocks)

    # If still over budget after eliding all complete phases, elide oldest completed milestones
    # in any phase (preserving the active milestone block)
    while token_count(stitched) > budget:
        oldest_milestone = find_oldest_completed_milestone_block(blocks)
        if not oldest_milestone:
            break                                       # nothing left to elide; budget is wrong or summaries are too large
        blocks = elide_single_milestone(blocks, oldest_milestone)
        stitched = re_render(blocks)

    if token_count(stitched) > budget:
        # Last resort — truncate from end and add hard-truncation marker
        stitched = truncate_to_budget(stitched, budget) + truncation_marker()

    return stitched, elided_phases
```

### Phase elision marker

```markdown
## Phase {N}: {Title} (Approved) — Elided

_{M} milestone summaries omitted to fit budget. See [phases/phase-{N}-{slug}/](../phases/phase-{N}-{slug}/) for the full record._
```

### Single-milestone elision marker (within an in-progress phase)

```markdown
### M{N} — {Title} (Approved) — Elided

_Summary omitted to fit budget. See [m{N}-{slug}.summary.md](../phases/phase-{N}-{slug}/m{N}-{slug}.summary.md)._
```

### Hard-truncation marker (last resort)

```markdown
> ⚠️ Carry-forward exceeded budget after eliding. Output truncated. Run `/bnac-context show` to see what's loaded; consider reducing summary sizes.
```

## Top header rendering

```markdown
# Carry-Forward Context

> Auto-stitched by `bnac-context-compactor` from completed `.summary.md` files.
> Loaded per `~/.claude/rules/context-first.md` step 6.
> Last rebuilt: {YYYY-MM-DD HH:mm}. Active milestone: M{N} — {Title}.

---
```

The active-milestone line is `(none)` if no milestone is active yet (e.g., fresh project pre-M1).

## Stale warning rendering (placeholder until M-CMM-4)

When `check_stale_summaries()` returns non-empty:

```markdown
> ⚠️ Stale summaries detected ({M} of {N}):
> - `{summary-file}` — artifact `{path}` modified {YYYY-MM-DD} (summary dated {YYYY-MM-DD})
> - ... up to 5 lines, then "+ K more, run `/bnac-context check-stale` for full list"
>
> Run `/bnac-context refresh` to update affected summaries.
```

Until M-CMM-4 ships, `check_stale_summaries()` returns empty; this block is omitted.

## Stale-warning surfacing (M-CMM-4.3)

This section defines the third stitching concern: when and how drift-check results are surfaced as a warning header in `carry-forward.md`.

### When the check runs

Before the stitcher writes (or overwrites) `carry-forward.md`, it invokes the compactor's `check-stale` procedure in **summary mode** — consuming only the count and stale ID list, not the full markdown report. The exact invocation payload is:

```
mode: "check-stale"
target: null
trigger: "refresh"
```

The stitcher consumes a reduced struct from the compactor's check-stale result — NOT the full markdown report:

```
{
  stale_count: number,          // total summaries flagged stale
  stale_ids: string[],          // IDs/slugs of stale summaries (e.g. "M9", "M-CMM-2", "phase-1-foundation")
  unknown_artifact_count: number, // count of summaries with unknown/missing artifacts (never triggers warning — see below)
  non_git_banner: bool          // true if project is not a git repo and filesystem mtime fallback was used
}
```

This check runs on EVERY stitch — including `stitch-only`, `milestone`, and `phase` modes. It is the stitcher's responsibility to invoke it as the first step of `render_header()`.

### Warning block shape

When `stale_count > 0`, the following block is **prepended** to `carry-forward.md`, before the top header and before any phase content:

```markdown
> [!WARNING] Stale summaries detected
> N summaries may be out of date — their listed artifacts have newer git mtimes than the summary itself.
> Stale: M9, M-CMM-2, phase-1-foundation
> Run `/bnac-context refresh <id>` to update one, or `/bnac-context refresh all` to refresh everything.
> Run `/bnac-context check-stale` for the full report.
```

Where:
- `N` is `stale_count`
- The `Stale:` line lists the first 5 IDs from `stale_ids[]`, comma-separated. If `stale_ids.length > 5`, append ` … +K more` where `K = stale_ids.length - 5`. Example with 8 stale: `Stale: M1, M3, M5, M-CMM-2, phase-1-foundation … +3 more`

### Non-git banner pass-through

If the compactor's check-stale step sets `non_git_banner: true` (the project is not a git repository and fell back to filesystem mtime), the stitcher prepends an **additional** `> [!NOTE]` block ABOVE the stale warning block — before even the `[!WARNING]` block:

```markdown
> [!NOTE] Filesystem mtime fallback active
> This project is not a git repository. Drift detection fell back to filesystem mtime.
> Filesystem mtime is less reliable than git mtime — it resets on checkout or `touch`.
> Stale flags below may be inaccurate. Consider initializing a git repo for reliable drift detection.
```

This wording matches the non-git banner the compactor emits at the top of its own check-stale report (see `bnac-context-compactor.md` `check-stale` procedure step 2) so the two surfaces stay consistent.

### Unknown / missing artifacts

Summaries whose artifacts have `unknown` classification (file deleted or renamed — `git log` returned empty AND file does not exist on disk) do NOT trigger the `[!WARNING]` block. This is a strict application of the **`unknown ≠ stale`** rule established in M-CMM-4.2 (see `bnac-context-compactor.md` Rules: "Unknown artifacts are not stale"). The `unknown_artifact_count` field is carried in the struct purely for transparency; the stitcher does not act on it. For the full list of unknown / missing artifacts, users should run `/bnac-context check-stale` which renders the dedicated "Unknown / missing artifacts" table.

### Idempotency

The warning block (both the `[!WARNING]` block and, if present, the preceding `[!NOTE]` non-git block) is **regenerated on every stitch**. It is never duplicated.

Before writing new content, the stitcher strips any prior stale-warning header from an existing `carry-forward.md`. Stripping rule: remove the leading contiguous `>` block(s) that begin with `> [!NOTE] Filesystem mtime fallback active` or `> [!WARNING] Stale summaries detected` (whichever is present), along with any blank lines between them and the first non-`>` line. The fresh result from the current stitch run replaces them (or is omitted entirely if `stale_count == 0` in the new run).

This ensures that a project that corrects drift (via `/bnac-context refresh all`) will have a clean `carry-forward.md` header on the next stitch — no stale warning, no ghost of the prior warning.

### Performance note

The embedded check-stale call uses the same Bash `git log -1 --format=%ct -- <path>` per-file probe as the standalone `/bnac-context check-stale` command. On projects with a small number of summary files (typical: 5–30), this overhead is negligible — a handful of Bash spawns. On projects with thousands of `.summary.md` files, however, the per-file `git log` probes add up to a measurable cost at every stitch.

If a project hits a scale where the stitch is noticeably slow, the stitcher MAY skip the check-stale call entirely and instead emit a static fallback note:

```markdown
> [!NOTE] Stale checks skipped on stitch — run `/bnac-context check-stale` to check for drift manually.
```

This is framed as a **future opt-out hook**, not a current implementation requirement. The threshold for "too slow" is project-specific and should be configurable (e.g., a `skip_stale_check_above: N` field in `load-manifest.json`'s configuration section). Until such a hook is implemented, the check always runs.

## Edge cases

| Case | Behavior |
|---|---|
| No phases folder exists | Write `# Carry-Forward Context\n\n_No phases yet. Run `/bnac-plan` to begin._` |
| Phases folder exists but no summary files yet | Write header + per-phase "Not Started" placeholders |
| Phase folder exists but no `index.md` | Skip the phase + log a warning |
| Milestone in `milestone-status.md` but no detail file | Render "missing detail" warning per phase block |
| Active milestone ID doesn't match any phase | Render top-level warning + skip pointer line; do not crash |
| Two summaries claim the same milestone ID | Use the lexicographically first; warn |
| Letter-prefixed phase IDs (e.g., `phase-cmm-*`) | Sort: numeric phases first by N, then letter-prefixed alphabetically |
| Phase `index.summary.md` exists but `phases/index.md` shows phase `In Progress` | Defensive: do NOT load the phase summary (Case 3 path); the stale summary likely predates a milestone re-open. Warn in the rebuild log. |
| Phase `index.summary.md` exists and phase is `Approved` but one milestone in the phase has just been re-opened to `In Progress` | The phase status `Approved` is now wrong — caller should flip it back to `In Progress` and run `/bnac-context refresh`. Until then the stitcher trusts `phases/index.md` and loads the stale phase summary; recommend running `/bnac-context refresh` after re-opening any milestone in an `Approved` phase. |
| All stale summaries belong to one `Approved` phase whose `index.summary.md` is used instead of child milestone summaries | The phase summary is itself subject to the same drift check. If any artifact listed in the phase summary's Artifacts section is newer than the phase summary's mtime, the phase summary is marked stale and the warning block surfaces with the phase ID listed under `Stale:`. The fact that child milestone summaries were elided in favour of the phase summary does not exempt the phase summary from the check — it is a summary like any other. |
| The active milestone's own summary is stale (it should not have a summary since it is rendered as a pointer line, but a leftover `.summary.md` from a prior Approved state may exist on disk) | The active milestone's `.summary.md` is not included in the carry-forward stitch (it is replaced by a pointer line). The check-stale probe therefore does NOT run against it. Even if the file exists and its artifacts are newer, no stale warning is emitted for the active milestone — it is excluded from the eligible-summaries list before the check runs. |
| `check-stale` itself errored during the embedded stitch call (e.g., Bash unavailable, filesystem permissions, unexpected exception from the compactor) | The stitcher MUST NOT fail the entire stitch due to a drift-check error. Continue the stitch without stale data and prepend a single informational note instead of the warning block: `> [!NOTE] Drift check unavailable this run — stale summaries may be present. Run \`/bnac-context check-stale\` manually.` Log the check-stale error to `log.md` as a warning-level entry. Never surface a raw stack trace in `carry-forward.md`. |

## Determinism

Same inputs MUST produce same output. Sources of non-determinism to control:

- **Glob order** — sort results before iterating
- **Map iteration** — never iterate dict/object keys directly; always sort
- **Timestamp in header** — the "Last rebuilt" line; this is the ONLY line that legitimately changes between runs with identical inputs (and that's by design — it's a freshness indicator)

The `load-manifest.json` is sorted by `included_summaries[*].milestone` to make diffs readable.

### load-manifest.json shape (M-CMM-3 addition)

The manifest records what was loaded AND what was deliberately skipped because a phase summary took precedence:

```json
{
  "rebuilt_at": "2026-05-21T14:32:11Z",
  "active_milestone": "M7",
  "included_phase_summaries": [
    { "phase": "phase-1-foundation", "file": "phases/phase-1-foundation/index.summary.md", "tokens": 720 }
  ],
  "included_milestone_summaries": [
    { "milestone": "M5", "phase": "phase-2-vertical", "file": "phases/phase-2-vertical/m5-slim-core.summary.md", "tokens": 410 },
    { "milestone": "M6", "phase": "phase-2-vertical", "file": "phases/phase-2-vertical/m6-context.summary.md", "tokens": 380 }
  ],
  "child_milestone_summaries_elided_in_favor_of_phase": {
    "phase-1-foundation": [
      "phases/phase-1-foundation/m1-cli-scaffold.summary.md",
      "phases/phase-1-foundation/m2-install-engine.summary.md",
      "phases/phase-1-foundation/m3-claude-adapter.summary.md",
      "phases/phase-1-foundation/m4-global-entry.summary.md"
    ]
  },
  "elided_for_budget": [],
  "total_tokens": 1510,
  "budget_tokens": 5000
}
```

The `child_milestone_summaries_elided_in_favor_of_phase` field is what makes the phase precedence rule auditable — at a glance, future readers can see which milestone summaries are on disk but not loaded.

## When to NOT rebuild

The compactor should NOT rebuild if:

- The trigger is `start` and no completed milestones exist yet (nothing to stitch)
- The trigger is `complete` but the completed milestone's summary write failed (rebuild would propagate the broken state)
- The trigger is `refresh` with a specific milestone ID and that ID isn't completed (refuse + report)

In these cases, log the reason and skip the write. The previous `carry-forward.md` stays in place.
