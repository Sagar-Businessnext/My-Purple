---
name: skill-authoring-template
description: Standard structure for authoring BNAC skill folders — SKILL.md frontmatter, body sections, and reference file conventions.
user-invocable: false
argument-hint: ""
---

Author new BNAC skill folders with consistent shape: a thin SKILL.md index over authoritative reference files in `<slug>/reference/`.

## Additional Resources

- [reference/skill-md-format.md](reference/skill-md-format.md) — SKILL.md frontmatter and body sections
- [reference/reference-files.md](reference/reference-files.md) — when to add reference files, naming, content patterns

## Steps

1. **Identify skill type**:
   - **Procedural** — "how to do X" (e.g., `build-fix`, `verification-loop`)
   - **Template** — canonical format for outputs (e.g., `git-workflow`, `changelog-conventions`)
   - **Lookup** — reference table consulted at need (e.g., `use-design-tokens`, `use-design-system`)
2. **Pick the right shape** based on type — see `reference/skill-md-format.md`
3. **Set `user-invocable`**:
   - `true` if the skill maps to a slash command users invoke directly (e.g., `/build-fix`, `/code-review`)
   - `false` if it's a reference skill that agents pull in passively
4. **Write SKILL.md** — frontmatter + 1-paragraph purpose + Additional Resources + Steps + Rules
5. **Write reference files** under `<slug>/reference/` — one file per topic, named `<topic>.md`
6. **Verify** — links from SKILL.md to reference files resolve, no stale references

## Rules

- **SKILL.md is an index, not a document** — Real content lives in `reference/`. Keep SKILL.md under ~80 lines.
- **At least 1 reference file** — Every skill has at least one. If you can't think of any, the skill is too thin to exist.
- **Reference files have no frontmatter** — Just titled markdown
- **Slug = folder name = `name` field** — All three identical
- **Don't duplicate other skills** — Search existing skills before authoring; merge or extend instead
- **No code in SKILL.md unless illustrative** — Production code lives in agents and project source, not in skill docs
