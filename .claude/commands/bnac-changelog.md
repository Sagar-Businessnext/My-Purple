Invoke the **bnac-changelog-agent** to update CHANGELOG.md with new entries from git history (keep-a-changelog format).

**Agent:** `bnac-changelog-agent`
**Target:** `$ARGUMENTS` (optional — `--release <version>` to cut a release; `--rebuild` to regenerate `[Unreleased]`)

## What to do

1. Delegate to the `bnac-changelog-agent` with these instructions:
   - If no arguments → append new entries under `[Unreleased]` from commits since last release
   - If `--release <version>` → rename `[Unreleased]` to `[<version>] — <today>`, insert fresh empty `[Unreleased]`
   - If `--rebuild` → regenerate `[Unreleased]` from scratch (warn first — existing `[Unreleased]` is replaced)

2. The bnac-changelog-agent will:
   - **Read** existing `CHANGELOG.md` to find latest version + date
   - **Bash** — `git log <last-tag>..HEAD` to enumerate commits
   - Filter out non-user-visible types (refactor, chore, docs, test, style, ci) per `changelog-conventions` skill
   - Group commits by scope and milestone (3+ same-scope = one entry; same-milestone = one entry)
   - Detect breaking changes (`!` in subject or `BREAKING CHANGE:` body)
   - Build entries in imperative past tense with links to PR / milestone / decision
   - **Edit** `CHANGELOG.md` — only `[Unreleased]` and new release sections; released versions are immutable
   - For `--release`: detect semver bump from change types, compare with provided version, warn on mismatch
   - Recommend `git tag` + push (does not execute)

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-changelog                     → append new entries under [Unreleased] from recent commits
/bnac-changelog --release 1.3.0    → cut version 1.3.0 with today's date
/bnac-changelog --rebuild           → regenerate [Unreleased] from scratch (with confirmation)
```
