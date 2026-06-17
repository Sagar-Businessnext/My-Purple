---
name: release-approval
description: Stakeholder GO / NO-GO release approval protocol. Defines who can approve at each release tier, what evidence must be cited, and the canonical sign-off record format. Used by bnac-go-nogo-approver.
user-invocable: false
argument-hint: ""
---

`bnac-quality-gate` reports automated PASS / FAIL on build + type + lint + tests. That is necessary but **not sufficient** for a production release — production cutover needs a human owner. This skill defines the GO / NO-GO protocol that closes gap #8 from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

**Authoritative source:** This skill body. The per-release sign-off record (`project/.claude/release-approval.md`) is the per-project instance.

## Additional Resources

- [reference/approval-tiers.md](reference/approval-tiers.md) — release tiers, approver matrix, required evidence per tier
- [reference/approval-record-format.md](reference/approval-record-format.md) — on-disk format of `release-approval.md`

## Steps

1. **Identify the release tier** — `hotfix`, `patch`, `minor`, `major`. The tier determines who can approve and what evidence is required (see [reference/approval-tiers.md](reference/approval-tiers.md)).
2. **Gather evidence** — at minimum: latest `quality-gate-report.md` PASS, latest `VALIDATION_REPORT.md` PROCEED, security-review.md PASS. Higher tiers add UAT sign-off, perf-test results, change-advisory-board minutes.
3. **Open the request** — append a `## Request` block to `release-approval.md` with release tier, target environment, deploy window, evidence references, and the requested approver list.
4. **Notify approvers** — out of scope for this skill (use existing notification channel — Slack / email / PR comment). The skill enforces the on-disk record, not the human workflow.
5. **Record decisions** — each approver appends a `## Decision` block: GO / NO-GO, approver name + role + timestamp, evidence reviewed, optional conditions.
6. **Compute outcome** — overall outcome is `GO` only when every required approver has signed `GO`. A single `NO-GO` overrides. Conditional `GO` is allowed but must list the conditions and a re-check owner.
7. **Update the consolidated `Decision` block** at the top of the file — single source of truth that the pipeline state tracker (gap #2) reads as a guard.

## Rules

- **Automated quality gate is not approval** — `bnac-quality-gate ✅` is one piece of evidence; it does not authorize a release. Only a recorded `GO` from the required approvers authorizes a release.
- **The release-approval.md file is the contract** — Slack thumbs-ups, email approvals, and verbal sign-offs do not count. If it is not in the file, it did not happen.
- **No retroactive approval** — Sign-off timestamps must be in the past at the moment the pipeline state tracker reads the file, AND must be after the referenced evidence files' mtimes. Approvals cited from before the evidence existed are rejected.
- **A NO-GO from any required approver blocks the release** — There is no majority-rules override. If a required approver says NO-GO, the only paths are: address their concern and re-request, or rollback the pipeline.
- **Conditional GO must list conditions explicitly** — "GO if we add monitoring for X" is valid; "GO with caveats" is not.
- **One approval record per release attempt** — Re-requests after a NO-GO get a new `release-approval.md` (the prior one is rotated to `release-approval-<run_id>-<attempt>.md`). The active file is the active attempt.
- **Approver identity must be verifiable** — Name + role + (org email or org Slack handle). The skill does not enforce SSO; it does enforce that the identity field is non-empty and structured.
- **The pipeline state tracker is the consumer, not the writer of the consolidated outcome** — `bnac-go-nogo-approver` writes the file; `bnac-pipeline-state-tracker` reads it as a guard on T07 (acceptance-testing → release-prod).
