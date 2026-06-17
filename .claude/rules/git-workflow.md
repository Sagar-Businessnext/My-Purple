---
paths:
  - "**/*"
---

# Git Workflow Rule

All BusinessNext projects follow conventional commits and a standard branching strategy.

## Commit Format (MANDATORY)

```
<type>(<scope>): <description>

Types: feat, fix, refactor, test, docs, chore, style, perf, ci, build
Scope: component name, module, or feature area
```

### Examples
```
feat(auth): add JWT token refresh endpoint
fix(dashboard): correct date range filter off-by-one
refactor(api): extract validation into middleware
test(user-service): add integration tests for signup flow
docs(readme): update setup instructions for Docker
chore(deps): bump typescript to 5.x
```

## Branch Strategy

| Branch | Purpose | Naming |
|--------|---------|--------|
| `main` | Production-ready code | — |
| `develop` | Integration branch | — |
| `feature/*` | New features | `feature/<ticket>-<description>` |
| `fix/*` | Bug fixes | `fix/<ticket>-<description>` |
| `release/*` | Release preparation | `release/v<version>` |
| `hotfix/*` | Production hotfixes | `hotfix/<ticket>-<description>` |

## Rules

1. **Never use `--no-verify`** — If a hook fails, fix the underlying issue
2. **Never force-push to `main` or `develop`** — These branches are protected
3. **Never commit secrets** — No API keys, passwords, connection strings, tokens
4. **Keep commits atomic** — One logical change per commit
5. **Write meaningful messages** — Describe why, not just what
6. **Rebase feature branches** — Keep linear history on feature branches
7. **Squash-merge to develop** — Clean integration history

## PR Workflow

1. Create feature branch from `develop`
2. Make commits following conventional format
3. Push and create PR
4. Code review (automated + human)
5. All checks must pass (build, type, lint, test)
6. Squash-merge to `develop`
