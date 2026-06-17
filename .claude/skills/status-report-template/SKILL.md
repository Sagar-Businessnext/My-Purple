---
name: status-report-template
description: Canonical format for status updates — done / in-progress / blockers / ETA. Used by bnac-status-update-agent.
user-invocable: false
argument-hint: ""
---

Generate stakeholder-readable status updates from the activity log, milestone tracker, and git history. Updates follow a fixed structure: Done, In progress, Blockers, ETA.

## Additional Resources

- [reference/format.md](reference/format.md) — status report structure, section headers, length guidance
- [reference/sources.md](reference/sources.md) — where to derive each section from (log.md, milestone-status.md, git, etc.)

## Format

```markdown
# Status Update — <project name>
**Period:** <start date> → <end date>
**Active milestone:** <ID — Title> (<n>/<total> tasks)

## Done
- <Outcome — what shipped or completed> ([link])
- <Outcome> ([link])

## In progress
- <Task or milestone> — <% complete or qualitative> — <owner if known>
- <Task> — <progress>

## Blockers
- <What's blocked> — <on whom or what> — <since when>
- (or "None")

## ETA
- **Active milestone completion:** <date estimate or "tracking">
- **Next milestone start:** <date or "after current">
- **Risks to ETA:** <bullet list, or "none">

## Notes
- <Anything that doesn't fit above but stakeholders should know>
```

## Rules

- **Four sections only** — Done, In progress, Blockers, ETA. (Notes is optional, fifth.)
- **Done means done** — Not "code merged but not deployed" — that's still "in progress" until users have it.
- **Outcomes, not activities** — "Login working in staging" not "Worked on login". Stakeholders want results.
- **Specific blockers** — "Blocked on infra-team approval for Postgres v15 (since 2026-04-22)" not "Waiting on infra".
- **ETA is a date or "tracking"** — Don't write "soon", "next sprint", "in a few weeks". Either give a date or say you can't yet.
- **Period is the reporting window** — Default = since last status update. Always show the dates.
- **Length: under one page** — If longer, the report is too detailed. Drill-downs go elsewhere.
- **Link liberally** — PRs, milestones, decisions. Stakeholders may want to dig in.
