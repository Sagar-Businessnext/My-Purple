# Milestone Summary Format Reference

Section-by-section spec for the `.summary.md` sibling file. This is what `bnac-context-compactor` produces in milestone mode.

## Required fields

| Field / Section | Required | Notes |
|---|---|---|
| `# M<N> Summary: <Title>` | yes | Heading — globally-numbered ID + same title as detail file |
| `Phase` | yes | `phase-<N>-<slug>` (must match parent folder) |
| `Completed` | yes | `YYYY-MM-DD` — the date the milestone was marked Done in `milestone-status.md` |
| `Detail` | yes | Markdown link to the sibling `m<N>-<slug>.md` |
| `## Goal` | yes | One line in outcome terms ("Users can log in") not work terms ("Implemented login endpoint") |
| `## Key decisions` | yes | 3–5 bullets, each with **Why:** |
| `## Artifacts` | yes | File paths only, ≤10 entries, ≤1 line each |
| `## Public surface` | conditional | Required if milestone produced an exported API; omit for internal-only work |
| `## Gotchas / debt` | yes | ≤3 lines total; if truly none, write `- None.` |

## Section-by-section guidance

### Header (frontmatter-free)

There's no YAML frontmatter on summary files (unlike memory files). The header is:

```markdown
# M<N> Summary: <Title>

**Phase:** phase-<N>-<slug>
**Completed:** YYYY-MM-DD
**Detail:** [m<N>-<slug>.md](m<N>-<slug>.md)
```

Why no frontmatter: summaries are stitched into `carry-forward.md` as Markdown blocks; frontmatter would pollute the output. The fields above appear as bold-label lines instead.

### `## Goal`

One line, **outcome-shaped**.

| Good | Bad |
|---|---|
| "Users can authenticate via email + password" | "Implemented login endpoint" |
| "Build artifacts deploy to staging on green CI" | "Wrote deploy.yml" |
| "Payment service answers /health with 200" | "Set up payment scaffold" |

If the original milestone's Goal field was work-shaped, **rewrite it** to outcome-shaped for the summary. Detail stays untouched; summary is its better-distilled form.

### `## Key decisions`

This is the most important section — it's what prevents future sessions from re-litigating the same calls. 3–5 bullets, each:

```markdown
- **<decision label>** — <one-line summary of the choice>. **Why:** <the reason — constraint, incident, deliberate tradeoff>.
```

The **Why:** lets later milestones judge edge cases. A bullet without **Why:** is a fact, not a decision.

Pull decisions from:
- The milestone's "Risks" section in the detail
- Log entries during the milestone period (look for "decision", "chose", "rejected")
- Git commit messages (often contain rationale)

If you can't extract 3 decisions, the milestone was either too small (merge with neighbor) or its detail file is sparse (request enrichment).

### `## Artifacts`

File paths only — no contents, no excerpts, no metrics. Each entry ≤1 line, ≤10 entries total.

Use **bundling** when a milestone produced many similar files:

| Verbose (bad) | Bundled (good) |
|---|---|
| `src/db/migrations/2026-05-15-001-users.sql` | `src/db/migrations/2026-05-15-*.sql` — 12 user schema migrations |
| `src/db/migrations/2026-05-15-002-roles.sql` | |
| ... 10 more lines ... | |

Each artifact line:
```markdown
- `path/to/file.ext` — <one-line purpose>
```

If you exceed 10 lines, bundle harder. >10 artifact lines = milestone was too broad.

### `## Public surface`

What other milestones can depend on — exported symbols, API endpoints, public file paths.

```markdown
- `functionName(args): ReturnType` — one-line purpose
- `interface FooContract { field: type; ... }` — one-line purpose
- `POST /api/v1/foo` — one-line purpose
```

**Signatures only.** Never include function bodies, interface implementations, or endpoint payloads. The detail file has those.

If the milestone produced no public surface (internal refactor, test additions), **omit this section entirely**. Don't write "None" — just leave it out.

### `## Gotchas / debt`

≤3 lines total. The "things someone reading this in 6 months needs to know that aren't in code". Examples:

- "Retry policy is global — no per-call override yet. Defer to a `RetryPolicy` plug-in when needed."
- "`AbortSignal` is wired but not surfaced in convenience methods; manual via `RequestOptions`."
- "Touches `legacy-auth.ts` for compat — DO NOT extend that file; new auth code goes under `auth-v2/`."

If genuinely none, write `- None.` rather than omitting the section.

## Over-budget protocol

If the first pass produces >500 tokens, the compactor retries with this directive:

```
Retry: previous summary was {N} tokens (target 500). Drop or compress:
1. Public surface — keep ≤5 entries
2. Gotchas — keep ≤2 lines
3. Decisions — keep exactly 3 most-load-bearing
4. Compress Artifacts via bundling
DO NOT drop Key decisions entirely or shorten Goal.
```

If the second pass still exceeds budget, **truncate**: cut from the bottom (Gotchas → Public surface → Artifacts) until under, and add a marker:

```markdown
> ⚠️ Truncated to fit budget — see [m<N>-<slug>.md](m<N>-<slug>.md) for full detail.
```

## Anti-patterns

| Anti-pattern | Why bad | Do instead |
|---|---|---|
| Quoting code bodies | Bloats budget, drifts on refactor | Signature only |
| Listing every task | That's in the detail file | Skip; mention only milestone-level decisions |
| Mentioning who did the work | Git has that | Omit personnel |
| Re-stating the acceptance test | Implicit — passed = done | Skip |
| Including a "Status" line | Always "Completed" — implicit | Use the `Completed: YYYY-MM-DD` header |
| Generic decisions ("we wrote good code") | Not actionable | Cut |
| Decisions without **Why:** | Becomes a fact, loses judgment value | Add the reason, even if short |
| Multiple Goal lines | Outcome should fit one line | If it doesn't, milestone was too broad |

## Validation checklist

The compactor self-validates before writing:

- [ ] Token count ≤500 (word-count proxy)
- [ ] All required sections present (Goal, Key decisions, Artifacts, Gotchas)
- [ ] Header has Phase, Completed (ISO date), Detail link
- [ ] Detail link points to existing sibling file
- [ ] Each Key decision has **Why:** marker
- [ ] No code blocks (other than inline backtick paths/signatures)
- [ ] Artifacts ≤10 entries
- [ ] Public surface ≤8 entries (or omitted)
- [ ] Gotchas ≤3 lines

If any check fails, retry once (smaller); if still fails, truncate + flag.
