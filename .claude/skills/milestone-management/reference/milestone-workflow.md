# Milestone Workflow Reference

## Complete Lifecycle

### 1. Planning Phase

Break project scope into milestones using these principles:

**Chunking rules:**
- Each milestone = one coherent deliverable (e.g., "Auth system", "Dashboard UI", "API endpoints")
- 3–7 tasks per milestone (5 is ideal)
- Tasks should be completable in 1–3 coding sessions
- Each task has a concrete, verifiable output (file created, function working, test passing)

**Task writing guidelines:**
- Bad: "Work on authentication" (vague, no clear done state)
- Good: "Create `auth/login.ts` with JWT token exchange and refresh" (specific output)
- Bad: "Improve performance" (unmeasurable)
- Good: "Add Redis caching to `/api/users` endpoint, verify <100ms response" (measurable)

**Dependency ordering:**
- Foundation first: types/interfaces → logic → UI → tests
- Infrastructure first: config → services → controllers → routes
- Data first: models → repositories → services → API

### 2. Start Phase

When `/bnac-milestone start M<N>` is invoked:

```markdown
# milestone-status.md changes:

## Before
| M3 | User Dashboard | 0/5 | UPCOMING |

## After  
| M3 | User Dashboard | 0/5 | <- ACTIVE |

## Active Milestone Detail
### M3 — User Dashboard
- [ ] Create DashboardPage with 8-file pattern
- [ ] Implement stats API integration in hooks
- [ ] Create StatsCard component
- [ ] Create RecentActivity component  
- [ ] Add loading/error/empty states
```

### 3. Execution Phase

During milestone work:

```markdown
# As developer completes tasks, check them off:

### M3 — User Dashboard
- [x] Create DashboardPage with 8-file pattern
- [x] Implement stats API integration in hooks
- [x] Create StatsCard component
- [ ] Create RecentActivity component  ← CURRENT
- [ ] Add loading/error/empty states

# Update progress table:
| M3 | User Dashboard | 3/5 | <- ACTIVE |
```

**Auto-update rules for bnac-developer agent:**
- After creating a file that matches a task → check it off
- After fixing a build error for a task → check it off
- After each task completion → update progress count
- Log each completion to `log.md`

### 4. Completion Phase

When `/bnac-milestone complete` is invoked:

**Pre-checks:**
1. All tasks must be `[x]` — if not, list remaining and abort
2. Recommend quality gate — `build ✓ | types ✓ | lint ✓ | tests ✓`

**Actions:**
1. Move active milestone detail to "Completed Milestones" section
2. Update progress table row to `DONE`
3. Record quality gate results in Quality Gate History table
4. Set next milestone as `<- ACTIVE`
5. Log completion

```markdown
# After completion:

## Progress
| M3 | User Dashboard | 5/5 | DONE |
| M4 | API Integration | 0/4 | <- ACTIVE |

## Completed Milestones
### M3 — User Dashboard (completed 2026-04-16)
- [x] Create DashboardPage with 8-file pattern
- [x] Implement stats API integration in hooks
- [x] Create StatsCard component
- [x] Create RecentActivity component
- [x] Add loading/error/empty states

## Quality Gate History
| M3 | ✅ | ✅ | ✅ | ✅ | PASS |
```

### 5. Transition Phase

After completion, the next milestone becomes active. The bnac-developer agent will:
1. Read the updated `milestone-status.md`
2. See the new active milestone and its tasks
3. Begin working on the first unchecked task
4. The cycle repeats

## Token Efficiency

Completed milestone details are archived in `milestone-status.md` under the Completed section. This means:
- Only the active milestone's tasks are "hot" context
- Completed milestones provide historical reference without polluting working context
- If `milestone-status.md` grows too large (>200 lines of completed milestones), older completed entries can be moved to `project/.claude/completed/milestone-archive.md`

## Edge Cases

| Scenario | Action |
|----------|--------|
| Task needs to be added mid-milestone | Add it to the checklist, update total count |
| Task turns out unnecessary | Remove it, update total count, log why |
| Milestone is blocked | Add blocker to "Blockers" section, log it, continue what's possible |
| User wants to skip a milestone | Warn, get confirmation, mark as SKIPPED (not DONE) |
| User wants to reopen completed milestone | Move it back from Completed, mark as ACTIVE |
