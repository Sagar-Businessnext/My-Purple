# Memory Types Reference

The four BNAC memory types. Each has a distinct trigger, lifetime, and body shape. Memory is project-scoped — these all live under `project/.claude/memory/`.

## Type 1: `user`

**Purpose:** Build a stable picture of who the user is, so future sessions can tailor tone, depth, and analogies.

**When to save:**
- User states their role, experience, or expertise (`I'm a senior backend dev`, `this is my first React project`)
- User states a preference about how they want to collaborate (`I prefer terse responses`, `walk me through it step by step`)
- User states what they're responsible for or working toward in a long-running sense

**When NOT to save:**
- One-off mood ("tired today")
- Anything that judges the user negatively
- Anything derivable from their role on the team (look it up, don't store it)

**Body shape:** Free-form prose. Lead with the most identity-defining fact.

### Examples

```markdown
---
name: user_role
description: senior backend engineer, deep Go expertise, new to React and this project's frontend
metadata:
  type: user
---

Senior backend engineer with ten years in Go. This is his first time touching the React side of this repo. Frame frontend explanations in terms of backend analogues (components → handlers, hooks → middleware) and don't assume familiarity with React idioms like Suspense, render props, or hooks lifecycle.
```

```markdown
---
name: user_response-style
description: prefers terse responses; no trailing summaries; reads diffs directly
metadata:
  type: user
---

Prefers terse, dense responses. Skip the "I'll now do X" preamble and the "here's what I changed" summary at the end — the diff communicates that. Use bullet points and tables, not paragraphs, when listing things.
```

## Type 2: `feedback`

**Purpose:** Capture guidance the user has given about how to approach work — both corrections AND confirmations. Record from failures AND successes. If you only save corrections, you drift away from approaches the user has already validated.

**When to save:**
- User corrects your approach (`no not that`, `stop doing X`, `don't`)
- User confirms a non-obvious approach worked (`yes exactly`, `keep doing that`, accepting an unusual choice without pushback)
- Especially: surprising or counterintuitive guidance — the kind that wouldn't be in the codebase

**When NOT to save:**
- First-time discussion or debate (no decision made yet)
- Generic advice that's already in CLAUDE.md or a rule

**Body shape (REQUIRED):**
1. The rule/fact (one or two sentences)
2. `**Why:** <reason — past incident, strong preference, constraint>`
3. `**How to apply:** <scope — where / when this guidance kicks in>`

The *why* is what lets future sessions judge edge cases instead of blindly following the rule.

### Examples

```markdown
---
name: feedback_no-mock-db
description: integration tests must hit a real database, not mocks
metadata:
  type: feedback
---

Integration tests must hit a real database (testcontainers or a real local instance), not mocks.

**Why:** prior incident in Q3 2025 — mock-based tests passed but a prod migration failed because the mock's behavior diverged from real PostgreSQL's lock semantics. Mocked DB tests give false confidence.

**How to apply:** any test under `tests/integration/`. Never use `jest.mock` or test doubles for the `db` module in that folder. Unit tests under `tests/unit/` are fine to mock.
```

```markdown
---
name: feedback_single-bundled-pr-for-refactors
description: refactors in this area prefer a single bundled PR over many small ones (confirmed pattern)
metadata:
  type: feedback
---

For refactors that span a single logical area (auth, billing, etc.), ship one bundled PR rather than splitting into a series of smaller PRs.

**Why:** validated 2026-04-10 — splitting an auth refactor into 8 PRs caused review fatigue and a merge ordering bug. User explicitly confirmed: "the single bundled PR was the right call here, splitting this one would've just been churn."

**How to apply:** when changes are tightly coupled (same module, same feature). For changes that span multiple unrelated areas, still split. Threshold: if reviewers would need to see PR_N to understand PR_N+1, bundle them.
```

## Type 3: `project`

**Purpose:** Information about ongoing work that is NOT derivable from code or git — deadlines, who's doing what, stakeholder context, motivation behind decisions.

**When to save:**
- User explains who is doing what, why, or by when
- User explains stakeholder context (legal flagged it, customer X needs Y)
- User explains *why* a piece of work is happening (the motivation, not the implementation)

**When NOT to save:**
- Anything in CLAUDE.md (architecture, structure, tech stack)
- Anything in git log (recent changes, who-changed-what)
- Anything in milestone-status.md (current task state)

**Body shape (REQUIRED):** Same Why + How structure as `feedback`.

### Examples

```markdown
---
name: project_compliance-deadline
description: auth middleware rewrite is driven by legal/compliance — deadline 2026-06-15
metadata:
  type: project
---

The auth middleware rewrite is driven by legal/compliance requirements around session token storage. It is NOT a tech-debt cleanup.

**Why:** legal flagged the current implementation in 2026-04 for failing new compliance requirements; deadline to ship the fix is 2026-06-15.

**How to apply:** any scope decision during the rewrite should favor compliance correctness over developer ergonomics. If a refactor is "nice to have" but slows compliance work, defer it.
```

```markdown
---
name: project_merge-freeze-mobile
description: merge freeze begins 2026-03-05 for mobile release cut
metadata:
  type: project
---

Merge freeze begins 2026-03-05 because the mobile team is cutting a release branch off main that morning.

**Why:** mobile team's release process tags from main; concurrent merges during cut break the tag.

**How to apply:** flag any non-critical PR work scheduled after 2026-03-05; recommend deferring to 2026-03-09 when the cut is complete.
```

## Type 4: `reference`

**Purpose:** Pointers to where information lives in external systems. These memories don't *contain* the information — they tell the next session where to look.

**When to save:**
- User mentions an external system + its purpose (Linear project X tracks bugs Y, Grafana dashboard Z is what oncall watches)
- User says "the source of truth for X is in Y"
- User shares a permanent URL that will keep being relevant

**When NOT to save:**
- Random one-off URLs without context
- Anything that's already inside the repo (link to the file instead)

**Body shape:** Free-form prose. Lead with the system + its purpose. Include enough context that a future session knows when this pointer is relevant.

### Examples

```markdown
---
name: reference_pipeline-bugs
description: pipeline bugs are tracked in Linear project INGEST
metadata:
  type: reference
---

Pipeline bugs (anything in `services/pipeline/`) are tracked in the Linear project **INGEST**. Read tickets there for context on pipeline regressions, ownership, and historical fixes. Linear is the source of truth — the GitHub issues for the pipeline repo are unused.
```

```markdown
---
name: reference_api-latency-dashboard
description: grafana.internal/d/api-latency is the oncall latency dashboard
metadata:
  type: reference
---

`grafana.internal/d/api-latency` is the dashboard oncall watches. If you're touching anything in the request handling path (`api/handlers/**`, middleware, rate-limiting), this is what will page someone if it regresses. Check it before/after touching that code.
```

## Common confusions

| Looks like | Actually is | Why |
|---|---|---|
| "We use Go 1.22" | NOT a memory (in CLAUDE.md or `go.mod`) | Derivable from code |
| "Last week we shipped feature X" | NOT a memory (in git log) | Derivable from git |
| "User is frustrated with build times" | NOT a memory (ephemeral mood) | Doesn't generalize |
| "User insists on tabs over spaces" | YES — `feedback` | Surprising preference, won't be in code if linter isn't set up |
| "Deadline 2026-06-15 for auth" | YES — `project` | Not in code, decays into a date |
| "Linear project INGEST is bugs" | YES — `reference` | External system, won't be findable from code |
| "User worked at Google before" | Probably NOT — irrelevant to work | Personal trivia |
| "User is a Go expert, new to React" | YES — `user` | Shapes how to frame explanations |
