---
id: ds-compliance-hook
name: BNDS Design System Compliance
event: post-write
enabled: true
blocking: true
targets: [claude, codex]
match:
  paths:
    - "**/*.tsx"
    - "**/*.jsx"
  stacks:
    - react-ts
rules:
  - id: no-raw-html
    message: "Raw HTML elements are forbidden — use BNDS components (see stacks/react-ts/skills/use-design-system/SKILL.md)."
    pattern: "<(button|input|select|textarea|a|img|table|h[1-6]|p|div[^>]*role=)"
    severity: error
  - id: no-inline-style-spacing
    message: "Inline style for spacing/colors is forbidden — use design tokens or bd-* utility classes."
    pattern: "style=\\{\\{[^}]*(margin|padding|color|background):"
    severity: error
  - id: no-hardcoded-px
    message: "Hardcoded pixel values are forbidden — use tokens (var(--bnds-g-*))."
    pattern: "(?<!var\\()[0-9]+px(?!\\s*\\*/)"
    severity: warning
---

# DS Compliance Hook

Enforces BusinessNext Design System rules on every `.tsx` / `.jsx` write. Fires after the model writes a file; if any `error`-severity rule triggers, the write is rolled back and the model is told what to fix.

## Contract

- **Event:** `post-write` — runs after a file is written by any tool (`Write`, `Edit`, `MultiEdit`).
- **Match:** only React files (`*.tsx`, `*.jsx`) in projects where stack detection reports `react-ts`.
- **Blocking:** yes — an error-severity hit prevents the write from standing. Warnings surface but do not block.

## Rules

| ID | Severity | What It Catches |
|----|----------|-----------------|
| `no-raw-html` | error | `<button>`, `<input>`, `<a>`, `<img>`, `<table>`, `<h1>`–`<h6>`, `<p>`, raw `<div role=...>` — all must be BNDS equivalents |
| `no-inline-style-spacing` | error | `style={{ margin: ... }}`, `padding`, `color`, `background` via inline style |
| `no-hardcoded-px` | warning | Hardcoded `Npx` not wrapped in `var(--bnds-g-*)` |

## Output Format

```
[ds-compliance] src/components/UserCard/UserCard.tsx:42
  error  no-raw-html     Raw <button> — use BNDS Button component
  warn   no-hardcoded-px 16px — use var(--bnds-g-spacing-md)
```

## Escape Hatches

Rare cases (e.g., third-party lib shims) may require a bypass:

```tsx
// bnac-ignore ds-compliance: reason=<why>
<button>Legacy shim</button>
```

Bypasses must include a reason. Reviewers check these in code review — a bypass without justification fails `/bnac-code-review`.

## Related

- React rule: `stacks/react-ts/rules/ds-compliance.md`
- Skill: `stacks/react-ts/skills/use-design-system/SKILL.md`
