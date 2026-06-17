# Sources for Status Updates

`bnac-status-update-agent` derives each section of a status update from specific sources. This file is the mapping.

## Source priority

For any given fact, sources have a priority order. Use the highest-priority source first; fall back to lower-priority sources only if the higher one is missing.

| Section | Primary source | Secondary | Tertiary |
|---|---|---|---|
| **Done** | `git log` (merged PRs) | `project/.claude/log.md` (activity log) | `milestone-status.md` (completed milestones) |
| **In progress** | `project/.claude/milestone-status.md` (active milestone tasks) | `git log` (open WIP commits) | `project/.claude/log.md` |
| **Blockers** | `project/.claude/log.md` (entries marked "blocked") | `milestone-status.md` notes | Manual user input |
| **ETA / milestone completion** | `milestone-status.md` (task progress) | Recent velocity from `log.md` | Manual estimate |
| **Risks to ETA** | `milestone-status.md` notes | Original milestone plan risks | Recent log entries flagging risk |

## Procedure per section

### Done

1. **Determine the reporting period:**
   - If `--since <date>` argument provided → use that date
   - Else → look at last status update timestamp (search for `# Status Update —` headings in recent docs)
   - Fall back: 7 days ago
2. **Bash** — `git log --merges --since="<period start>" --pretty=format:"%H|%s|%cd"` — find merged PRs
3. **Read** `project/.claude/log.md` — entries within the period marked as completed feature / milestone
4. **Read** `project/.claude/milestone-status.md` — milestones marked DONE within the period
5. **Aggregate** — by feature / milestone, not per commit (per `changelog-conventions/reference/commit-mapping.md`)
6. **Filter** — drop refactors, chores, docs unless explicitly asked
7. **Format** — outcomes only, links to PR or milestone

### In progress

1. **Read** `project/.claude/milestone-status.md` — active milestone, task list, completed vs open
2. Format the active milestone as a single bullet with progress ratio: `M3 — User Authentication (3/6 tasks)`
3. **Bash** — `git log --since="<period start>" --no-merges --pretty=format:"%H|%s|%an"` — un-merged commits = in-progress branches
4. Group commits by branch (via `git branch --contains <hash>` if needed) and report active branches
5. Each in-progress item: what + progress + owner (from commit author)

### Blockers

1. **Grep** `project/.claude/log.md` for entries with markers: `BLOCKED:`, `BLOCKER:`, `waiting on`, `blocked on`
2. For each, extract: what's blocked, who/what is blocking, date first marked
3. Compute "since when" = days between blocker first appearance and report period end
4. If > 14 days → flag as **stale**
5. If no blockers found → output `None`

### ETA — milestone completion

1. **Read** `milestone-status.md` — task count, completed count
2. **Compute velocity:**
   - Look at `log.md` for completed-task entries in the last 7 days
   - velocity = tasks completed / 7 days
3. **Estimate completion date:**
   - days remaining = (total tasks − completed tasks) / velocity
   - ETA = today + days remaining
4. If velocity is 0 (no tasks completed in last 7 days) → "tracking" if no blockers, or "delayed" if blocked
5. Format as ISO date or "tracking"

### ETA — next milestone

1. **Read** `MILESTONES.md` (or `milestone-plan.md`) — next milestone's estimated task count
2. ETA next milestone start = ETA active milestone completion
3. ETA next milestone end = start + (next-milestone tasks / current velocity)
4. Often it's enough to write "after current"

### ETA — risks

1. **Read** active milestone's risks from milestone plan
2. **Grep** `log.md` for recent entries with `risk:`, `concern:`, `dependency:`
3. List as bullets, or "none"

## Period detection rules

If no `--since` arg:

1. Search workspace for files matching `STATUS-*.md` or `status-update-*.md`
2. Read the most recent one's `**Period:**` line — use the end date as new start
3. If no prior status, use 7 days ago
4. Always print the resolved period at the top so the reader knows

## Anti-patterns when sourcing

| Anti-pattern | Why wrong | Fix |
|---|---|---|
| Using only `git log` | Misses blocked-but-no-commit work | Read log.md too |
| Using only `milestone-status.md` | Misses unplanned fixes / scope additions | Read git log too |
| Including refactor commits in Done | Not user-visible | Filter as in `changelog-conventions/reference/commit-mapping.md` |
| Treating "code merged" as Done | User doesn't have it yet | Done = deployed/usable, not just merged (note: project's release rhythm may shift this) |
| Inventing blockers | Stakeholders trust the report | Only report what `log.md` or user explicitly said |
| Computing ETA from a single day's velocity | Too noisy | Use 7-day average |
