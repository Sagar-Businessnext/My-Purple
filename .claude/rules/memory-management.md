---
paths:
  - "**/*"
---

# Memory Management Rule

BNAC projects maintain a **typed long-term memory store** at `project/.claude/memory/`. This memory survives across sessions and milestones; it carries forward what shouldn't be re-derived from code or git every time.

This is distinct from `project/.claude/context/carry-forward.md` (work-product *history* — what was built) and from `project/.claude/log.md` (action audit — what was done when). Memory is curated *facts* — user role, feedback, project decisions, external system pointers.

## When to read memory

Read `project/.claude/memory/MEMORY.md` (the index) on every new session as part of the [context-first.md](context-first.md) chain (step 5). If an entry's `description:` field looks relevant to the task, open the specific memory file.

Memory records can become stale. Use memory as context for what was true at a given point in time. Before acting on a recalled memory, verify it against current code or current resources. If it conflicts with reality, **update or remove the memory** — do not act on the stale fact.

## When to write memory

Save a memory immediately when one of the four type-specific triggers fires:

| Type | Trigger |
|---|---|
| `user` | You learn a fact about the user's role, expertise, preferences, or responsibilities |
| `feedback` | The user corrects your approach (`stop doing X`, `don't`) OR confirms a non-obvious approach worked (`yes exactly`, validated judgment call) |
| `project` | You learn who is doing what, why, or by when — particularly when it's not derivable from code or git |
| `reference` | You learn that information lives in an external system (Linear, Slack, Grafana, Confluence) |

If the user explicitly says "remember X", save it as the type that fits best. If they say "forget X", find and remove the entry.

## What NOT to save

These belong in code, git, or `log.md` — not in memory:

- **Code patterns, conventions, architecture, file paths, project structure** — derive from current code
- **Git history, recent changes, who-changed-what** — `git log` / `git blame` are authoritative
- **Debugging solutions / fix recipes** — the fix is in the code; the commit has context
- **Anything documented in `CLAUDE.md`** — that's the project context tier, not memory
- **Ephemeral task state** — in-progress work belongs in the conversation / TodoWrite, not memory

These exclusions apply even when a user asks to save them. If asked, push back briefly: "What was *surprising* or *non-obvious* about that?" — the answer is what's worth keeping.

## Memory file format

Every memory file is one `.md` under `project/.claude/memory/`, named `<type>_<slug>.md` (e.g., `feedback_no-mock-db.md`, `user_role.md`).

```markdown
---
name: {short-kebab-case-slug}
description: {one-line summary — used to decide relevance in future sessions; be specific}
metadata:
  type: {user | feedback | project | reference}
---

{memory body}
```

For `feedback` and `project` types, the body MUST start with the rule/fact, then a **Why:** line (the reason — often a past incident or constraint) and a **How to apply:** line (when this guidance kicks in). The *why* is what lets you judge edge cases later instead of blindly following the rule.

Link to related memories with `[[slug]]`. A `[[slug]]` that doesn't yet match an existing memory is fine — it marks something worth writing later.

See [memory-conventions/SKILL.md](../skills/memory-conventions/SKILL.md) for the full body shape per type.

## MEMORY.md index

Every memory file MUST also be registered in `project/.claude/memory/MEMORY.md`. The index is one-line-per-entry, under ~150 chars per line, capped at 200 lines total (anything past 200 is dropped from the load window).

```markdown
# Memory Index

- [User role](user_role.md) — senior backend dev, deep Go, new to React
- [No mock DB](feedback_no-mock-db.md) — integration tests must hit real DB (prior incident)
- [Compliance deadline](project_compliance-deadline.md) — auth rewrite due 2026-06-15
- [Pipeline bugs in Linear](reference_pipeline-bugs.md) — INGEST project tracks pipeline bugs
```

The index has **no frontmatter**. Never write memory body content directly into `MEMORY.md` — it's a pointer list only.

## Rules

1. **Read MEMORY.md first** — every session opens with the index; only read specific files when their `description:` is relevant
2. **Save per trigger, not on every interaction** — corrections, confirmations, decisions. Not "interesting conversations".
3. **One file per memory** — never bundle multiple memories into a single file; one fact, one slug, one entry
4. **Always update both** — adding a memory means writing the file AND adding the MEMORY.md line
5. **Convert relative dates to absolute** — "Thursday" → "2026-03-05" so the memory remains interpretable
6. **Verify before acting** — recalled memory is a hint, not gospel; cross-check against current state
7. **No duplicates** — before writing, search MEMORY.md for an existing entry; update it instead of creating new
8. **Curator owns cleanup** — `/bnac-memory list --prune-stale` invokes `bnac-memory-curator` to detect stale / duplicate / orphaned entries

## If `memory/` doesn't exist

If `project/.claude/memory/` doesn't exist, do NOT auto-create it from inside an unrelated task. Instead, instruct the user to run `/bnac-init` (or `/bnac-init --no-local` is fine — just `/bnac-init` re-scaffolds the folder).

Existing projects that pre-date this rule will not have `memory/`. They will simply not have memory loaded — the rule's read step (context-first.md step 5) is conditional on existence.

## When the user says "ignore memory"

If the user explicitly says to *ignore* or *not use* memory for a task: do not apply remembered facts, do not cite, do not compare against, do not mention memory content. The memory still exists on disk — it's just suppressed for that turn.
