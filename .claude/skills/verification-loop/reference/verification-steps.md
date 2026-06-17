# Verification Steps by Stack

## Node.js / TypeScript

| Step | Command | What It Checks |
|------|---------|---------------|
| Build | `npm run build` | Compilation, bundling |
| Type check | `tsc --noEmit` | Type safety without emitting files |
| Lint | `npm run lint` | Code style, potential errors |
| Test | `npm test` | Unit + integration tests |

## .NET

| Step | Command | What It Checks |
|------|---------|---------------|
| Build | `dotnet build --no-restore` | Compilation |
| Type check | (included in build) | — |
| Lint | `dotnet format --verify-no-changes` | Code formatting |
| Test | `dotnet test --no-build` | Unit + integration tests |

## Python

| Step | Command | What It Checks |
|------|---------|---------------|
| Build | `python -m py_compile <files>` | Syntax check |
| Type check | `mypy .` or `pyright .` | Type safety |
| Lint | `ruff check .` | Code style, potential errors |
| Test | `pytest` | Unit + integration tests |

## Flutter

| Step | Command | What It Checks |
|------|---------|---------------|
| Build | `flutter build` | Compilation |
| Type check | `dart analyze` | Static analysis |
| Lint | (included in analyze) | — |
| Test | `flutter test` | Widget + unit tests |

## Interpreting Results

- **0 errors, 0 warnings** — Clean. Proceed.
- **0 errors, N warnings** — Proceed, but note warnings for follow-up.
- **N errors** — Stop. Fix errors before proceeding.
- **Tests skipped** — Investigate why. Skipped tests may hide failures.
- **No tests found** — Note as WARNING. Tests should exist.
