# Memory Frontmatter Reference

The frontmatter schema for every memory file, plus the MEMORY.md index format. This is what `bnac-memory-curator` validates on every `add` and `prune-stale` run.

## Memory file frontmatter

```yaml
---
name: {kebab-case-slug}
description: {one-line — be specific enough to scan in MEMORY.md and decide relevance}
metadata:
  type: {user | feedback | project | reference}
---
```

### Field rules

| Field | Required | Format | Validation |
|---|---|---|---|
| `name` | yes | kebab-case slug, no `<type>_` prefix | Must equal the filename minus `<type>_` prefix and `.md` extension. E.g., filename `feedback_no-mock-db.md` → `name: no-mock-db` |
| `description` | yes | One line, ≤120 chars, no markdown | Verbatim copied into MEMORY.md index line; "User info" is too vague |
| `metadata.type` | yes | One of: `user`, `feedback`, `project`, `reference` | Closed set; custom types rejected by curator |

### Slug naming rules

- Kebab-case only (`no-mock-db`, not `NoMockDb` or `no_mock_db`)
- 2–5 words; if you need more, the memory is probably bundling multiple facts
- Slugs MUST be unique across the type — `feedback_no-mock-db` and `project_no-mock-db` would be a name collision; curator rejects
- Stable — don't rename slugs; if a memory's content drifts, write a new one and forget the old

### Filename convention

`<type>_<slug>.md`

| Filename | Frontmatter `name` |
|---|---|
| `user_role.md` | `name: role` |
| `feedback_no-mock-db.md` | `name: no-mock-db` |
| `project_compliance-deadline.md` | `name: compliance-deadline` |
| `reference_pipeline-bugs.md` | `name: pipeline-bugs` |

The curator enforces filename ↔ `name` equality. Mismatches are auto-fixed (the file is renamed; never the frontmatter).

## Body conventions

- **Plain Markdown** — no HTML, no JSX. Bullets, tables, links, code blocks are fine.
- **`feedback` and `project` types MUST include**:
  ```
  **Why:** <reason>
  **How to apply:** <scope>
  ```
  These two lines must appear exactly as bolded labels. Curator validates their presence.
- **Cross-links:** `[[other-slug]]` syntax (e.g., `see also [[feedback_no-mock-db]]`). These are resolved at read time; broken links don't error — they just don't render.
- **Absolute dates:** any relative date (`Thursday`, `next week`, `Q3`) is converted to ISO format (`2026-03-05`, `2026-Q3`) at save time. Curator flags unconverted dates on `prune-stale`.
- **Length:** target ≤300 words per memory body. Longer = probably bundling.

## MEMORY.md index format

The index is a flat list with no frontmatter. It has one section header per type, entries sorted alphabetically within a section.

```markdown
# Memory Index

> Auto-maintained by `bnac-memory-curator`. One line per memory.

## User

- [Role](user_role.md) — senior backend dev, deep Go, new to React
- [Response style](user_response-style.md) — prefers terse, no trailing summaries

## Feedback

- [No mock DB](feedback_no-mock-db.md) — integration tests must hit real DB (prior incident)
- [Single bundled PR for refactors](feedback_single-bundled-pr-for-refactors.md) — bundle coupled refactors, don't split

## Project

- [Compliance deadline](project_compliance-deadline.md) — auth rewrite due 2026-06-15 (legal driver)
- [Merge freeze mobile](project_merge-freeze-mobile.md) — freeze begins 2026-03-05 for release cut

## Reference

- [API latency dashboard](reference_api-latency-dashboard.md) — grafana.internal/d/api-latency oncall view
- [Pipeline bugs in Linear](reference_pipeline-bugs.md) — INGEST project tracks pipeline bugs
```

### Index line format

`- [<Title>](<filename>) — <description>`

- `<Title>` is a short human title (3–5 words) — NOT the slug
- `<filename>` is the relative filename (e.g., `feedback_no-mock-db.md`) — relative to `memory/`
- `<description>` is the file's `description:` field, copied verbatim
- The em-dash is `—` (U+2014), not `--` or `-`

### Limits

- ≤200 lines total (anything past 200 is not loaded — split a project's memory or prune)
- ≤150 chars per line
- One blank line between sections; no blank lines within a section

## Validation checklist (curator runs this)

On every `add`:
- [ ] Frontmatter has `name`, `description`, `metadata.type`
- [ ] `metadata.type` is in the closed set
- [ ] `name` slug equals filename slug (modulo type prefix and `.md`)
- [ ] `description` is ≤120 chars, no newlines
- [ ] If type is `feedback` or `project`, body contains `**Why:**` and `**How to apply:**` lines
- [ ] No duplicate slug in same type
- [ ] Slug is unique across all types
- [ ] MEMORY.md updated with the new line in the right section

On `prune-stale`:
- [ ] Every file referenced in MEMORY.md exists
- [ ] Every file in `memory/` (minus MEMORY.md) is referenced in MEMORY.md
- [ ] No two files have the same `name`
- [ ] All dates in bodies are absolute (ISO or YYYY-Qn) — flag relative dates
- [ ] Memory body matches its type's body-shape requirements
- [ ] Cross-links `[[slug]]` either resolve to an existing memory OR are explicitly marked as placeholders
