# Reference Files Reference

Reference files under `<skill>/reference/` are where the real content of a BNAC skill lives. SKILL.md is just an index over them.

## When to add a reference file

Add one when you have:
- **A checklist** — too long for SKILL.md (e.g., 30-item code review checklist)
- **A canonical format** — example output, template, or schema (e.g., commit message format)
- **A lookup table** — design tokens, component map, error patterns
- **A worked example** — showing how the skill applies to a non-trivial case

If the content is under ~10 lines and read sequentially, inline it in SKILL.md. Otherwise, factor out.

## Naming

| Pattern | Use when |
|---|---|
| `<topic>.md` | Standalone topic — `commit-examples.md`, `common-errors.md`, `mixins.md` |
| `<n>-<topic>.md` | Ordered series — `01-types.md`, `02-util.md` (rare; only when sequence matters) |
| `<category>-<topic>.md` | Sub-categorization — `wcag-forms.md`, `wcag-tables.md` |

Keep names lowercase, kebab-case, descriptive. Avoid generic names like `notes.md`, `details.md`, `more.md`.

## Format

Reference files have **no frontmatter**. Just a titled markdown document.

```markdown
# <Topic Title>

<One-paragraph orientation — what this file is for, when to consult it>

## <Section 1>

<content>

## <Section 2>

<content>
```

## Length

No hard limit. Reference files can be long — they're consulted, not read top-to-bottom.

| File type | Typical size |
|---|---|
| Checklist | 50–150 lines |
| Format / template | 30–80 lines |
| Lookup table | 100–500+ lines |
| Worked example | 80–200 lines |

If a reference file exceeds ~600 lines, consider splitting by sub-topic.

## Linking

- From SKILL.md to reference: `[reference/<file>.md](reference/<file>.md) — <what's in it>`
- Between reference files: `[<other-topic>](<other-topic>.md)` (relative within `reference/`)
- To other skills: `[<skill-name>](../../<skill-name>/SKILL.md)` (relative across skills)
- To agents: `[<agent>](../../../agents/<agent>.md)` (relative across agent folder)

## Anti-patterns

| Don't | Do |
|---|---|
| Frontmatter at top of reference file | No frontmatter; only the SKILL.md has it |
| Re-stating SKILL.md content | Reference files have **new** information; don't repeat |
| Wall-of-text without sections | Always use `##` headers for navigation |
| Code blocks without language tag | Always tag fenced blocks (`\`\`\`ts`, `\`\`\`scss`, etc.) |
| Hardcoded absolute paths | Use repo-relative or skill-relative paths |
| Mixing topics in one file | One topic per file; if you find yourself adding "Also..." sections, split |

## Examples by skill type

### Procedural skill (`build-fix`)
```
build-fix/
├── SKILL.md                         # Steps + Rules
└── reference/
    └── common-errors.md             # Error pattern → fix lookup
```

### Template skill (`git-workflow`)
```
git-workflow/
├── SKILL.md                         # Commit format + branch strategy
└── reference/
    └── commit-examples.md           # 20+ realistic commit messages
```

### Lookup skill (`use-design-tokens`)
```
use-design-tokens/
├── SKILL.md                         # When to use tokens vs utilities
└── reference/
    ├── colors.md                    # Full color token list
    └── typography-spacing.md        # Typography + spacing tokens
```

### Stack skill (`react-component-pattern`)
```
react-component-pattern/
├── SKILL.md                         # 8-file pattern overview
└── reference/
    ├── file-structure.md            # What goes in each .ts/.tsx/.scss
    ├── naming-conventions.md        # Slug → filenames
    └── separation-rules.md          # Import boundary rules
```
