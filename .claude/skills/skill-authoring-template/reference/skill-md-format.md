# SKILL.md Format Reference

Every BNAC skill has a `SKILL.md` at the root of its folder. SKILL.md is a thin index — short, scannable, with links into `reference/` for detail.

## Frontmatter

```yaml
---
name: <slug>
description: <one-line — what the skill does, who consumes it>
user-invocable: true | false
argument-hint: "<expected argument shape, or empty>"
---
```

| Field | Required | Notes |
|---|---|---|
| `name` | yes | Kebab-case slug, must equal folder name |
| `description` | yes | One line, ≤120 chars, action-oriented |
| `user-invocable` | yes | `true` if a `/slash-command` runs this skill directly. Most BNAC skills are agent-consumed (`false`). |
| `argument-hint` | yes | What follows the slash command — e.g. `"<file-path>"`, `""`, `"<ComponentName>"` |

## Body sections (in order)

### 1. Purpose paragraph
One sentence stating the skill's job. Same shape as the description, but expanded.

```markdown
Author new BNAC skill folders with consistent shape: a thin SKILL.md index over authoritative reference files in `<slug>/reference/`.
```

### 2. Additional Resources
Bullet list of every file in `reference/` with one-line description.

```markdown
## Additional Resources

- [reference/<topic-1>.md](reference/<topic-1>.md) — <one-line description>
- [reference/<topic-2>.md](reference/<topic-2>.md) — <one-line description>
```

### 3. Steps (procedural skills) OR Format (template skills) OR Tables (lookup skills)

**Procedural skill** (build-fix, verification-loop):
```markdown
## Steps

1. <imperative action>
2. <imperative action>
3. <branching: if X, do Y>
4. <imperative action>
5. <verification step>
```

**Template skill** (git-workflow, changelog-conventions):
```markdown
## Format

\`\`\`<language>
<canonical example>
\`\`\`

### Examples
\`\`\`
<example 1>
<example 2>
\`\`\`
```

**Lookup skill** (use-design-tokens, use-design-system): often delegates entirely to reference files
```markdown
## Lookup

See [reference/<topic>.md](reference/<topic>.md) for the authoritative table.
```

### 4. Rules
Bulleted list of constraints. Always present — even lookup skills have rules ("don't memorize, always look up").

```markdown
## Rules

- <rule 1, in plain prose>
- <rule 2>
- <rule 3>
```

## Length

- SKILL.md should be **under 80 lines**. If it grows beyond, push detail into reference files.
- Reference files have no length limit but each should focus on one topic.

## Skill type → shape decision

| Type | Body sections | Example |
|---|---|---|
| Procedural | Purpose → Resources → Steps → Rules | `build-fix`, `verification-loop` |
| Template | Purpose → Resources → Format → Examples → Rules | `git-workflow`, `changelog-conventions` |
| Lookup | Purpose → Resources → Lookup → Rules | `use-design-tokens`, `use-design-system` |
| Procedural+Template | Purpose → Resources → Steps → Format → Rules | `code-review` |
