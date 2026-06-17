# Feature Plan — Output Format

Used by `bnac-task-planner` when invoked via `/bnac-task-plan --lens feature`.

## Document shape

```markdown
## Feature Plan: <title>

### Goal
One sentence describing the end state — what users / the system can do when this is done.

### Input
- Source: <PRD path / "description provided">
- Scope: <files / directories affected>

### Prerequisites
- What must be true before starting (env vars, infra, prior milestone done)

### Tasks
| # | Task | Type | Files | Depends On | Complexity |
|---|------|------|-------|------------|------------|
| 1 | ... | create / modify | ... | — | S / M / L |
| 2 | ... | create / modify | ... | 1 | S / M / L |

### Architecture Decisions
- Decision 1: <what> — chose X over Y because <reason>
- Decision 2: <what> — chose A over B because <reason>

### Risks
- Risk 1: <concrete failure mode> → <mitigation>
- Risk 2: <concrete failure mode> → <mitigation>

### Out of Scope
- Things explicitly NOT included (and which feature/milestone picks them up, if any)
```

## Field rules

### Goal
- One sentence. Outcome-oriented.
- Bad: "Implement authentication"
- Good: "Users can sign in with email and password and receive a JWT valid for 24 hours"

### Tasks
- Use `task-estimation` skill for complexity tiers and file path discipline.
- Typical feature: 5–15 tasks. Outside this range = scope is wrong, re-shape.

### Architecture Decisions
- Only include non-obvious decisions. "Use TypeScript" is not a decision in a TS project.
- Include the alternative considered. "Chose Zod over Yup because we already depend on Zod elsewhere."

### Risks
- Each risk = a concrete failure mode + a mitigation.
- "Performance" alone is not a risk. State *what* is slow, *why*, and *how* to verify.

### Out of Scope
- Always populate. Empty out-of-scope = scope is implicit = scope creep.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Goal phrased as activity ("implement X") | Phrase as outcome ("users can X") |
| No architecture decisions section | If truly none, write "No non-obvious decisions" — don't omit |
| Risk = single word ("scalability") | Specify the concrete failure mode and mitigation |
| Tasks without explicit file paths | Add paths; refer to `task-estimation/reference/task-format.md` |
| Out-of-scope omitted | Always list — even "none" is an answer |
