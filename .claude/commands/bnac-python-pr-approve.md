Invoke the **python-pr-approver** agent to perform final merge-gate sign-off on a Python pull request.

**Agent:** `python-pr-approver`
**Target:** `$ARGUMENTS` (PR number, branch name, or empty for current branch)

## What to do

1. Delegate to the `python-pr-approver` agent with these instructions:
   - If `$ARGUMENTS` is a PR number or URL → review the specified open PR
   - If `$ARGUMENTS` is a branch name → review the branch diff against `main` or `develop`
   - If no arguments → review the current branch against its base

2. The `python-pr-approver` agent will:
   - **Read** context chain (`CLAUDE.md`, `SUMMARY.md`, project `CLAUDE.md`)
   - Verify all three gates have passed (zero blockers):
     - `python-code-verifier` — typing, idioms, layering
     - `python-security-checker` — OWASP, bandit, secrets
     - `python-compliance-checker` — structure, naming, imports
   - Run `pytest` to confirm all tests pass
   - Review the full diff holistically: typed API, tests for new behavior, error handling, commit hygiene
   - Produce an **APPROVED** or **BLOCKED** decision with specific, actionable reasons
   - Log the decision to `project/.claude/log.md`

3. The agent does not modify code — the decision is returned as a report

## Examples

```
/bnac-python-pr-approve
/bnac-python-pr-approve feature/PROJ-123-add-email-verification
/bnac-python-pr-approve 456
```

## Pre-conditions

Run these three checks before calling this command and ensure they report zero blockers:

```
/bnac-python-verify
/bnac-python-security-check
/bnac-python-compliance-check
```

If any check has blockers, fix them first. `python-pr-approver` will block if gate evidence is missing.
