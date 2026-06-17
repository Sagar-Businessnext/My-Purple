# Status Report Format Reference

Status updates are stakeholder-readable summaries — concise, factual, and structured for skim-reading.

## Required structure

```markdown
# Status Update — <project name>
**Period:** <YYYY-MM-DD> → <YYYY-MM-DD>
**Active milestone:** <ID — Title> (<completed>/<total> tasks)

## Done
[bullets]

## In progress
[bullets]

## Blockers
[bullets, or "None"]

## ETA
- **Active milestone completion:** <date or "tracking">
- **Next milestone start:** <date or "after current">
- **Risks to ETA:** <bullets, or "none">

## Notes
[optional — bullets]
```

## Section content rules

### Header line
- `# Status Update — <project name>` — exact format, em-dash separator
- `**Period:**` — ISO 8601 dates, both sides
- `**Active milestone:**` — milestone ID + title + task ratio

### Done
- Outcomes that landed during the reporting period
- Past tense, imperative: "Shipped login. Auth working end-to-end on staging."
- Link to PR / milestone / decision when available
- Aggregate by feature; don't list every commit
- 3–8 bullets is normal. More than 10 → too detailed, aggregate further.

### In progress
- Active work — not yet done, not blocked
- Each bullet: what + progress + owner (if relevant)
- Progress can be `<%>`, fraction (`3/5 tasks`), or qualitative (`code complete, awaiting review`)
- 2–6 bullets is normal

### Blockers
- Things stopping progress
- Each bullet: what's blocked + on whom/what + since when
- "None" is a valid and good answer
- If a blocker has been there > 2 weeks, mark it as **stale** and call out

### ETA
Always 3 lines:
1. **Active milestone completion:** date estimate, or "tracking" if on schedule, or "delayed by N days" if known
2. **Next milestone start:** date, or "after current"
3. **Risks to ETA:** bullets of named risks, or "none"

### Notes (optional)
- Anything that doesn't fit but stakeholders should know
- Personnel changes, vendor issues, scope adjustments, learnings
- Skip the section entirely if empty (don't write "None" here)

## Length

| Audience | Length |
|---|---|
| Engineering manager | < 1 page (this template) |
| Executive | One paragraph + a link to the full update |
| Daily standup | Verbal — only Blockers section matters |
| Weekly sync | Full template |

This skill produces the **full template**. Other audiences are derived from it manually.

## Tone

| Rule | Example |
|---|---|
| Factual, not aspirational | "Tracking" not "On track for awesome delivery" |
| Specific dates | "2026-05-08" not "early May" |
| Specific blockers | "Blocked on infra-team approval (since 2026-04-22)" not "Waiting on infra" |
| Outcomes, not activities | "Auth working in staging" not "Worked on auth" |
| No hedging | "Tracking" or "delayed by 3 days" — not "should probably be done by maybe end of week" |
| No marketing | "P95 latency 200ms → 80ms" not "Made search blazingly fast" |

## Anti-patterns

| Anti-pattern | Why bad | Fix |
|---|---|---|
| Reporting effort instead of outcomes | "Spent 3 days on auth" — stakeholder doesn't care | Report what's working that wasn't before |
| "Done" items that aren't deployed | Misleads on actual progress | Move to "In progress" until users have it |
| Vague ETAs ("soon", "next month") | Useless for planning | Date, or admit you don't know yet |
| Multi-page status | Nobody reads it | Aggregate; use the under-1-page rule |
| No blockers section ever | Either you're hiding them or not paying attention | Always include the section, even if "None" |
| Same status update copy-pasted | Reader can't tell what changed | If period had no progress, say so explicitly |
