# Phase Naming Patterns

Common phase structures by project type. `bnac-phase-planner` uses these as starting points but adjusts to project specifics.

## Phase ID convention

- Number, in folder form `phase-<N>` and heading form `Phase <N>`: phase-1, phase-2, phase-3, ...
- Always start at `phase-1`.
- Don't skip numbers — phase-1, phase-3 (no phase-2) is forbidden.
- Don't recycle numbers across re-plans — once `phase-2` exists, even after deletion the next new phase becomes the next free number.

## Common phase patterns

### Pattern 1: New product (greenfield)

| Phase | Title | Typical exit criterion |
|---|---|---|
| phase-1 | Foundation | Buildable scaffold, CI green, hello-world deployed |
| phase-2 | Core domain | Entities + business rules + happy-path UCs |
| phase-3 | API / UI surface | All UCs from PRD Section 04 reachable from UI / API |
| phase-4 | Hardening | Auth, error handling, observability, security review |
| phase-5 | Launch readiness | Performance targets met, docs published, runbook complete |

### Pattern 2: Migration (legacy → new system)

| Phase | Title | Typical exit criterion |
|---|---|---|
| phase-1 | Foundation | New system scaffold + dual-write capability to legacy |
| phase-2 | Read parity | Reads from new system match legacy for all queries |
| phase-3 | Write cutover | Writes go to new system; legacy is now the read fallback |
| phase-4 | Decommission | Legacy reads removed; new system is sole source of truth |

### Pattern 3: Platform / library

| Phase | Title | Typical exit criterion |
|---|---|---|
| phase-1 | API design | Public surface reviewed and frozen for v1 |
| phase-2 | Implementation | All public methods backed by tests + docs |
| phase-3 | Adoption | Reference consumer integrated and shipping |
| phase-4 | Polish | DX feedback addressed, examples + tutorials published |

### Pattern 4: Internal tool

| Phase | Title | Typical exit criterion |
|---|---|---|
| phase-1 | MVP | Single-user happy path working locally |
| phase-2 | Multi-user | Auth, sharing, data isolation |
| phase-3 | Production | Deployed with backups, monitoring, alert routing |

### Pattern 5: BNAC-style platform (the meta case)

| Phase | Title | Typical exit criterion |
|---|---|---|
| phase-1 | Foundation | Package scaffold + CLI entry point |
| phase-2 | Vertical | First profile installable end-to-end |
| phase-3 | Pipeline | Domain-specific workflow (e.g., PRD → project) working |
| phase-4 | Robust | Cross-platform, error recovery, doctor |
| phase-5 | Scale | Additional profiles / harnesses |
| phase-6 | Enterprise | Adoption, RBAC, governance |
| phase-7 | Advanced | Observability, integrations, DX |

## Choosing a pattern

| Question | Answer | Pattern |
|---|---|---|
| Is there an existing system being replaced? | Yes | Migration (Pattern 2) |
| Is the deliverable consumed by other code? | Yes | Platform / library (Pattern 3) |
| Is the deliverable a UI for end-users? | Yes (external) | New product (Pattern 1) |
| Is the deliverable a UI for end-users? | Yes (internal) | Internal tool (Pattern 4) |
| Is it a developer platform / framework? | Yes | BNAC-style (Pattern 5) |

## Customizing

Patterns are starting points. Adjust phase titles to project vocabulary:
- "Foundation" → "Setup" / "Bootstrap" / "Scaffold"
- "Hardening" → "Production-ready" / "Battle-tested"
- "Launch readiness" → "GA" / "Release prep" / "Ship gate"

Keep the *exit criterion shape* (single testable condition) regardless of name.

## Anti-patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| Phase named after a date or sprint | Couples phase to time, not outcome | Name by deliverable |
| Phase named after a person ("Alice's phase") | Coupled to one contributor | Name by deliverable |
| Phase named with a letter ID (`A`, `B`) | Old convention; not canonical | Use `phase-1`, `phase-2`, … |
| Five phases all named "Iteration" | Indicates no real phase boundaries | Either remove phases entirely (medium project) or name each by deliverable |
