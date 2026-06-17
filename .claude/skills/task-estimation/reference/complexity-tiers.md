# Complexity Tiers — S / M / L

`bnac-task-planner` assigns each task a complexity tier. The tier is for *relative sizing*, not exact effort — that's intentional.

## Tier definitions

| Tier | Time band | Description |
|---|---|---|
| **S** | < 4 hours | Well-understood pattern, no unknowns, mechanical |
| **M** | 4 hours – 2 days | Some unknowns, requires understanding nearby code |
| **L** | > 2 days | Significant unknowns, research, or first-time-in-this-codebase work |

> Time bands are sanity checks, not commitments. Use the *signals* below to assign tier.

## Signals per tier

### S signals (any 2 of these → S)

- Following an existing pattern in this codebase (e.g., adding the 9th CRUD endpoint of the same shape)
- Single file or tightly clustered files (one component, one migration)
- No external dependencies needed
- Type signatures and behavior already defined elsewhere
- "Mechanical" — copy-paste-adjust

### M signals (any 2 of these → M)

- New pattern not yet in this codebase, but standard for the stack
- Spans 3–6 files in different layers (e.g., model + controller + test)
- Touches both code and config
- Requires reading 1–3 unfamiliar files before writing
- Some judgment calls about types, error handling, edge cases

### L signals (any 1 of these → L)

- New external dependency (library, service, infra component)
- Crosses tech-stack boundaries (e.g., affects both React and .NET)
- Requires research / spike before knowing what to build
- Touches > 6 files or > 1 module
- Has explicit "TBD" parts that need decision before implementation
- First time the team is doing this kind of work
- Migration / data transformation with rollback considerations
- Performance-sensitive code where the approach is non-obvious

## Decision procedure

1. Read the task title + files
2. Check L signals first — any single L signal → L. Stop.
3. Check M signals — 2+ M signals → M. Stop.
4. Default to S
5. Sanity-check against time band — if you'd estimate > 2 days, bump up regardless of signal count

## Worked examples

### Example 1: S
**Task:** Add `GET /api/users/:id` endpoint following the existing pattern in `users.controller.ts`.
**Files:** `src/api/users.controller.ts` (modify), `tests/users.test.ts` (modify)
**Signals:** existing pattern + 2 files + no new deps → 3 S signals → **S**

### Example 2: M
**Task:** Implement JWT-based session refresh.
**Files:** `src/utils/jwt.ts` (create), `src/api/auth.controller.ts` (modify), `src/middleware/auth.ts` (create), `tests/auth.test.ts` (modify)
**Signals:** new pattern (refresh logic) + 4 files across layers + judgment on TTL/storage → 3 M signals → **M**

### Example 3: L
**Task:** Migrate user table from int IDs to UUIDs.
**Files:** migration scripts, every model referencing user_id, tests
**Signals:** migration with rollback consideration + > 6 files + first time doing this in this codebase → multiple L signals → **L**

### Example 4: edge case
**Task:** Add real-time notification system using WebSockets.
**Signals:** new external dependency (ws library) + new pattern + cross-layer + judgment calls → 1 L + 3 M signals → **L** (any L signal wins)

## Sanity checks at the milestone level

After assigning all tasks, sanity-check the mix against the milestone's complexity:

| Milestone feel | Expected mix | Watch out for |
|---|---|---|
| Small milestone | Mostly S, some M | All-L list signals milestone is too ambitious |
| Medium milestone | Even split S/M/L | All-S list usually means tasks are too coarse |
| Large milestone | Mostly M and L | All-S list almost certainly wrong; re-evaluate |

If the mix doesn't match the feel, adjust the task list — split L tasks into smaller pieces, or merge S tasks if you find yourself with many trivial ones in sequence.

## Common mistakes

| Mistake | Fix |
|---|---|
| Calling "anything I haven't done before" L | Use signals; first-time-for-the-developer is not first-time-in-the-codebase |
| Calling "anything that touches > 1 file" M | Files alone don't make M; pattern novelty does |
| Using XL or XXL | Tiers are S/M/L only. If something feels XL, it's a milestone, not a task |
| Tier-shopping ("I want it to be S so it gets done fast") | Tier reflects reality; gaming it loses planning value |
