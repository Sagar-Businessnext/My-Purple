# Keep-a-Changelog Format Reference

`CHANGELOG.md` follows [keepachangelog.com v1.1.0](https://keepachangelog.com/en/1.1.0/) with the BusinessNext additions noted below.

## File header

Every CHANGELOG.md starts with:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

## Version heading shape

```markdown
## [<version>] — <YYYY-MM-DD>
```

| Element | Format |
|---|---|
| Version | Semver — `[1.2.0]`, `[0.4.1]`, `[2.0.0-rc.1]` |
| Em-dash separator | ` — ` (with spaces) |
| Date | ISO 8601 — `2026-04-30` |

For unreleased changes:

```markdown
## [Unreleased]
```

`[Unreleased]` is always the topmost section. When you cut a release, rename `[Unreleased]` to the version + date and add a fresh `[Unreleased]` above it.

## Section headers (the six only)

| Header | Use for |
|---|---|
| `### Added` | New features, capabilities, public APIs |
| `### Changed` | Modifications to existing functionality (API behavior, defaults, UX) |
| `### Deprecated` | Features that still work but are slated for removal |
| `### Removed` | Features that no longer exist |
| `### Fixed` | Bug fixes — incorrect behavior corrected |
| `### Security` | Security-relevant changes — vulnerability patches, hardening |

These six are the only allowed sections. No "Misc", "Internal", "Refactoring", "Tests", "Docs". If a change isn't user-visible, it doesn't belong in the changelog.

## Entry format

```markdown
- <Imperative past-tense description>. ([link to source])
```

Examples:
- `Added user authentication via JWT. ([#142](https://github.com/x/repo/pull/142))`
- `Changed default page size from 20 to 50. ([M7](MILESTONES.md#m7))`
- `Fixed off-by-one in date range filter. ([#159](https://github.com/x/repo/pull/159))`

### Linking to source

Every entry should link to one of:
- PR — `[#142](url)`
- Issue — `[#99](url)`
- Milestone — `[M7](MILESTONES.md#m7)`
- Decision record — `[D6](.claude/plan.md#d6)`

Multiple links are fine if relevant: `Added X. ([#142](pr-url), [M7](milestone-url))`

## Sub-grouping inside a section

For long sections (> 6 entries), allow one level of `####` sub-grouping by feature area:

```markdown
### Added

#### Authentication
- JWT signing utility ([#142])
- Login endpoint ([#143])

#### Reports
- PDF export ([#150])
- Scheduled email delivery ([#151])
```

Don't sub-group sections with < 6 entries — adds noise.

## Versioning rules (semver alignment)

| Change type | Semver bump |
|---|---|
| Breaking change (Removed, breaking Changed) | MAJOR |
| New feature, backwards-compatible (Added, non-breaking Changed) | MINOR |
| Bug fix only (Fixed) | PATCH |
| Security patch | PATCH (or higher if also breaking) |

If `[Unreleased]` contains both `Added` and `Removed`, the next release is MAJOR. The agent should detect this and warn before cutting a release.

## Anti-patterns

| Anti-pattern | Why bad | Fix |
|---|---|---|
| Section "Internal" / "Misc" | Not user-visible — doesn't belong | Drop the entry, or rephrase as user-visible |
| Marketing language ("blazing-fast new search") | Not factual | "Search P95 latency reduced from 500ms to 80ms" |
| One entry per commit | Spam — readers can't see the feature | Aggregate by logical change |
| Future date | Pretends a release happened | Use the actual merge date |
| Missing link | Reader can't find context | Link to PR / issue / milestone / decision |
| Edits to released versions | Released history is immutable | Add a note in the next release |
