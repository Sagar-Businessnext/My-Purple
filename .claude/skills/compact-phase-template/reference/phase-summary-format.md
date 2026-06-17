# Phase Summary Format Reference

Section-by-section spec for the `index.summary.md` sibling file. This is what `bnac-context-compactor` produces in phase mode.

## Required fields

| Field / Section | Required | Notes |
|---|---|---|
| `# Phase <ID> Summary: <Title>` | yes | Heading — phase ID (e.g., `Phase 1`, `Phase CMM`) + same title as `index.md` |
| `Folder` | yes | `phase-<N>-<slug>` (must match parent folder name) |
| `Completed` | yes | `YYYY-MM-DD` — the date the phase was marked Approved in `phases/index.md` |
| `Detail` | yes | Markdown link to the sibling `index.md` |
| `## Goal + outcome` | yes | 1–2 lines in outcome terms ("Package installs cleanly on a fresh machine") not work terms ("Wrote installer") |
| `## Milestones rolled up` | yes | Table — one row per milestone in the phase, all rows MUST be `Approved` |
| `## Architecture decisions (cross-milestone)` | yes | 3–7 bullets with **Why:** — choices that span >1 milestone or set patterns for later phases |
| `## Public surface introduced` | conditional | Required if the phase produced exported APIs / modules / paths; omit for internal-only phases |
| `## Carried-forward debt / open questions` | yes | ≤5 lines; write `- None.` if genuinely nothing |

## Section-by-section guidance

### Header (frontmatter-free)

No YAML frontmatter on phase summary files — like milestone summaries, they get inlined into `carry-forward.md` as Markdown blocks and frontmatter would pollute the output.

```markdown
# Phase <ID> Summary: <Title>

**Folder:** phase-<N>-<slug>
**Completed:** YYYY-MM-DD
**Detail:** [index.md](index.md)
```

Phase IDs can be numeric (`Phase 1`, `Phase 2`) or letter-prefixed (`Phase CMM`, `Phase P3`). The heading mirrors the heading in `index.md`.

### `## Goal + outcome`

1–2 lines, **outcome-shaped**. Pull from the phase's `index.md` Goal field and rewrite if it's work-shaped.

| Good | Bad |
|---|---|
| "Users can authenticate via email + password; sessions persist across reload" | "Implemented authentication module" |
| "Production deploys ship from green main on every merge" | "Wrote CI/CD configs" |
| "Project context (memory + carry-forward) ships and survives session resets" | "Built memory and compaction subsystems" |

If the original phase Goal was work-shaped, **rewrite it** for the summary. The detail file (`index.md`) stays untouched.

### `## Milestones rolled up`

A table — one row per milestone, in milestone-ID order (ascending). Required even for a single-milestone phase.

```markdown
| ID | Title | Status | Key artifact |
|----|-------|--------|--------------|
| M5 | Slim core | Approved 2026-04-22 | `src/core/agents/bnac-developer.md` |
| M6 | Project context system | Approved 2026-04-28 | `src/scripts/commands/init.ts` |
```

**Key artifact:** one path per milestone — the single most important deliverable, not a list. Pull from the milestone's Deliverables section. Bundle if the milestone produced a folder full of equivalent files (e.g., `src/core/skills/**`).

If a milestone's status is anything other than `Approved`, the phase summary should NOT have been generated — the compactor refuses in that case (per the pre-check in `/bnac-phase complete`).

### `## Architecture decisions (cross-milestone)`

This is the most important section — it's what prevents later phases from re-litigating decisions that span multiple milestones. 3–7 bullets, each:

```markdown
- **<decision label>** — <one-line summary of the choice>. **Why:** <reason — constraint, incident, deliberate tradeoff>.
```

The **Why:** is non-negotiable. A bullet without a reason becomes a fact; with a reason it becomes judgment fuel for the next phase.

What counts as a "cross-milestone" decision (vs. milestone-local):

| Cross-milestone (include) | Milestone-local (skip) |
|---|---|
| "Adapter pattern across all harness targets" (M3, M16 both use it) | "Used `commander` for the CLI" (M1 only) |
| "Per-file SHA-256 checksums in install-state" (M2 establishes, M11 doctor consumes) | "M2's `walkDir` skips dotfiles" (internal to M2) |
| "Atomic writes via tmp+rename" (M2 set the pattern, M12 generalized it) | "M5 named its rule files `kebab-case.md`" (one milestone) |

Pull decisions from:
- Each milestone's "Risks" + "Key decisions" sections in the detail
- Log entries during the phase period (look for "decision", "chose", "rejected", "Why")
- The phase's own `index.md` "Decisions inherited from plan-N.md" section (if present)
- Git commit messages spanning the phase (often contain rationale)

If you can't extract 3 cross-milestone decisions, either the phase was too small (single-milestone phase — that's fine, just say so) or the milestones were too independent (also fine — note that in `Carried-forward debt`).

### `## Public surface introduced`

What the rest of the project depends on after this phase ships — exported symbols, API endpoints, public file paths, manifest entries.

```markdown
- `src/scripts/lib/install-executor.ts` — `executeInstallPlan(plan, target): InstallResult`
- `src/scripts/commands/install.ts` — CLI subcommand `bnac install [--profile <id>] [--target <id>]`
- `POST /api/v1/auth/login` — request: `{email, password}`, response: `{token, expiresAt}`
- `src/core/agents/bnac-developer.md`, `bnac-reviewer.md`, `bnac-quality-gate.md` — 3 core execution agents
```

**Signatures only.** Never include function bodies, full interface definitions, or endpoint payloads — those live in detail. Bundle when the phase shipped many similar exports:

| Verbose (bad) | Bundled (good) |
|---|---|
| 8 lines listing each `bnac-*` agent .md file | "`src/core/agents/bnac-*.md` — 8 core execution + planning agents" |

≤12 entries; if you exceed, bundle harder. If the phase was internal (no exported APIs, just refactors / tests / docs), **omit this section entirely** — don't write "None".

### `## Carried-forward debt / open questions`

≤5 lines total. Things later phases will need to revisit. Examples:

- "Hook runner evaluates rules but does not integrate with `settings.json` — deferred to M11."
- "`bnac update` flags but does NOT delete removed files — needs `bnac prune` follow-up."
- "User-tier memory (`~/.claude/memory/`) deferred — project-tier only in this phase."
- "Phase CMM itself does not get a summary file (meta-issue) — manual completion entry in plan-2.md."

If genuinely nothing carries forward, write `- None.` rather than omitting the section.

## Over-budget protocol

If the first pass produces >1500 tokens, the compactor retries with this directive:

```
Retry: previous summary was {N} tokens (target 1500). Compress:
1. Architecture decisions — keep exactly 5 most load-bearing
2. Public surface — bundle to ≤8 entries
3. Carried-forward debt — keep ≤3 lines
4. Milestones rolled-up table — keep "Title" column to ≤6 words per row
DO NOT drop Architecture decisions entirely, do NOT shorten Goal + outcome.
```

If the second pass still exceeds budget, **truncate**: cut from the bottom (Carried-forward debt → Public surface → bundle Milestones harder) until under, and append a marker:

```markdown
> ⚠️ Truncated to fit budget — see [index.md](index.md) + per-milestone `m<N>-<slug>.summary.md` siblings for full detail.
```

## Anti-patterns

| Anti-pattern | Why bad | Do instead |
|---|---|---|
| Reading milestone `.summary.md` files to compose the phase summary | CMM-D4 violation; double-lossy compression | Read milestone *detail* (`m<N>-<slug>.md`) files |
| Quoting code bodies | Bloats budget, drifts on refactor | Signature only |
| Listing every task across every milestone | Tasks belong in milestone detail | Skip; mention only cross-milestone decisions |
| Mentioning who shipped what | Git has that | Omit personnel |
| Re-stating the phase exit criterion | Implicit — passed = done | Skip |
| Including milestone-local decisions | Belongs in milestone summary | Cut; cross-milestone only |
| Decisions without **Why:** | Becomes a fact, loses judgment value | Add the reason, even if short |
| Generic decisions ("we followed best practices") | Not actionable | Cut |
| Omitting Milestones rolled-up table | Required even for single-milestone phases | Include with one row |
| Listing milestone summaries as "sources" in any visible footer | CMM-D4: source is detail, not summary | Don't even reference summaries in the phase summary |

## Validation checklist

The compactor self-validates before writing:

- [ ] Token count ≤1500 (word-count proxy)
- [ ] All required sections present (Goal + outcome, Milestones rolled up, Architecture decisions, Carried-forward debt)
- [ ] Header has Folder, Completed (ISO date), Detail link
- [ ] Detail link points to existing sibling `index.md`
- [ ] Every milestone in the table has status `Approved` with completion date
- [ ] Architecture decisions are cross-milestone (verify by spot-checking each against milestone scope)
- [ ] Each Architecture decision has **Why:** marker
- [ ] No code blocks (other than inline backtick paths/signatures)
- [ ] Public surface ≤12 entries (or omitted entirely)
- [ ] Carried-forward debt ≤5 lines
- [ ] No `.summary.md` paths referenced as sources anywhere in the output

If any check fails, retry once (smaller); if still fails, truncate + flag per the over-budget protocol.

## Relationship to milestone summaries

A phase summary **replaces** child milestone summaries in `carry-forward.md` stitching — it does NOT supplement them. Once `index.summary.md` exists and the phase is `Approved`, the stitcher skips every `m<N>-<slug>.summary.md` in that phase folder.

Implications:

- A phase summary that's missing key decisions can't be "patched" by adding them to a child milestone summary — the child summary won't be loaded
- If a phase summary is wrong or outdated, regenerate it via `/bnac-context refresh P<N>` (M-CMM-4) — don't try to fix it indirectly via the milestone summaries
- The full per-milestone summaries stay on disk forever — they're loadable on demand (CMM-D10 opt-up) but skipped from default carry-forward once the phase rolls up

## Edge cases

| Case | Behavior |
|---|---|
| Phase has only 1 milestone | Still write a phase summary at phase complete; rolled-up table has 1 row. Architecture decisions may be thinner — that's fine. |
| Phase has 1 milestone that itself never produced an exported API | Omit Public surface; still required to keep the other 4 mandatory sections. |
| Milestone in the phase is `Approved` but `m<N>-<slug>.md` detail file is missing | Abort phase compaction; log error and refuse to write a partial summary. Restore the detail file before re-running. |
| Phase folder uses letter-prefix slug (e.g., `phase-cmm-context-memory`) | Heading uses the letter prefix verbatim (`# Phase CMM Summary: Context & Memory Management`). |
| The phase being summarized is itself the meta-phase that built compaction (e.g., Phase CMM) | Write the summary the same way; the meta-issue is noted in plan-N.md's completion entry, not in the summary. |
