# Skill: Git Workflow

> **Used by:** `bnac-developer` agent
> **Trigger:** Any git operation — commits, branching, PRs

## Purpose

Ensures all git operations follow BusinessNext conventional commit format and branching strategy. This skill is the single source of truth for how code is committed and branched.

## Commit Procedure

1. **Stage specific files** — never `git add .` or `git add -A`
2. **Choose the correct type:**

   | Type | When | Example |
   |------|------|---------|
   | `feat` | New feature or capability | `feat(auth): add login page` |
   | `fix` | Bug fix | `fix(api): handle null response` |
   | `refactor` | Code restructuring, no behavior change | `refactor(utils): extract date helpers` |
   | `test` | Adding or fixing tests | `test(auth): add login integration tests` |
   | `docs` | Documentation only | `docs(readme): update setup steps` |
   | `chore` | Maintenance, deps, tooling | `chore(deps): update react to 19` |
   | `style` | Formatting, whitespace, no logic change | `style(components): fix indentation` |
   | `perf` | Performance improvement | `perf(query): add index for user lookup` |
   | `ci` | CI/CD changes | `ci(github): add deploy workflow` |
   | `build` | Build system changes | `build(webpack): update output config` |

3. **Determine scope** — the component, module, or area affected
4. **Write the message** — imperative mood, lowercase, no period at end
5. **Commit:**
   ```bash
   git add <specific-files>
   git commit -m "<type>(<scope>): <description>"
   ```

## Branching Procedure

1. **Create branch from `develop`** (not `main`):
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/<ticket>-<description>
   ```

2. **Branch naming:**
   - `feature/<ticket>-<description>` — new features
   - `fix/<ticket>-<description>` — bug fixes
   - `hotfix/<ticket>-<description>` — production hotfixes
   - `release/v<version>` — release prep

3. **Keep branch up to date:**
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

## PR Procedure

1. Push branch with upstream tracking:
   ```bash
   git push -u origin <branch-name>
   ```
2. Create PR targeting `develop`
3. PR title = same format as commit: `<type>(<scope>): <description>`
4. PR body = summary of changes + test plan
5. All checks must pass before merge
6. Squash-merge to `develop`

## Forbidden Actions

- `git --no-verify` — fix the hook
- `git push --force` to `main` or `develop`
- `git add .` or `git add -A` — stage specific files
- Committing `.env`, secrets, credentials, tokens
- Empty commits or meaningless messages like "fix" or "update"

## Reference

See `reference/commit-examples.md` for more examples per stack.
