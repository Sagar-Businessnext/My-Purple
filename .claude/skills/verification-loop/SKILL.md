---
name: verification-loop
description: Run build → type check → lint → test verification cycle. Used by quality gates and milestone completion.
user-invocable: true
argument-hint: ""
---

Run the full verification loop: build, type check, lint, and tests.

## Additional Resources

- [reference/verification-steps.md](reference/verification-steps.md) — detailed verification procedure

## Steps

1. Read `project/.claude/CLAUDE.md` to determine available build/test commands
2. Run each verification step in order
3. If any step fails, stop and report
4. If all pass, report success

## Verification Order

```
Build → Type Check → Lint → Test
  ↓         ↓          ↓       ↓
 FAIL?    FAIL?      FAIL?   FAIL?
  ↓         ↓          ↓       ↓
 STOP      STOP       STOP    STOP
```

Each step must pass before proceeding to the next. There's no point running tests if the build is broken.

## Output Format

```markdown
## Verification Results

| Step | Status | Duration | Details |
|------|--------|----------|---------|
| Build | PASS | 3.2s | 0 errors, 0 warnings |
| Type check | PASS | 1.8s | 0 errors |
| Lint | PASS | 0.9s | 0 errors, 2 warnings |
| Tests | PASS | 12.4s | 42 passed, 0 failed, 0 skipped |

**Overall: PASS**
```

## When Used

- Before marking a milestone task as complete
- As part of `/bnac-quality-gate` command
- After `/bnac-build-fix` to verify all issues resolved
- After `/bnac-feature-dev` to confirm feature works
