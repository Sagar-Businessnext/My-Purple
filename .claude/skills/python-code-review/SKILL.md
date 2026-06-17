---
name: python-code-review
description: Structured Python code review checklist — mutable defaults, broad except, list comprehension vs loop, walrus operator misuse, and common quality pitfalls. Used by python-code-verifier and python-pr-approver.
user-invocable: false
argument-hint: ""
---

Systematic checklist for reviewing Python code quality beyond what linters catch automatically. This skill guides the reviewer through the most common Python-specific issues that lead to bugs or maintenance problems.

## Additional Resources

- [reference/review-checklist.md](reference/review-checklist.md) — full checklist with severity ratings and grep patterns
- [reference/common-pitfalls.md](reference/common-pitfalls.md) — explained anti-patterns with correct alternatives

## Steps

1. **Run tooling first** — `ruff check <path>` and `mypy <path>`; record all errors; these are non-negotiable findings
2. **Mutable defaults scan** — Grep for `def .*=\s*[\[\{]`; any mutable default in a function signature is a bug
3. **Exception handling scan** — Grep for bare `except:` and `except Exception:`; check if the handler swallows the error silently (no log, no re-raise)
4. **Type annotation coverage** — check all public function signatures; missing return type is a gap; `-> None` must be explicit
5. **Comprehension vs loop check** — comprehensions producing side effects (printing, mutating external state) should be refactored to loops
6. **Layering check** — routers should not contain business logic; services should not contain database queries; repositories should not call external HTTP
7. **Resource management** — file opens, database connections, and network sessions must use context managers
8. **Magic numbers** — unexplained numeric or string literals inside logic should be named constants
9. **Walrus operator check** — `:=` is valid but should not obscure readability; overly nested walrus expressions are a clarity issue

## Rules

- **All ruff and mypy errors are findings** — do not skip them as "just style"
- **Severity is objective** — mutable defaults, swallowed exceptions, and layering violations are High regardless of how small the function looks
- **Report grep pattern used** — when citing a finding, include the grep pattern that found it so the developer can verify locally
- **Walrus operator is not always a bug** — only flag when the expression becomes hard to read; give the benefit of the doubt for `while chunk := f.read(8192):`
