---
name: memory-conventions
description: Typed long-term memory conventions for BNAC projects — 4 memory types (user, feedback, project, reference), file naming, frontmatter contract, body structure, and MEMORY.md indexing rules. Used by bnac-memory-curator and read by every agent that needs to recall durable facts.
user-invocable: false
argument-hint: ""
---

Define the canonical shape of a BNAC project's typed long-term memory store at `project/.claude/memory/`. This skill is the contract that `bnac-memory-curator` enforces and that the `memory-management` rule references.

## Additional resources

- [reference/memory-types.md](reference/memory-types.md) — full description of each of the 4 types, when to use, what NOT to confuse them with, concrete examples
- [reference/memory-frontmatter.md](reference/memory-frontmatter.md) — frontmatter schema, slug naming, MEMORY.md index format

## On-disk shape (NON-NEGOTIABLE)

```
project/.claude/memory/
├── MEMORY.md                          ← index — pointer per memory, one line each
├── user_<slug>.md                     ← user role / preferences / expertise
├── feedback_<slug>.md                 ← corrections + confirmations
├── project_<slug>.md                  ← deadlines, decisions, motivation
└── reference_<slug>.md                ← external system pointers
```

- Filename pattern: `<type>_<kebab-case-slug>.md`
- Slug matches the `name:` frontmatter field exactly
- One memory per file — never bundle
- MEMORY.md has NO frontmatter; it's a pointer index

## The 4 types

| Type | Lifetime | Example trigger | Example body |
|---|---|---|---|
| `user` | Long — survives project changes | "I'm a senior backend dev, new to React" | `Senior backend engineer, ten years in Go. New to React. Frame frontend explanations in terms of backend analogues.` |
| `feedback` | Medium — until the rule is invalidated | User corrects approach OR confirms validated judgment | `Integration tests must hit real DB, not mocks.<br>**Why:** prior incident where mock/prod divergence masked a broken migration<br>**How to apply:** any test under `tests/integration/`, never use jest.mock for db modules` |
| `project` | Short — facts decay fast | "Auth rewrite is for compliance, not tech debt" | `Auth middleware rewrite driven by legal/compliance requirements around session token storage.<br>**Why:** legal flagged it; deadline 2026-06-15<br>**How to apply:** scope decisions favor compliance over ergonomics` |
| `reference` | Long — until the external system changes | "Pipeline bugs go in Linear INGEST" | `Pipeline bugs tracked in Linear project INGEST. Read tickets there for context on pipeline regressions.` |

## Body structure

- **`user` and `reference`** — free-form prose, lead with the fact
- **`feedback` and `project`** — fact/rule, then `**Why:** <reason>` and `**How to apply:** <scope>` lines. The *why* is what lets a future session judge edge cases rather than blindly apply the rule.

Cross-link related memories with `[[slug]]` (e.g., `see also [[feedback_no-mock-db]]`). A `[[slug]]` that doesn't yet match a file is fine — it's a placeholder for a memory worth writing.

## Frontmatter contract

```yaml
---
name: {kebab-case-slug}                    # MUST equal filename's slug
description: {one-line — be specific}      # used to decide relevance on future reads
metadata:
  type: {user | feedback | project | reference}
---
```

`description:` should be **specific enough** that scanning MEMORY.md (which uses these descriptions as the one-line hook) is enough to decide whether to open the file. "User info" is bad. "Senior Go dev, new to React" is good.

## MEMORY.md index

```markdown
# Memory Index

> Auto-maintained by `bnac-memory-curator`. One line per memory.

- [User role](user_role.md) — senior backend dev, deep Go, new to React
- [No mock DB](feedback_no-mock-db.md) — integration tests must hit real DB (prior incident)
- [Compliance deadline](project_compliance-deadline.md) — auth rewrite due 2026-06-15
- [Pipeline bugs in Linear](reference_pipeline-bugs.md) — INGEST project tracks pipeline bugs
```

Rules:
- One entry per file, ordered by `metadata.type` then alphabetical
- Line is `- [<Title>](<filename>) — <description>` (using the file's `description:` field verbatim)
- ≤200 lines total — past 200 is truncated from the load window
- Curator regenerates this from the actual files on `prune-stale`

## When to save vs. when to skip

| Save | Skip |
|---|---|
| User states a role / preference | "Just FYI"-style asides without a clear preference |
| User corrects approach | First-time disagreement that's just discussion |
| User confirms a non-obvious choice ("yes exactly") | Affirming an obvious choice |
| Deadline, stakeholder, motivation behind work | Code structure (in code already) |
| External system pointer + purpose | Random URL drop without context |

See [reference/memory-types.md](reference/memory-types.md) for concrete examples per type.

## Rules

- **One file per memory** — never combine multiple facts into one file
- **Both file AND index** — adding a memory updates MEMORY.md too; orphaned files are a bug
- **Frontmatter `name:` = filename slug** — strict equality
- **Type is closed set** — only `user`, `feedback`, `project`, `reference`. Custom types get rejected by the curator.
- **`feedback` and `project` MUST have Why + How** — these two lines distinguish a memory from a sticky note
- **Absolute dates** — "Thursday" gets converted to "2026-03-05" at save time
- **No duplicates** — search MEMORY.md before writing; update existing entries rather than creating new
- **Stale = update or remove** — recalled memory that conflicts with current state must be reconciled, not acted on
