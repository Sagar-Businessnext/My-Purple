---
name: code-review
description: General-purpose code review skill — runs on any tech stack. Reviews for correctness, security, OOP design, design patterns (suggested), null safety, type cast safety, performance, duplication, dead code, and over- / under-engineering. Produces a findings file (`summary.vins.md` by default) with severity-classified rows.
user-invocable: true
argument-hint: "<file-or-directory> [--out <file>]"
---

Review `$ARGUMENTS` and write structured findings.

This skill is **stack-agnostic**. It applies universal categories to any language and adds per-stack overlays (TypeScript/JS, C#/.NET, Python, Java/Kotlin, Go, Dart/Flutter, SQL, CSS/SCSS).

## Additional Resources

- [reference/review-checklist.md](reference/review-checklist.md) — full universal checklist + per-stack overlays

## Output destination (MANDATORY)

The skill writes to a file — it does not just print to chat.

| Invocation | Output path |
|------------|-------------|
| `--out <file>` provided | `<file>` (overwrite) |
| Target is a folder `X/` | `X/summary.vins.md` |
| Target is a file `X/a.ts` | `X/summary.vins.md` (parent folder) |
| No target (git-diff mode) | `<repo-root>/summary.vins.md` |
| Multiple unrelated targets | `<repo-root>/summary.vins.md` |

If `summary.vins.md` already exists at the resolved path, overwrite it — this file is a per-review report, not an append log. Print the resolved path before writing.

## Steps

1. Read context chain: `~/.claude/CLAUDE.md` → `project/.claude/CLAUDE.md` → `project/.claude/SUMMARY.md` → `project/.claude/milestone-status.md` → `project/.claude/memory/MEMORY.md` → `project/.claude/context/carry-forward.md`
2. Read all applicable rules from `~/.claude/rules/` and `project/.claude/rules/`
3. **Detect stack(s)** from project manifests (`package.json`, `*.csproj`, `pyproject.toml`, `pubspec.yaml`, `go.mod`, `pom.xml`, `build.gradle`). Record detected stack in the report header.
4. **Resolve output path** per the table above. Print it.
5. Enumerate target files (Glob for folder, single file, or `git diff --name-only` for no-target).
6. Read target files **fully** — not just the diff.
7. Run **universal checks** (see checklist).
8. Run **per-stack overlays** for the detected stack(s).
9. Run **targeted greps** for high-signal smells (see agent doc / checklist).
10. Classify each finding: CRITICAL, WARNING, INFO. Assign category from the universal vocabulary.
11. **Write** the findings file at the resolved path.
12. Append a log entry to `project/.claude/log.md`.

## Universal review categories

Apply to any language. Detailed checks live in [reference/review-checklist.md](reference/review-checklist.md).

| Category | What to check |
|----------|---------------|
| **Correctness** | Logic errors, off-by-one, wrong operators, race conditions, edge cases, ignored return values |
| **Security** | Injection (SQL/XSS/cmd/path), secrets in source, broken auth, missing input validation, unsafe deserialization, weak crypto |
| **Null Safety** | Unguarded property access on nullable, non-null assertions on untrusted source, missing defaults, defensive over-coding |
| **Type Safety / Type Cast** | `any` / `dynamic` / `object`-leak, unsafe casts (`as Foo`, `(Foo)x`), missing return types, type-erasure abuse |
| **OOP Design** | SOLID violations (god-class, leaky abstraction, fat interface, wrong inheritance, concrete dependency), composition-vs-inheritance, mutable shared state |
| **Design Patterns (suggest)** | Where a known pattern would simplify — Factory, Strategy, Adapter, Observer, Repository, Builder, Decorator, Template Method, Null Object; flag misapplied patterns |
| **Error Handling** | Swallowed exceptions, bare catch-all, raw stack traces to user, no retry on transient, missing cleanup in finally/using/defer/with |
| **Performance** | Unnecessary work in hot paths, N+1 queries, sync-over-async, missing pagination, missing memoization, allocations in tight loops, blocking I/O in async context, recreated formatters/regex per call |
| **Duplicate / DRY** | Copy-paste blocks, duplicate constants, duplicate types, parallel hierarchies that should share a base |
| **Unused / Dead** | Unused imports, params, locals, unreachable branches, dead flags, unused exports, commented-out code |
| **Over-engineering** | Premature abstraction (interface w/ one impl), speculative generics, factory-of-factories, deep inheritance for a leaf, unused configurability |
| **Under-engineering** | Magic numbers/strings, no extraction at boundary, copy-paste instead of helper, no validation at trust boundary, hard-coded env values |
| **Standards** | Naming, file organization, import order, TODOs w/o ticket, debug logs left behind |

## Stack-specific overlays

After the universal pass, apply the per-stack table for the detected stack(s). Each table is ~10–15 high-signal language-specific smells (e.g., `Task.Result` deadlock in .NET, mutable default args in Python, `interface{}` in Go public APIs, `dynamic` + `as` in Dart). See [reference/review-checklist.md](reference/review-checklist.md) for the tables.

## Severity

| Level | Meaning |
|-------|---------|
| **CRITICAL** | Must fix before merge — security, data loss, logic bug, runtime break, broken types |
| **WARNING** | Should fix — anti-pattern, perf regression, dead code, standards violation |
| **INFO** | Nice to have — better naming, cleaner approach, pattern suggestion |

## Output format (the report file)

```markdown
# Code Review — <target>

- **Reviewed:** <ISO date>
- **Reviewer:** bnac-reviewer
- **Target:** <path>
- **Files reviewed:** <N>
- **Detected stack(s):** <e.g., TypeScript (primary), SCSS>
- **Output path:** <resolved path>

## Findings

| # | Severity | File:Line | Category | Issue | Suggested Fix |
|---|----------|-----------|----------|-------|---------------|
| 1 | CRITICAL | ... | Security | ... | ... |
| 2 | WARNING  | ... | Null Safety | ... | ... |

## Summary

- **CRITICAL:** X
- **WARNING:** Y
- **INFO:** Z
- **Total:** N
- **Verdict:** APPROVE | REQUEST CHANGES | NEEDS DISCUSSION

## By category

| Category | CRITICAL | WARNING | INFO |
|----------|----------|---------|------|
| ... | | | |
```

## Verdict rules

| Verdict | When |
|---------|------|
| **APPROVE** | 0 CRITICAL and ≤ 3 WARNING |
| **REQUEST CHANGES** | ≥ 1 CRITICAL, or many WARNING (> 10) |
| **NEEDS DISCUSSION** | Architecture concerns (OOP Design / Design Patterns / Over- / Under-engineering) needing a team call |
