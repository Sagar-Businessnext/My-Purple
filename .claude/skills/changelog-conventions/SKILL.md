---
name: changelog-conventions
description: keep-a-changelog format and BusinessNext conventions for CHANGELOG.md — sections, version headings, commit-to-entry mapping. Used by bnac-changelog-agent.
user-invocable: false
argument-hint: ""
---

Maintain `CHANGELOG.md` in [keepachangelog.com](https://keepachangelog.com/en/1.1.0/) format with BusinessNext-specific conventions for grouping, links, and milestone alignment.

## Additional Resources

- [reference/format.md](reference/format.md) — keep-a-changelog structure, section headers, version headings
- [reference/commit-mapping.md](reference/commit-mapping.md) — how conventional commits map to changelog sections

## Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features merged but not yet released

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in a future release

### Removed
- Features removed in this release

### Fixed
- Bug fixes

### Security
- Security-relevant changes

## [1.2.0] — 2026-04-30

### Added
- BNAC profile with planning hierarchy ([P2 plan](.claude/plan.md))
- `/bnac-plan` top-level command

### Changed
- Renamed cross-stack agents to `bnac-*` prefix (D6 enforcement)
```

## Rules

- **Six section names only** — Added, Changed, Deprecated, Removed, Fixed, Security. Do not invent new sections.
- **Most recent at top** — `[Unreleased]` first, then versions in descending order.
- **Link to context** — Every entry should link to the underlying source (PR, issue, milestone, decision doc) when possible.
- **One entry per logical change** — Multiple commits for one feature get one entry, not one per commit.
- **Imperative past tense** — "Added user authentication" not "Adds user authentication" or "Adding user authentication".
- **No marketing language** — "Lightning-fast new search" → "Search performance improved (P95 200ms → 80ms)".
- **Date format is YYYY-MM-DD** — ISO 8601, no other format.
- **Don't backfill** — Only document changes that actually happened. Don't synthesize a changelog from scratch unless explicitly asked.
