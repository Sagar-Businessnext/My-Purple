---
id: separation-pattern-hook
name: React 8-File Separation Pattern
event: post-write
enabled: true
blocking: true
targets: [claude, codex]
match:
  paths:
    - "**/*.tsx"
    - "**/*.ts"
    - "**/*.scss"
  stacks:
    - react-ts
rules:
  - id: util-no-react
    message: "util.ts files must not import React or any .tsx/.hooks.ts file."
    appliesTo: "**/*.util.ts"
    forbidImports:
      - "react"
      - "react-dom"
      - "*.tsx"
      - "*.hooks.ts"
    severity: error
  - id: hooks-no-bnds
    message: "hooks.ts files must not import BNDS component files — hooks are UI-free."
    appliesTo: "**/*.hooks.ts"
    forbidImports:
      - "@bnds/*/components/*"
      - "*.tsx"
    severity: error
  - id: tsx-no-util-direct
    message: "Component (.tsx) files must not import from .util.ts directly — use the hook."
    appliesTo: "**/*.tsx"
    forbidImports:
      - "./*.util"
      - "./*.util.ts"
    severity: error
  - id: types-no-runtime
    message: "types.ts files must import types only — no runtime modules (React, BNDS, utils)."
    appliesTo: "**/*.types.ts"
    forbidImports:
      - "react"
      - "@bnds/*"
      - "./*.util"
      - "./*.hooks"
    severity: error
  - id: scss-tokens-only
    message: "SCSS must use design tokens — no hardcoded hex, px, or rem values."
    appliesTo: "**/*.scss"
    pattern: "(?:#[0-9a-fA-F]{3,8}|[0-9]+(?:\\.[0-9]+)?(?:px|rem))(?!\\s*;\\s*/\\*\\s*token)"
    severity: error
---

# Separation Pattern Hook

Enforces the React 8-file separation pattern on every write. The pattern isolates types, pure utils, hooks, and UI — violating the import boundaries is the #1 way components rot into unmaintainable tangles.

## The 8-File Pattern

For a component `Foo`:

```
Foo/
├── Foo.types.ts     — types only, no runtime imports
├── Foo.util.ts      — pure functions, no React, no BNDS
├── Foo.hooks.ts     — React state, no BNDS components
├── Foo.tsx          — UI only, BNDS components, imports hook
├── Foo.scss         — styles, design tokens only
├── Foo.test.ts      — tests (util + hook + UI in separate describes)
├── Foo.stories.tsx  — Storybook story
└── index.ts         — barrel export
```

## Import Matrix

| File | May Import | Must Not Import |
|------|-----------|-----------------|
| `.types.ts` | Other `.types.ts` | React, BNDS, utils, hooks |
| `.util.ts` | Own types, pure libs | React, BNDS, hooks, tsx |
| `.hooks.ts` | React, own types, own utils | BNDS components, tsx |
| `.tsx` | React, BNDS, own types, own hook | Own util (must go through hook) |
| `.scss` | Design tokens | Hardcoded hex/px/rem |

## Contract

- **Event:** `post-write` — fires after any file write in matching paths.
- **Blocking:** yes — error-severity violations roll back the write.
- **Scope:** only activates when `react-ts` stack is detected.

## Output Format

```
[separation-pattern] src/components/UserCard/UserCard.util.ts:1
  error  util-no-react  Import "react" forbidden in .util.ts — move to .hooks.ts

[separation-pattern] src/components/UserCard/UserCard.scss:14
  error  scss-tokens-only  Hardcoded "16px" — use var(--bnds-g-spacing-md)
```

## Escape Hatches

```ts
// bnac-ignore separation-pattern:util-no-react reason=<why>
import { something } from 'react';
```

Bypasses must name the specific rule ID and include a reason. `/bnac-code-review` audits these.

## Related

- React rules: `stacks/react-ts/rules/separation-pattern.md`, `component-files.md`, `types-files.md`, `scss-files.md`
- Skill: `stacks/react-ts/skills/react-component-pattern/SKILL.md`
