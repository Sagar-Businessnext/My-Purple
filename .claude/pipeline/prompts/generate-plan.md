# Generate Implementation Plan

> **Pipeline Step:** 4 (after skills generation)
> **Input:** Validated PRD, `project-context/project-structure.md`, `project-context/project-tech-stack.md`, generated skills
> **Output:** `project-context/implementation-plan.md`, `project/.claude/milestone-status.md`

---

## Purpose

Generate a comprehensive implementation plan that:
1. Breaks the project into milestones with specific file counts and task descriptions
2. Defines agent assignments per task (`bnac-developer`, `bnac-reviewer`, `bnac-quality-gate`)
3. Establishes quality gates and review checkpoints
4. Provides exact file paths in task descriptions
5. Estimates total project file count

---

## Workflow

### Step 1: Read All Context

Read these files:
- PRD sections (all 22)
- `project-context/project-structure.md` — file tree and architecture
- `project-context/project-tech-stack.md` — dependencies and infrastructure
- `project/.claude/skills/` — available project-specific skills
- `pipeline/validation/VALIDATION_REPORT.md` — PRD quality context

### Step 2: Identify Work Streams

Extract from PRD:
- **Data layer:** Entities from Section 08 → models, schemas, migrations
- **Business logic:** Business rules from Section 07 → validators, services
- **API/UI layer:** Use cases from Section 06 → controllers, pages, handlers
- **Integrations:** From Section 05 → API clients, adapters, webhooks
- **Security:** From Section 10 → auth, encryption, audit logging
- **Infrastructure:** From Section 09 NFRs → caching, monitoring, scaling

### Step 3: Generate Milestones

Create milestones following this standard pattern:

```markdown
### M[N]: [Milestone Title]

**Goal:** [One sentence — what's done when this milestone is complete]
**Files:** [Exact count of files created/modified]
**Agent:** [Primary agent: `bnac-developer` / `react-developer` / etc.]
**Skills:** [Skills used from project/.claude/skills/]

| # | Task | Files | Agent | Output |
|---|------|-------|-------|--------|
| N.1 | [Specific task with file paths] | [count] | [agent] | [deliverable] |
| N.2 | ... | ... | ... | ... |

**Quality Gate:**
- [ ] Build passes
- [ ] Type check passes
- [ ] Lint passes
- [ ] Tests pass (coverage >= target)

**Exit Criteria:** [What must be true for this milestone to be complete]
```

### Step 4: Milestone Ordering

Follow this standard phase structure:

| Phase | Milestones | Content |
|-------|-----------|---------|
| **Foundation** | M1-M2 | Project scaffold, database schema, base configuration |
| **Domain** | M3-M5 | Entity models, business rules, core services |
| **API/UI** | M6-M8 | Controllers/pages, routes, request/response handling |
| **Integration** | M9-M10 | External API clients, webhooks, event handlers |
| **Security** | M11 | Authentication, authorization, audit logging |
| **Quality** | M12 | Full test coverage, performance optimization |
| **Deploy** | M13 | CI/CD, deployment config, monitoring |

Adjust the number of milestones based on project complexity:
- Small project (3-5 entities, <10 UCs): 5-7 milestones
- Medium project (5-15 entities, 10-30 UCs): 8-13 milestones
- Large project (15+ entities, 30+ UCs): 13-20 milestones

### Step 5: Task Detail Requirements

Each task MUST include:
- **Exact file paths** — `src/models/user.model.ts`, not "create user model"
- **File count** — how many files this task creates or modifies
- **Agent assignment** — which agent executes this task
- **Dependencies** — which tasks must complete first (if any)

### Step 6: Generate Output Files

**File 1: `project-context/implementation-plan.md`**

```markdown
# Implementation Plan — [Product Name]

> **Generated:** [date]
> **Milestones:** [count]
> **Total Tasks:** [count]
> **Total Files:** [count]
> **Estimated Agent Workflow:** planner → `bnac-developer` → `bnac-reviewer` → `bnac-quality-gate`

---

## Summary

| Phase | Milestones | Tasks | Files |
|-------|-----------|-------|-------|
| Foundation | M1-M2 | [n] | [n] |
| Domain | M3-M5 | [n] | [n] |
| ... | ... | ... | ... |

---

[Full milestone details as per Step 3 format]
```

**File 2: Update `project/.claude/milestone-status.md`**

Set M1 as the active milestone with its task list.

---

## Agent Workflow Per Milestone

```
bnac-task-planner → bnac-developer → bnac-reviewer → bnac-quality-gate
   (feature lens)        code             review            verify
```

1. **bnac-task-planner** (invoked via `/bnac-task-plan --lens feature`) reviews the milestone tasks and refines the plan
2. **bnac-developer** implements each task, following project skills
3. **bnac-reviewer** reviews code after each milestone
4. **bnac-quality-gate** runs build/type/lint/test verification

---

## Success Criteria

- Every entity from Section 08 is assigned to a task
- Every use case from Section 06 maps to at least one task
- Every integration from Section 05 has implementation tasks
- File paths are specific (no placeholders)
- Total file count matches project structure
- Each milestone has a quality gate
- Task dependencies form a valid DAG (no cycles)
