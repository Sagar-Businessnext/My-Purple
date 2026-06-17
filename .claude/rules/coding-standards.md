---
paths:
  - "src/**/*"
---

# Coding Standards Rule

Universal coding standards that apply across all BusinessNext stacks. Stack-specific rules are additive (see stack rule files when installed).

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files (TS/React) | PascalCase for components, camelCase for utils | `UserProfile.tsx`, `formatDate.ts` |
| Files (.NET) | PascalCase | `UserService.cs` |
| Files (Python) | snake_case | `user_service.py` |
| Variables | camelCase (TS), snake_case (Python), camelCase (.NET) | `userName`, `user_name`, `userName` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `API_BASE_URL` |
| Functions | camelCase (TS), snake_case (Python), PascalCase (.NET) | `getUser()`, `get_user()`, `GetUser()` |
| Types/Interfaces | PascalCase with descriptive names | `UserProfile`, `IUserRepository` |
| CSS classes | kebab-case | `user-profile`, `nav-header` |

## Code Quality Rules

1. **No `any` types** — Use proper TypeScript types. If the type is truly unknown, use `unknown` with type guards.
2. **No unused variables** — Remove or prefix with `_` if intentionally unused.
3. **No commented-out code** — Delete it. Git has history.
4. **No magic numbers** — Use named constants.
5. **No deeply nested code** — Max 3 levels of nesting. Extract to functions.
6. **No side effects in pure functions** — Functions labeled as pure must have no side effects.

## Security Standards

1. **Parameterized queries** — Never concatenate user input into SQL strings
2. **Input validation** — Validate all external input at system boundaries
3. **No secrets in code** — Use environment variables or secret management
4. **Sanitize output** — Prevent XSS by sanitizing rendered content
5. **Least privilege** — Request minimum required permissions

## Error Handling

1. **Catch specific errors** — Don't catch generic `Error` unless re-throwing
2. **Don't swallow errors** — Always log or handle meaningfully
3. **Fail fast** — Validate inputs early, return/throw before doing work
4. **User-facing errors** — Provide actionable messages, not stack traces

## File Organization

1. **One concept per file** — Don't mix unrelated logic
2. **Imports at top** — Organized: external libs → internal modules → relative imports
3. **Exports explicit** — Use named exports, barrel files for public API
4. **Keep files focused** — If a file exceeds ~300 lines, consider splitting
