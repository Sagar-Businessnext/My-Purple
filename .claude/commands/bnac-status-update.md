Invoke the **bnac-status-update-agent** to generate a stakeholder-readable status update (Done / In progress / Blockers / ETA).

**Agent:** `bnac-status-update-agent`
**Target:** `$ARGUMENTS` (optional — `--since <date>` to set period; `--audience exec|standup` to adjust output)

## What to do

1. Delegate to the `bnac-status-update-agent` with these instructions:
   - If no arguments → period auto-detects from most recent `STATUS-*.md` file (or 7 days back)
   - If `--since <YYYY-MM-DD>` → period starts on that date
   - If `--audience exec` → one-paragraph executive summary
   - If `--audience standup` → Blockers section only

2. The bnac-status-update-agent will:
   - **Read** context chain (CLAUDE.md, SUMMARY.md, milestone-status.md)
   - **Resolve** the reporting period (per `status-report-template/reference/sources.md`)
   - **Bash** — `git log --merges` for the period to find shipped work
   - **Read** `log.md` for completed entries and blockers (`BLOCKED:`, `waiting on`, etc.)
   - **Read** `milestone-status.md` for active milestone progress
   - Compute velocity and ETA from last 7 days of completed tasks
   - Aggregate Done by feature / milestone (not per commit)
   - Build the four sections: Done / In progress / Blockers / ETA (plus optional Notes)
   - **Write** `STATUS-<YYYY-MM-DD>.md` (or to a path given in arg)
   - Adjust output for audience tag if provided

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-status-update                                → status for the period since last update (or 7 days)
/bnac-status-update --since 2026-04-01            → status from April 1 to today
/bnac-status-update --audience exec               → one-paragraph executive summary
/bnac-status-update --audience standup            → Blockers section only (for daily standup)
```
