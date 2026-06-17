Invoke the **bnac-memory-curator** agent to manage the typed long-term memory store at `project/.claude/memory/`. Add, list, forget, or search memory entries; or prune stale / duplicate / orphaned entries.

**Agent:** `bnac-memory-curator`
**Target:** `$ARGUMENTS` — `<action> [args]`
**Actions:** `add` · `list` · `forget` · `search`

## Action map

| Action | Arg shape | What it does |
|---|---|---|
| `add <type> "<content>"` | type ∈ {user, feedback, project, reference}; content quoted | Create a new typed memory file + index it in MEMORY.md |
| `list [type]` | type optional | Print MEMORY.md grouped by type (or just one type) |
| `list --prune-stale` | none | Run validation checklist; auto-fix safe issues; report items needing review |
| `forget <slug>` | slug = memory's `name:` field (with or without `<type>_` prefix) | Tombstone the file + remove its MEMORY.md line (destructive — asks for confirmation) |
| `search <query>` | free-text | Grep across memory bodies + descriptions; return ranked matches |

If `action` is omitted, default to `list`.

## What to do

1. Parse `<action>` from `$ARGUMENTS` (first positional). If absent → `list`.
2. Parse remaining args based on the action's shape.
3. **Verify** `project/.claude/memory/` exists. If not, tell the user to run `/bnac-init` and stop.
4. Delegate to the `bnac-memory-curator` agent with the resolved action + args.

### When action = `add`

1. Validate `<type>` is in the closed set (`user`, `feedback`, `project`, `reference`). Reject otherwise.
2. Validate `<content>` is quoted and non-empty.
3. For `feedback` and `project` types, scan `<content>` for the **Why:** and **How to apply:** markers. If missing, prompt the user to supply both before proceeding — these are required by [memory-conventions](../skills/memory-conventions/SKILL.md).
4. Pass control to `bnac-memory-curator` with `add` action.

### When action = `list`

1. Read `project/.claude/memory/MEMORY.md`.
2. If `[type]` is given, filter to that section; else print all sections.
3. Output the indented list (one line per entry).

### When action = `list --prune-stale`

1. Pass control to `bnac-memory-curator` with `prune-stale` action.
2. The curator runs the full validation checklist (orphans, broken index, slug mismatches, duplicates, invalid types, missing Why/How, relative dates, oversize descriptions, broken cross-links).
3. Auto-fix what's safe; report the rest for user review.

### When action = `forget`

1. Resolve `<slug>` — accept full (`feedback_no-mock-db`), bare (`no-mock-db`), or prefix (`no-mock`).
2. If 0 matches: report not-found.
3. If multiple matches: list candidates, ask for disambiguation, do not delete.
4. If 1 match: show the first 5 lines of the memory + ask the user to confirm.
5. On confirmation, the curator tombstones the file (writes a single comment marker) and removes the MEMORY.md line.
6. Emit a manual `rm` instruction so the user can fully delete the file when ready.

### When action = `search`

1. Pass `<query>` to the curator with `search` action.
2. Curator greps across memory bodies + MEMORY.md descriptions.
3. Output matches ranked: title match → description match → body match.

## Rules

- **Quoted content for `add`** — multi-word memory bodies MUST be quoted; otherwise `$ARGUMENTS` parsing breaks on spaces
- **Why + How for `feedback` and `project`** — refuse `add` if `<content>` doesn't include both markers; the curator will not silently invent them
- **`forget` is two-step** — show the memory + ask for explicit confirm before tombstoning
- **`list` is read-only** — never mutates files
- **`prune-stale` auto-fixes only safe ops** — filename casing, orphan re-indexing, broken-line removal. Merges, type changes, and date conversions are user-review only.
- **All actions log** to `project/.claude/log.md` per `~/.claude/rules/activity-logging.md`

## Examples

```
/bnac-memory                                              → defaults to list (all types)
/bnac-memory list                                         → list all memories grouped by type
/bnac-memory list feedback                                → list only feedback memories
/bnac-memory list --prune-stale                           → validate + auto-fix + report

/bnac-memory add user "Senior backend dev, deep Go, new to React"
/bnac-memory add feedback "No mock DB in integration tests. **Why:** prior incident. **How to apply:** tests/integration/**"
/bnac-memory add project "Auth rewrite due 2026-06-15. **Why:** legal compliance. **How to apply:** scope favors compliance"
/bnac-memory add reference "Pipeline bugs tracked in Linear project INGEST"

/bnac-memory search mock                                  → matches across bodies + descriptions
/bnac-memory search "linear"                              → matches reference_pipeline-bugs

/bnac-memory forget no-mock-db                            → tombstone the feedback memory (with confirm)
/bnac-memory forget feedback_no-mock-db                   → same, full slug
```

## When to use vs. when not to

| Use `/bnac-memory add` | Don't — use somewhere else |
|---|---|
| User states a durable preference / role | Code style → in linter / CLAUDE.md |
| User corrects approach (`stop doing X`) | One-off opinion still being debated |
| Stakeholder / deadline / motivation | Architecture / tech stack → CLAUDE.md / SUMMARY.md |
| External system pointer + purpose | Random URL drop without context |

If unsure, ask: "What was *surprising* or *non-obvious* about that?" — the answer is what's worth saving.

## Distinct from `/bnac-context`

This command manages **typed facts that survive sessions** (`project/.claude/memory/`).
`/bnac-context` manages **work-product compact history** (`project/.claude/context/carry-forward.md`).
They are separate stores with different writers, lifetimes, and contracts. See [memory-management rule](../rules/memory-management.md) for the boundary.
