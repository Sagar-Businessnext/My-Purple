# Generate Project-Specific Skills

> **Pipeline Step:** 3 (after tech spec generation)
> **Input:** Validated PRD, `project-context/project-structure.md`, `project-context/project-tech-stack.md`
> **Output:** Project-specific skills in `project/.claude/skills/`

---

## Purpose

Generate skills tailored to this specific project by analyzing:
1. PRD use cases, business rules, and integrations → domain-specific skills
2. Project structure and architecture → pattern-specific skills
3. Tech stack and frameworks → technology-specific skills

Skills are generated ON-DEMAND based on actual project requirements, not from generic templates.

---

## Workflow

### Phase 1: Copy Generic Stack Skills

1. Read the resolved language from `project-context/project-tech-stack.md`
2. Check if generic skills exist at `stacks/{language}/skills/`
3. If they exist → copy them to `project/.claude/skills/`
4. Track which skill names were copied (to avoid duplicates in Phase 2)

### Phase 2: Analyze Project Context

Read and extract:

**From PRD:**
- Use cases (UC-XXX) → identify complex workflows that need skill guidance
- Business rules (BR-XXX) → identify validation/calculation patterns
- Integrations → identify external API patterns
- Data entities → identify CRUD and relationship patterns

**From Project Structure:**
- Architecture pattern (Clean Architecture, Hexagonal, etc.)
- Layer organization (API → Domain → Infrastructure)
- Testing structure

**From Tech Stack:**
- Framework-specific patterns (e.g., FastAPI dependency injection, .NET CQRS)
- ORM patterns (e.g., SQLAlchemy, Entity Framework, Prisma)
- Third-party service patterns

### Phase 3: Generate Project-Specific Skills

For each identified pattern, generate a skill directory:

```
project/.claude/skills/{skill-name}/
├── SKILL.md          → Instructions for the agent
└── reference/
    └── {ref}.md      → Examples, templates, patterns
```

**Skill categories to consider:**

| Category | Example Skills | Trigger |
|----------|---------------|---------|
| Domain workflows | `process-payment/`, `user-onboarding/` | Complex UC with 10+ steps |
| Business logic | `apply-business-rules/`, `calculate-pricing/` | 5+ related BRs |
| Integration | `call-payment-api/`, `sync-crm-data/` | External system with 3+ endpoints |
| Data patterns | `manage-user-entity/`, `handle-relationships/` | Entity with 10+ attributes or complex relationships |
| Architecture | `clean-architecture-layer/`, `cqrs-command/` | Stack-specific patterns |
| Testing | `test-integration/`, `test-business-rules/` | Based on testing requirements (Section 15) |

### Phase 4: Generate Skill Content

Each `SKILL.md` must contain:

```markdown
# [Skill Name]

> **Purpose:** [One-line description]
> **When to use:** [Trigger conditions]

## Instructions

[Step-by-step procedure for the agent to follow]

## Rules

[Constraints and patterns to enforce]

## Examples

[Concrete code examples specific to this project]
```

Each `reference/*.md` must contain:
- Project-specific templates (with actual entity/service names)
- Code patterns that match the project's stack
- Anti-patterns to avoid

---

## Skill Naming Convention

- Lowercase kebab-case: `process-payment`, `manage-user-entity`
- Prefix with domain area when ambiguous: `auth-validate-token`, `payment-calculate-fees`
- Do NOT duplicate generic skill names already copied in Phase 1

---

## Success Criteria

- Every complex use case (10+ steps) has a corresponding skill
- Every external integration has a skill with endpoint references
- Every architectural pattern in the stack has a skill
- Skills reference actual project entities, services, and file paths
- No generic placeholder content — all skills are project-specific
- Skill count is logged
