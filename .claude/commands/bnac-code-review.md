Invoke the **bnac-reviewer** agent to review code on any stack (TS/JS, C#/.NET, Python, Java/Kotlin, Go, Dart/Flutter, SQL, CSS/SCSS). Covers correctness, security, OOP design, design patterns (suggested), null safety, type-cast safety, performance, duplication, dead code, and over- / under-engineering.

**Agent:** `bnac-reviewer`
**Arguments:** `$ARGUMENTS` — `[path] [--out <file>]`

## Argument shape

| Argument | Meaning |
|----------|---------|
| `<path>` file | Review that single file |
| `<path>` folder | Review every file under that folder |
| no path | Review uncommitted changes (`git diff` + `git diff --staged`) |
| `--out <file>` | Write findings to `<file>` instead of the default `summary.vins.md` |

## Output file (when `--out` is not provided)

| Target | Default output file |
|--------|---------------------|
| Folder `X/` | `X/summary.vins.md` |
| File `X/a.ts` | `X/summary.vins.md` (parent folder) |
| Git-diff mode (no path) | `<repo-root>/summary.vins.md` |
| Multiple unrelated targets | `<repo-root>/summary.vins.md` |

Existing `summary.vins.md` is overwritten — the report is per-review, not append-log.

## What the agent does

1. Reads the context chain (`~/.claude/CLAUDE.md` → `project/.claude/CLAUDE.md` → `SUMMARY.md` → `milestone-status.md` → `memory/MEMORY.md` → `context/carry-forward.md`).
2. Reads applicable rules from `~/.claude/rules/` and `project/.claude/rules/`.
3. **Detects the stack** from project manifests (`package.json`, `*.csproj`, `pyproject.toml`, `pubspec.yaml`, `go.mod`, `pom.xml`).
4. **Resolves output path** per the table above. Prints it before writing.
5. Enumerates target files (Glob for folder, single file, or `git diff --name-only`).
6. Reads each file fully (not just the diff).
7. Greps for high-signal violation patterns (stack-tuned).
8. Runs the **universal checklist** (Correctness, Security, Null Safety, Type Safety / Type Cast, OOP Design, Design Patterns suggest, Error Handling, Performance, Duplicate/DRY, Unused/Dead, Over-engineering, Under-engineering, Standards).
9. Runs the **stack-specific overlay** for the detected stack(s).
10. Classifies findings: CRITICAL / WARNING / INFO.
11. **Writes** the findings file (markdown table + summary + by-category breakdown + verdict).
12. Logs the run to `project/.claude/log.md`.

The verdict is **APPROVE** (0 critical, ≤ 3 warning), **REQUEST CHANGES** (≥ 1 critical, or many warnings), or **NEEDS DISCUSSION** (architecture / OOP / pattern concerns needing team input).

## Examples

```
/bnac-code-review                                            → review uncommitted git changes; writes <repo-root>/summary.vins.md
/bnac-code-review src/components/Auth/                       → writes src/components/Auth/summary.vins.md
/bnac-code-review src/utils/formatDate.ts                    → writes src/utils/summary.vins.md
/bnac-code-review src/                                       → writes src/summary.vins.md
/bnac-code-review src/auth/ --out reports/auth-review.md     → writes reports/auth-review.md
/bnac-code-review --out summary.md                           → review git diff, write summary.md at repo root
```
