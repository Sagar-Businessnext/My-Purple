# Commit-to-Changelog Mapping

`bnac-changelog-agent` reads conventional commits from `git log` and aggregates them into changelog entries. This file is the mapping table.

## Conventional commit type → changelog section

| Commit type | Goes to section | Notes |
|---|---|---|
| `feat` | `### Added` | New feature or capability |
| `feat!` (breaking) | `### Added` + `### Removed` (or `### Changed`) | Breaking feat → also note removed/changed behavior |
| `fix` | `### Fixed` | Bug fix |
| `fix!` (breaking) | `### Fixed` + `### Changed` | Breaking fix changed contract |
| `refactor` | (skip) | Not user-visible |
| `perf` | `### Changed` | Performance improvement — note metric if available |
| `chore` | (skip) | Not user-visible |
| `docs` | (skip) | Not user-visible |
| `test` | (skip) | Not user-visible |
| `style` | (skip) | Not user-visible |
| `ci` | (skip) | Not user-visible |
| `build` | (skip) | Unless user installs from source — then `### Changed` |
| `revert` | (varies) | Counter-entry to whatever was reverted; usually `### Removed` or `### Changed` |

## Detecting breaking changes

A commit is breaking if any of:
- Subject ends with `!` — `feat(api)!: change response shape`
- Body contains `BREAKING CHANGE:` line
- Body contains `BREAKING-CHANGE:` line (legacy)

Breaking changes always show in the changelog regardless of type.

## Aggregation rules

**One entry per logical change, not one per commit.** Multiple commits implementing the same feature get one entry.

### Aggregation by scope

If a scope appears in 3+ commits, treat them as one entry:

```
feat(auth): add login endpoint
feat(auth): add JWT signing
feat(auth): add session refresh
test(auth): add integration tests
```
→ Single entry: `Added user authentication (login, JWT signing, session refresh). ([#142])`

### Aggregation by milestone

If commits are part of the same milestone (detected via PR description, branch name, or activity log), aggregate by milestone:

```
feat(react): add UserCard component (M7.1)
feat(react): add Dashboard page (M7.2)
test(react): add UserCard tests (M7.3)
```
→ Single entry: `Added user dashboard with UserCard component. ([M7](MILESTONES.md#m7))`

### Don't over-aggregate

Two unrelated bug fixes in the same release stay separate:
- `Fixed off-by-one in date range filter. ([#159])`
- `Fixed null pointer in user serialization. ([#161])`

## Procedure

When `/bnac-changelog` is invoked:

1. **Read** existing `CHANGELOG.md` to find the latest version and its date
2. **Bash** — `git log <last-changelog-tag>..HEAD --pretty=format:"%H|%s|%b"` to enumerate new commits
3. **Filter** — drop commits whose type maps to (skip)
4. **Group** — by scope, then by milestone, then aggregate
5. **Detect breaking changes** — any `!` or `BREAKING CHANGE:` body
6. **Write entries** under `[Unreleased]`:
   - One bullet per logical change
   - Link to PR (find via `git log --merges` matching commit) or to milestone
   - Imperative past tense
7. **Validate** — ensure no entries are user-invisible refactors
8. **Edit** `CHANGELOG.md` — add to `[Unreleased]`, never modify released versions
9. **Log** to `project/.claude/log.md`

## Cutting a release

When `/bnac-changelog --release <version>` is invoked:

1. **Verify** — `[Unreleased]` is non-empty
2. **Detect semver bump** — if `### Removed` or breaking `### Changed`, suggest MAJOR; else if `### Added` or non-breaking `### Changed`, suggest MINOR; else PATCH
3. **Compare** with `<version>` argument — warn if mismatch
4. **Rename** `[Unreleased]` to `[<version>] — <today's date>`
5. **Insert** a fresh empty `[Unreleased]` above
6. **Edit** `CHANGELOG.md`
7. **Log** to `project/.claude/log.md`
8. **Recommend** — git tag `v<version>` and push

## Common mistakes

| Mistake | Fix |
|---|---|
| Listing every commit verbatim | Aggregate by logical change |
| Including refactors / tests / docs | Skip — not user-visible |
| Editing a released version | Released history is immutable |
| Wrong semver bump | Use the breaking-change detection rule |
| No links in entries | Always link to PR / milestone / issue |
| Marketing-speak | Stick to factual descriptions |
