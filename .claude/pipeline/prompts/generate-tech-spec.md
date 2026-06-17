# Generate Technical Specification

> **Pipeline Step:** 2 (after validation)
> **Input:** Validated PRD (22 sections), especially Section 13 (App Type) and Section 22 (Code Generation Context)
> **Output:** `project-context/project-structure.md`, `project-context/project-tech-stack.md`

---

## Purpose

Generate production-ready technical context by:
1. Reading Section 13 to resolve the application language and service type
2. Extracting all entities, processes, integrations from the PRD
3. Generating a complete project folder structure with real names (no placeholders)
4. Generating a condensed tech stack with package versions

---

## Workflow

### Step 1: Read PRD Sections

Read these sections from the validated PRD:
- **Section 01** — Product name, compliance requirements
- **Section 06** — Use cases (UC-XXX) → derive controllers, services, handlers
- **Section 07** — Business rules (BR-XXX) → derive validators, calculators
- **Section 08** — Data entities → derive models, schemas, migrations
- **Section 05** — Integrations → derive API clients, adapters
- **Section 04** — Process flows → derive workflow orchestrators
- **Section 09** — NFRs → derive middleware (caching, rate limiting, logging)
- **Section 13** — Application language + service type (PRIMARY)

### Step 2: Resolve Stack

From Section 13, determine:
- **Language:** Python / DotNet / React / Flutter
- **Service Type:** REST API / gRPC / Microservices / Worker / ML-AI / Web App / Mobile App

Use the matching stack profile shipped with this package as the skeleton source:
- `src/stacks/python/` — Python conventions, patterns, structure
- `src/stacks/dotnet/` — .NET conventions, patterns, structure
- `src/stacks/react-ts/` — React + TS conventions, BNDS pattern, structure
- `src/stacks/flutter/` — Flutter conventions, widgets, structure

Pull tech-stack and folder conventions from each stack's `skills/<stack>-project-structure/` and `skills/<stack>-patterns/` reference files. If the project's service type isn't covered → generate structure from the closest stack convention.

### Step 3: Generate Project Structure

Create `project-context/project-structure.md` containing:

```markdown
# Project Structure — [Product Name]

## Stack
- Language: [resolved]
- Service Type: [resolved]
- Architecture: [Clean Architecture / Hexagonal / etc.]

## Folder Structure

[Complete tree with ALL placeholders replaced]
- Entity names from Section 08 → model files
- Use case names from Section 06 → handler/controller files
- Integration names from Section 05 → client/adapter files
- Business rule names from Section 07 → validator files

## File Count
- Total files: [exact count]
- Total folders: [exact count]
```

### Step 4: Generate Tech Stack

Create `project-context/project-tech-stack.md` containing:

```markdown
# Tech Stack — [Product Name]

## Runtime
- Language: [version]
- Framework: [version]

## Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| [package] | [version] | [why needed] |

## Dev Dependencies
| Package | Version | Purpose |
|---------|---------|---------|

## Infrastructure
| Service | Purpose |
|---------|---------|
| [database] | [Primary storage] |
| [cache] | [Session/caching] |
| [queue] | [Async processing] |
```

---

## Entity-to-File Mapping

For each entity in Section 08, generate:

| PRD Element | Generated Files |
|-------------|----------------|
| Entity `User` | `models/user.ts`, `schemas/user.schema.ts`, `migrations/create-user.ts` |
| UC-001 `Login` | `controllers/auth.controller.ts`, `services/auth.service.ts` |
| BR-001 `Password Policy` | `validators/password.validator.ts` |
| Integration `Payment Gateway` | `clients/payment-gateway.client.ts` |

---

## Success Criteria

- All entities from Section 08 appear as model files
- All use cases from Section 06 appear as controller/handler files
- All integrations from Section 05 appear as client files
- No placeholder names remain (`{entity}`, `{process}`, `[TBD]`)
- Tech stack versions are specific (not "latest")
- File count is calculated and documented
