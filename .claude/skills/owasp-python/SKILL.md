---
name: owasp-python
description: OWASP Top 10 mapped to Python — SQL injection via string formatting, unsafe deserialization with pickle, XSS in Jinja2 templates, CSRF, and server-side mitigations. Used by python-security-checker.
user-invocable: false
argument-hint: ""
---

Maps the OWASP Top 10 (2021) to concrete Python code patterns and their mitigations. Each category includes the Python-specific attack vector, a vulnerable code example, and the corrected pattern. Use this skill to classify security findings and recommend fixes.

## Additional Resources

- [reference/top10-mapping.md](reference/top10-mapping.md) — all 10 categories with Python-specific attack vectors and example code
- [reference/mitigations.md](reference/mitigations.md) — library-level mitigations, FastAPI middleware configuration, and safe patterns

## Steps

1. **Identify the data flow** — trace user-controlled input from the entry point (HTTP body, query param, header, file upload) to every sink (database query, shell command, template render, file path)
2. **Classify each sink** — assign the relevant OWASP category (A01–A10)
3. **Check the mitigation** — is the correct library/pattern used? (parameterized query, auto-escaped template, HMAC-signed token)
4. **Check deserialization paths** — any use of `pickle`, `marshal`, `yaml.load` (unsafe loader), `eval`, or `exec` with external data
5. **Check secret management** — credentials are not hardcoded; environment variables or a secrets manager is used
6. **Check authentication** — JWT validation uses a library (e.g., `python-jose`, `PyJWT`) with algorithm whitelisting; not manual parsing
7. **Report findings** with OWASP category code (A01–A10) and line reference

## Rules

- **Every finding gets an OWASP category** — do not report "injection risk" without specifying A03
- **Pickle is always a finding** — `pickle.loads()` on data from any external source is Critical regardless of context; flag it
- **`eval()` on external data is Critical** — no exceptions
- **`yaml.safe_load()` is acceptable; `yaml.load()` without `Loader=yaml.SafeLoader` is a finding**
- **False positives must be noted** — if a `pickle.loads()` call only processes data from an internal queue with known producers, mark as Low with the justification; do not silently skip it
