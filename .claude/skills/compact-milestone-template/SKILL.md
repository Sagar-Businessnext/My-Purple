---
name: compact-milestone-template
description: Canonical structure for milestone compact summaries — the ≤500-token `.summary.md` sibling written when a milestone completes. Used by bnac-context-compactor (milestone mode). Hard token budget; strict 7-section template; sourced from the milestone's detail .md, log.md slice for the period, and (optionally) git diff.
user-invocable: false
argument-hint: ""
---

Define the canonical shape of a milestone compact summary: a token-budgeted (`≤ 500 tokens`) sibling file named `<milestone-file>.summary.md` that captures the *why* and *what* of a completed milestone without re-listing its detail.

## Additional resources

- [reference/milestone-summary-format.md](reference/milestone-summary-format.md) — full section-by-section format, examples, and the over-budget retry protocol

## On-disk shape (NON-NEGOTIABLE)

Summary files are **siblings** of milestone detail files (per CMM-D1):

```
project/.claude/phases/phase-1-foundation/
├── index.md
├── m1-cli-scaffold.md              ← detail (stays untouched)
├── m1-cli-scaffold.summary.md      ← compact summary (this skill defines its shape)
├── m2-install-engine.md
└── m2-install-engine.summary.md
```

Glob pattern for all summaries: `**/*.summary.md`.

## Token budget (HARD)

- **Target:** ≤500 tokens (~2000 characters)
- **Hard reject:** if `bnac-context-compactor` produces a summary >500 tokens, it retries once with "drop optional sections, keep decisions"; final fallback truncates and adds a `> ⚠️ Truncated — see detail file` marker

Token counting: use a simple word-count proxy (1 token ≈ 0.75 words). Counting must be **conservative** — when in doubt, assume more tokens.

## Required sections (in order)

```markdown
# M<N> Summary: <Title>

**Phase:** <phase-folder>
**Completed:** YYYY-MM-DD
**Detail:** [m<N>-<slug>.md](m<N>-<slug>.md)

## Goal
<one line — what this milestone produced, in outcome terms>

## Key decisions
- **<decision name>** — <one-line summary>. **Why:** <reason, ideally tied to a constraint or prior incident>.
- (3–5 bullets — these are the part that prevents future hallucination)

## Artifacts
- `path/to/file1.ext` — <one-line purpose>
- `path/to/file2.ext` — <one-line purpose>
(file paths only — no contents, no excerpts)

## Public surface
- `<exported symbol or API>` — `<signature only, no body>`
- (signatures only — what other milestones can depend on)

## Gotchas / debt
- <one to three lines max — what someone reading this in 6 months needs to know>
```

## Section caps (enforced)

| Section | Cap |
|---|---|
| Goal | 1 line |
| Key decisions | 3–5 bullets, each ≤2 lines |
| Artifacts | ≤10 paths, each ≤1 line |
| Public surface | ≤8 entries, each ≤1 line |
| Gotchas / debt | ≤3 lines total |

If a milestone genuinely produced more than these limits, **bundle similar items** (e.g., "12 schema migration files under `db/migrations/`" as one Artifact line). Do not exceed the caps — that's a signal the milestone was too broad.

## What to source from

The compactor builds the summary from three inputs (NOT from the milestone's own summary if any earlier version existed — always rebuild from primary sources):

1. **Milestone detail `.md`** — the `m<N>-<slug>.md` file: Goal, High-level tasks, Deliverables, Acceptance criteria
2. **`log.md` slice** — entries whose timestamp falls between milestone-start and milestone-complete events (read full entries, extract decisions + result lines)
3. **Git diff** (optional, when Bash is available) — files changed between milestone-start and milestone-complete commits; supplements the Artifacts section

Per CMM-D4: phase summaries also follow this principle (sourced from milestone details, NOT from milestone summaries).

## What NOT to include

- **No task-level breakdown** — atomic tasks belong in the detail file
- **No quoted code** — paths only, signatures only, never bodies
- **No log line excerpts** — distill into "decision" bullets
- **No mention of who did what** — git/log have that; the summary is project history, not personnel
- **No re-statement of the acceptance test** — passed = implicit; failed = milestone shouldn't be summarized yet

## Example

```markdown
# M3 Summary: HTTP Helper

**Phase:** phase-1-foundation
**Completed:** 2026-05-15
**Detail:** [m3-http-helper.md](m3-http-helper.md)

## Goal
A typed HTTP client wrapping the project's auth + retry contract.

## Key decisions
- **Single helper module, no per-feature clients** — every caller imports from `lib/http.ts`. **Why:** earlier projects sprawled into 8 ad-hoc clients with divergent retry logic.
- **5xx-only retry, max 3 attempts, exponential backoff** — fixed in the helper, no caller override. **Why:** a retry-everything bug in Q3 2025 amplified a 4xx storm into a DDoS on auth.
- **Body classes, not plain objects** — every request body must extend `RequestBody<T>`. **Why:** runtime type guard catches the silent-field-drop class of bugs.

## Artifacts
- `src/lib/http.ts` — main helper module
- `src/lib/http.types.ts` — Request/Response interfaces
- `src/lib/http.test.ts` — 24 unit tests

## Public surface
- `httpGet<T>(url, opts?): Promise<T>` — typed GET
- `httpPost<T,B extends RequestBody>(url, body, opts?): Promise<T>` — typed POST
- `interface RequestOptions { retry?: RetryPolicy; headers?: HeadersInit; signal?: AbortSignal }`

## Gotchas / debt
- Retry policy is global — no per-call override yet. Defer to a `RetryPolicy` plug-in when a use case emerges.
- `AbortSignal` is wired but not surfaced in the convenience methods; manual via `RequestOptions`.
```

That summary is ~270 tokens — well under budget, all 7 sections present.

## Rules

- **Stay under 500 tokens** — hard reject + retry above
- **Decisions need *why*** — a bullet without a reason is a fact; the *why* is what makes it judgment fuel
- **Paths and signatures only** — never quote code bodies
- **No tasks, no people, no log excerpts** — those have their own files
- **Built from detail + log + git** — never from a prior summary (avoids drift on rebuild)
- **One file per milestone** — `<milestone-file>.summary.md`, sibling location
- **Detail file stays untouched** — summary is additive; never modifies the detail
