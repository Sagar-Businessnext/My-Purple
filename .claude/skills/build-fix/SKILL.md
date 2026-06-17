---
name: build-fix
description: Diagnose and fix build errors, type errors, and lint failures. Iterates until the build is clean.
user-invocable: true
argument-hint: ""
---

Diagnose and fix all build, type, and lint errors in the current project.

## Additional Resources

- [reference/common-errors.md](reference/common-errors.md) — common error patterns and fixes

## Steps

1. Read `project/.claude/CLAUDE.md` to understand the build system
2. Run the build command and capture output
3. Parse errors — categorize as type, import, syntax, lint
4. For each error (in dependency order):
   a. Read the failing file and context
   b. Identify root cause
   c. Apply minimal fix
   d. Check if fix affects other files
5. Re-run build
6. If new errors appeared, repeat from step 3
7. When build is clean, run type check (`tsc --noEmit` or equivalent)
8. When type check passes, run lint if configured
9. Report summary of all fixes applied

## Error Priority

Fix errors in this order (earlier fixes often resolve later ones):

1. **Missing dependencies** — `npm install`, `dotnet restore`
2. **Import/module errors** — Wrong paths, missing exports
3. **Type errors** — Missing types, wrong types
4. **Syntax errors** — Malformed code
5. **Lint errors** — Style violations

## Rules

- Fix root causes, not symptoms
- Don't use `@ts-ignore`, `eslint-disable`, `# type: ignore` to suppress errors
- Don't widen types to `any` to make errors go away
- If an error requires an architecture change, report it — don't patch around it
- If a dependency is missing, install it (but flag new dependencies for review)
