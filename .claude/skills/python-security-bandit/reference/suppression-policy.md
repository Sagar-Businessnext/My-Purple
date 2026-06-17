# Bandit Suppression Policy

## When Suppression Is Allowed

A `# nosec` suppression is allowed only when ALL of the following are true:

1. The finding is a confirmed false positive (the code is not exploitable in its context)
2. The B-code is listed in the finding (never bare `# nosec`)
3. A justification comment appears on the preceding line
4. The suppression is reviewed and approved in the PR by `python-pr-approver`

## Suppression Format

```python
# nosec: B303 — md5 used as cache key (ETag), not for security; input is server-controlled content bytes
cache_key = hashlib.md5(file_content).hexdigest()  # nosec B303
```

The justification comment must:
- Reference the B-code by number
- Explain why the code is not exploitable in this context
- Identify what makes it safe (e.g., "input is server-controlled", "used in test fixtures only")

## Suppressing a Block

For multiple lines with the same false positive:

```python
# nosec: B101 — assert used for type narrowing in test helpers; production code does not execute this path
assert isinstance(result, UserResponse)  # nosec B101
assert result.id > 0  # nosec B101
```

Do not use a single `# nosec` at the top of a file (`# type: ignore` style) — this suppresses all findings including future genuine ones.

## B-Codes That Require Escalation

These codes must never be suppressed at the developer level — they require security team sign-off:

| B-Code | Rule | Reason for Escalation |
|--------|------|----------------------|
| B301 | pickle | Unsafe deserialization is rarely truly safe; alternatives exist |
| B302 | marshal | Same as pickle |
| B506 | yaml.load | Use `yaml.safe_load()` — the fix is trivial; suppression is unnecessary |
| B307 | eval | Legitimate use cases are extremely rare; escalate to confirm |
| B602 | shell=True | `shell=False` with an explicit argument list is always possible |

## Suppression Audit

All `# nosec` comments are tracked. During compliance checks, `python-compliance-checker` Greps for `# nosec` occurrences and lists them in the report with their justification status. Suppressions without justification comments are compliance violations.

## Alternatives to Suppression

Before suppressing, consider whether a refactor removes the risk:

```python
# INSTEAD OF suppressing B608:
# nosec: B608 — query is built from validated enum, not raw user input
query = f"SELECT * FROM {table_name}"  # nosec B608

# REFACTOR to eliminate the finding:
ALLOWED_TABLES = {"users", "orders", "products"}
if table_name not in ALLOWED_TABLES:
    raise ValueError(f"Invalid table: {table_name}")
result = await db.execute(text(f"SELECT * FROM {table_name}"))
# bandit no longer flags this because the risk is mitigated by the explicit allowlist check
```
