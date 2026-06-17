---
name: python-security-bandit
description: Bandit static analysis reference — common B-codes, their meaning, severity/confidence matrix, and the BusinessNext policy for suppressing false positives. Used by python-security-checker.
user-invocable: false
argument-hint: ""
---

Reference for running and interpreting `bandit` output in BusinessNext Python projects. Bandit assigns each finding a rule ID (B-code), a severity (LOW/MEDIUM/HIGH), and a confidence (LOW/MEDIUM/HIGH). This skill describes the most common B-codes, when they are genuine findings versus false positives, and the approved suppression policy.

## Additional Resources

- [reference/b-codes-reference.md](reference/b-codes-reference.md) — B-code lookup: ID, name, severity, common context
- [reference/suppression-policy.md](reference/suppression-policy.md) — when `# nosec` is allowed, required comment format, and the review process

## Steps

1. **Run bandit** — `bandit -r <path> -f json -o bandit-report.json` then `bandit -r <path>` for terminal output
2. **Filter by severity** — High severity findings are blockers; Medium are required fixes; Low are informational
3. **Look up B-codes** — use the `b-codes-reference.md` to understand each finding's context
4. **Assess confidence** — a HIGH severity / LOW confidence finding may be a false positive; investigate the code before reporting
5. **Apply suppression policy** — only suppress with `# nosec B###` (specific code) after confirming it is a false positive; never `# nosec` without a code
6. **Cross-reference with OWASP** — map each High/Medium finding to the `owasp-python` skill category for the final report

## Rules

- **All HIGH severity findings are blockers** — regardless of confidence level; investigate and either fix or suppress with documented justification
- **`# nosec` without a B-code is not allowed** — `# nosec B605` is acceptable; `# nosec` alone is a compliance violation
- **Suppressions require a comment** — the line above the suppression must explain why it is a false positive
- **bandit is additive, not definitive** — a clean bandit scan does not mean the code is secure; manual review of deserialization and SQL paths is still required
- **Never suppress B301 (pickle), B302 (marshal), B506 (yaml.load) without escalation** — these require explicit security team sign-off
