---
paths:
  - "**/*"
---

# Context-First Execution Rule

Before executing ANY command, skill, or agent action, you MUST read context in this order:

1. **`~/.claude/CLAUDE.md`** — Platform rules, available tools, enterprise standards
2. **`project/.claude/CLAUDE.md`** — Project-specific overrides and conventions (if exists)
3. **`project/.claude/SUMMARY.md`** — What the project is, current state, tech stack (if exists)
4. **`project/.claude/milestone-status.md`** — Active milestone and task progress (if exists)
5. **`project/.claude/memory/MEMORY.md`** — Typed long-term memory index (if exists) — user role/preferences, feedback, project decisions, external references. Only open specific `memory/*.md` files when their `description:` is relevant to the task. See [memory-management.md](memory-management.md).
6. **`project/.claude/context/carry-forward.md`** — Compact history of completed phases/milestones (if exists). Auto-stitched by `bnac-context-compactor` from `*.summary.md` siblings of completed milestones. This is the cumulative-context layer — it's how Phase N sees what Phase N-1 produced without loading every detail file. See [context-carry-forward](../skills/context-carry-forward/SKILL.md).

## Completed-detail guard (CMM-D10)

By default, **do NOT read detail `.md` files of completed milestones or phases** — use their `*.summary.md` sibling (already loaded via step 6).

Exceptions where opt-up is allowed:
- **Debugging a regression** that traces back to an earlier milestone's code (reviewer especially)
- **Cross-milestone refactor** that touches files owned by a completed milestone
- **The user explicitly asks** about a specific completed milestone's full detail

If you opt up, **read the detail file directly** — don't try to reconstruct it from log.md or git. Re-summarization happens only on `/bnac-context refresh`, not implicitly.

The active milestone's detail is loaded normally via step 4 (`milestone-status.md`'s Active Milestone Detail section) — the guard applies only to *completed* milestones.

## Why This Matters

Every project has specific conventions, active work context, and constraints. Acting without reading context leads to:
- Wrong patterns applied (e.g., using EF Core when the project uses ADO.NET)
- Duplicated work (feature already implemented in a different branch)
- Broken conventions (naming, structure, import rules)
- Wasted milestone progress (working on the wrong task)

## When to Re-Read Context

- At the start of every new conversation/session
- Before starting a new task or command
- After switching between projects
- When something doesn't look right — context may have changed

## Two-Tier Resolution

If both global (`~/.claude/`) and project-local (`project/.claude/`) have the same file, **project-local wins**. This allows projects to override global defaults.

## Violation

Skipping context reading is a CRITICAL violation. If you realize you acted without context, stop, read context, and verify your actions were correct.
