---
name: compact-phase-template
description: Canonical structure for phase compact summaries — the ≤1500-token `index.summary.md` written next to a phase's `index.md` when the phase is rolled up via `/bnac-phase complete`. Used by bnac-context-compactor (phase mode). Hard token budget; 6-section template; sourced from the phase's milestone *detail* files (NOT milestone summaries — CMM-D4), the phase's `index.md`, log.md slice for the phase period, and optional git diff.
user-invocable: false
argument-hint: ""
---

Define the canonical shape of a phase compact summary: a token-budgeted (`≤ 1500 tokens`) sibling file named `index.summary.md` next to a phase's `index.md` that captures the *why* and *what* of a completed phase without re-listing every milestone's full detail.

## Additional resources

- [reference/phase-summary-format.md](reference/phase-summary-format.md) — full section-by-section format, examples, and the over-budget retry protocol

## On-disk shape (NON-NEGOTIABLE)

Phase summaries are **siblings** of the phase's `index.md` (per CMM-D1, mirroring the milestone-summary layout):

```
project/.claude/phases/phase-1-foundation/
├── index.md                    ← phase detail (stays untouched)
├── index.summary.md            ← phase compact summary (this skill defines its shape)
├── m1-cli-scaffold.md
├── m1-cli-scaffold.summary.md
├── m2-install-engine.md
└── m2-install-engine.summary.md
```

Glob pattern for all phase summaries: `**/index.summary.md`.
Glob pattern for all summaries (milestone + phase): `**/*.summary.md`.

## Token budget (HARD)

- **Target:** ≤1500 tokens (~6000 characters)
- **Hard reject:** if `bnac-context-compactor` produces a summary >1500 tokens, it retries once with "compress Architecture decisions to 5 most load-bearing, bundle Public surface, trim Carried-forward debt"; final fallback truncates from the bottom and adds a `> ⚠️ Truncated — see phase detail + per-milestone summaries` marker

Token counting: same word-count proxy as the milestone template (1 token ≈ 0.75 words). Counting must be **conservative** — when in doubt, assume more tokens.

## Required sections (in order)

```markdown
# Phase <ID> Summary: <Title>

**Folder:** phase-<N>-<slug>
**Completed:** YYYY-MM-DD
**Detail:** [index.md](index.md)

## Goal + outcome
<one to two lines — what the phase produced, in outcome terms (not work terms)>

## Milestones rolled up
| ID | Title | Status | Key artifact |
|----|-------|--------|--------------|
| M<a> | <title> | Approved YYYY-MM-DD | `path/to/main/deliverable` |
| ...  | ...     | ...                 | ...                        |

## Architecture decisions (cross-milestone)
- **<decision name>** — <one-line summary of the choice>. **Why:** <reason — constraint, prior incident, deliberate tradeoff>.
- (3–7 bullets — these are the load-bearing decisions other phases depend on)

## Public surface introduced
- `path/to/module.ext` — `<exported symbol or API signature, one line>`
- (modules, exports, paths the rest of the project can depend on — signatures only)

## Carried-forward debt / open questions
- <one line per item — what later phases still owe>
- (≤5 lines total; "- None." if truly nothing)
```

## Section caps (enforced)

| Section | Cap |
|---|---|
| Goal + outcome | 1–2 lines |
| Milestones rolled up | one table row per milestone, ≤1 line per row |
| Architecture decisions | 3–7 bullets, each ≤2 lines |
| Public surface introduced | ≤12 entries, each ≤1 line (bundle similar modules) |
| Carried-forward debt | ≤5 lines total |

If a phase genuinely produced more than these limits, **bundle similar items** (e.g., "8 install-state helpers under `src/scripts/lib/install-*.ts`" as one Public surface line). Exceeding caps is a signal that the phase was too broad — escalate, don't pad.

## What to source from

Per CMM-D4, the compactor builds a phase summary from **primary sources**, NOT summary-of-summaries:

1. **Phase `index.md`** — goal, exit criterion, milestone allocation, agents involved, cross-phase risks
2. **Every milestone *detail* `m<N>-<slug>.md` in the phase** — Goal, Key decisions, Deliverables, Acceptance criteria, Risks (NOT the milestone `.summary.md` siblings — those are also derivatives)
3. **`log.md` slice** — entries whose timestamp falls between the first milestone-start and the phase-complete events (extract decision lines, results, Notes blocks containing "decision", "chose", "rejected", "Why")
4. **Git diff** (optional, when Bash is available) — files changed across the phase's commit range; supplements Public surface and helps verify Milestones rolled up

This is the explicit CMM-D4 contract: phase summary built from milestone details, not from milestone summaries. The compactor MUST refuse to read `.summary.md` files when composing a phase summary (avoids double-lossy compression).

## What NOT to include

- **No milestone-level task lists** — atomic tasks belong in milestone details
- **No quoted code bodies** — paths only, signatures only, never implementations
- **No log line excerpts** — distill into Architecture decisions bullets with **Why:**
- **No personnel mentions** — git/log have authorship; the summary is project history
- **No re-statement of the phase exit criterion** — passed = implicit; failed = phase shouldn't be summarized yet
- **No content sourced from the milestone `.summary.md` files** — CMM-D4 hard rule

## Example

```markdown
# Phase 1 Summary: Foundation

**Folder:** phase-1-foundation
**Completed:** 2026-04-30
**Detail:** [index.md](index.md)

## Goal + outcome
Package scaffolded with a working `bnac` CLI; install engine writes content idempotently with per-file checksum state; Claude adapter installs to `~/.claude/`; global entry-point files (CLAUDE.md, AGENTS.md, RULES.md) land cleanly on a fresh machine.

## Milestones rolled up
| ID | Title | Status | Key artifact |
|----|-------|--------|--------------|
| M1 | CLI scaffold & entry point | Approved 2026-04-05 | `src/bin/bnac.ts` |
| M2 | Install engine & state tracking | Approved 2026-04-12 | `src/scripts/lib/install-executor.ts` |
| M3 | Claude adapter & interactive init | Approved 2026-04-19 | `src/scripts/lib/targets/claude-home.ts` |
| M4 | Global entry-point files | Approved 2026-04-26 | `src/global/CLAUDE.md` |

## Architecture decisions (cross-milestone)
- **Manifest-driven installs, not script-driven** — `install-modules.json` + `install-profiles.json` declare what lands where; the executor is a pure function over the manifest. **Why:** keeps content authors out of TypeScript; lets `bnac doctor` diff source vs installed without re-running install logic.
- **Per-file SHA-256 checksums in `install-state.json`** — every installed file's hash is recorded; `bnac doctor` flags drift, `bnac update` diffs new vs installed. **Why:** mtime-based detection was unreliable across timezones + git-clone resets; content hashing is determinstic.
- **Adapter pattern for harness targets** — `claude-home`, `codex`, `cursor`, `augment` each implement the same adapter interface. **Why:** anticipated multi-harness support (M16) without baking Claude assumptions into the installer.
- **Atomic writes via tmp+rename in safe-fs** — every install write goes through `safeWriteFile` which writes to `<dest>.tmp` then renames. **Why:** earlier projects lost half-written state files when antivirus held a lock mid-write.
- **No `--force` flag on the installer** — drift is reported by `bnac doctor`; user must explicitly run `bnac update` or `bnac install --replace`. **Why:** silent overwrites destroyed in-progress edits twice in beta.

## Public surface introduced
- `src/bin/bnac.ts` — CLI entry point; commander-based dispatcher to `install`, `update`, `doctor`, `detect`
- `src/scripts/lib/install-executor.ts` — `executeInstallPlan(plan, target): InstallResult`
- `src/scripts/lib/install-state.ts` — `readState(target): InstallState | null`; `writeState(target, state): void`
- `src/scripts/lib/install-manifests.ts` — `loadManifest(): InstallManifest`; manifest schema in `src/types/index.ts`
- `src/scripts/lib/targets/claude-home.ts` — `claudeHomeTarget: InstallTarget`; resolves `~/.claude/` cross-platform
- `src/scripts/lib/safe-fs.ts` — `safeWriteFile`, `safeCopyFile`, `safeMkdir`, `assertSafeFilename`, `toPosix`
- `src/global/CLAUDE.md`, `src/global/AGENTS.md`, `src/global/RULES.md` — entry-point content installed to `~/.claude/`

## Carried-forward debt / open questions
- Hook runner evaluates rules but does not yet integrate with Claude Code's `settings.json` — wiring deferred to M11.
- `bnac update` does NOT delete removed files; flags them instead. Future `bnac prune` / `bnac eject` will clean.
- YAML parser is a purpose-built subset (no `js-yaml` dep) — swap for a full lib if hook schemas grow.
```

That summary is ~620 tokens — well under the 1500 budget, all 6 sections present.

## Rules

- **Stay under 1500 tokens** — hard reject + retry above
- **Build from milestone *details*, not milestone summaries** — CMM-D4 (refuse to read `.summary.md` files in phase mode)
- **Architecture decisions need *why*** — a bullet without a reason is a fact; the *why* lets later phases judge edge cases
- **Paths and signatures only** — never quote code bodies
- **No task lists, no people, no log excerpts** — those have their own files
- **One file per phase** — `index.summary.md`, sibling of `index.md`
- **Phase detail (`index.md`) stays untouched** — summary is additive; never modifies the detail
- **Milestones rolled-up table is mandatory** — even a single-milestone phase gets the table (with one row)
- **Phase summary replaces — never supplements — child milestone summaries in carry-forward stitching** — see [context-carry-forward/reference/stitching-strategy.md](../context-carry-forward/reference/stitching-strategy.md)
