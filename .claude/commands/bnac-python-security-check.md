Invoke the **python-security-checker** agent to scan Python code for OWASP Top 10 vulnerabilities, bandit rule violations, and hardcoded secrets.

**Agent:** `python-security-checker`
**Target:** `$ARGUMENTS` (optional path to scan; defaults to entire project)

## What to do

1. Delegate to the `python-security-checker` agent with these instructions:
   - If `$ARGUMENTS` is a path → restrict scan to that directory or file
   - If no arguments → scan the entire project

2. The `python-security-checker` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - Run `bandit -r <path>` and parse the JSON output
   - Run `pip-audit` to check for known CVEs in dependencies
   - Grep for dangerous patterns bandit may miss: `eval(`, `pickle.loads(`, raw SQL f-strings, hardcoded credentials
   - Map all findings to OWASP Top 10 categories (A01–A10)
   - Produce a structured security findings report (file, line, severity, OWASP category, bandit code, recommended fix)
   - Log the scan summary to `project/.claude/log.md`

3. The agent does not modify code — findings are returned as a report

## Examples

```
/bnac-python-security-check
/bnac-python-security-check src/auth/
/bnac-python-security-check src/users/repository.py
```

## Next step

After reviewing findings, use `/bnac-python-feature-dev` to fix Critical and High findings before proceeding to PR approval. Then run `/bnac-python-pr-approve` for final sign-off.
