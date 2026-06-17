# PRD Template — 22-Section Functional Specification

> **Version:** 3.1
> **Usage:** Fill in all sections before running `bnac prd-validate`. Tier 1 sections must be complete for code generation to proceed.
> **Schema alignment:** Sections 17–22 close the 22-layer intake gap identified in the BN AI Dark Factory contract (see `dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md` §8).

---

## Priority Tiers

| Tier | Sections | Blocks |
|------|----------|--------|
| **Tier 1** | 01, 02, 06, 07, 08, 10, 13, 19, 22 | Code generation — incomplete = pipeline stops |
| **Tier 2** | 03, 04, 05, 09, 12, 15, 17, 18, 20, 21 | Quality gate — incomplete = quality checks fail |
| **Tier 3** | 11, 14, 16 | Completeness score — incomplete = warnings only |

---

## 02 Document Information

> **Purpose:** Identifies the product, its target users, platform, deployment model, compliance requirements, and supported languages. Used by the pipeline to select the correct stack and validation rules.

```yaml
document_info:
  product_name: ""              # Full product name (e.g., "BNAC Enterprise Portal")
  version: ""                   # PRD version (e.g., "1.0.0")
  date: ""                      # ISO date (e.g., "2026-04-16")
  status: ""                    # draft | review | approved
  authors:
    - name: ""
      role: ""
      email: ""
  target_users: ""              # Primary user group (e.g., "Loan Officers, Credit Analysts")
  platform: ""                  # web | mobile | desktop | api | hybrid
  deployment: ""                # cloud | on-premise | hybrid | saas
  compliance:
    - ""                        # e.g., GDPR, PCI-DSS, SOC2, HIPAA, ISO27001
  supported_languages:
    - ""                        # e.g., en-US, hi-IN, ar-SA
  related_documents:
    - title: ""
      path: ""
```

**Instructions:**
- `product_name` — Use the official product name as it will appear in deployments.
- `target_users` — List the primary roles/personas who will use the product.
- `compliance` — List all standards the product must comply with; this drives security and data handling rules.
- `supported_languages` — Use BCP 47 language tags.

**Validation checklist:**
- [ ] `product_name` is non-empty
- [ ] `platform` is one of: web, mobile, desktop, api, hybrid
- [ ] `deployment` is one of: cloud, on-premise, hybrid, saas
- [ ] At least one `compliance` standard listed (or `none` if not applicable)
- [ ] `status` is one of: draft, review, approved

**Related sections:** 13 (Architecture), 11 (Personas), 10 (Security)

---

## 02 Executive Summary

> **Purpose:** Captures the product vision, quantified business objectives, key capabilities, and success metrics. This is the single most-read section — it must be precise and complete.

```markdown
## Executive Summary

### Product Vision
<!-- REQUIRED: Minimum 50 words. Describe what this product is, who it serves, and the problem it solves. -->

### Business Objectives
<!-- REQUIRED: Minimum 3 objectives. Each must have a quantified target. -->
| # | Objective | Target | Timeframe |
|---|-----------|--------|-----------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### Key Capabilities
<!-- REQUIRED: Minimum 5 capabilities. Use plain language — no technical jargon. -->
1.
2.
3.
4.
5.

### Success Metrics
<!-- REQUIRED: Each metric must have a measurable target. -->
| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|--------------------|
| | | | |
| | | | |
| | | | |
```

**Instructions:**
- Vision must clearly state the core value proposition in 50+ words.
- Objectives must be SMART — Specific, Measurable, Achievable, Relevant, Time-bound.
- Capabilities are user-facing — write from the user's perspective, not the engineer's.
- Success metrics will be referenced in section 16 (KPIs).

**Validation checklist:**
- [ ] Vision is at least 50 words
- [ ] Minimum 3 business objectives with quantified targets
- [ ] Minimum 5 key capabilities listed
- [ ] At least 3 success metrics with targets and measurement methods

**Related sections:** 16 (KPIs), 11 (Personas), 04 (Process Flows)

---

## 03 Architecture Overview

> **Purpose:** Describes the high-level component structure of the product. The pipeline uses this to validate that implementation matches the intended architecture.

```markdown
## Architecture Overview

### Component Diagram
<!-- REQUIRED: ASCII diagram showing major components and their relationships. -->
<!-- Example:
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  Web Client │────▶│   API Layer  │────▶│ Business Logic │
└─────────────┘     └──────────────┘     └────────────────┘
                                                  │
                                         ┌────────▼───────┐
                                         │   Data Layer   │
                                         └────────────────┘
-->

### Component Descriptions
<!-- REQUIRED: Describe each component from the diagram. -->

#### [Component Name]
- **Responsibility:** What this component does
- **Technology:** What it is built with
- **Interfaces:** How it communicates with other components
- **Owned by:** Team or role responsible

#### [Component Name]
- **Responsibility:**
- **Technology:**
- **Interfaces:**
- **Owned by:**

### Architecture Decisions
<!-- Document key architectural decisions and their rationale. -->
| Decision | Option Chosen | Rationale | Rejected Alternatives |
|----------|--------------|-----------|----------------------|
| | | | |
```

**Instructions:**
- The ASCII diagram does not need to be pixel-perfect — it needs to show component boundaries and data flow.
- Every box in the diagram must have a corresponding Component Description entry.
- Architecture Decisions capture the "why" — future developers and the pipeline reviewer will use these.

**Validation checklist:**
- [ ] ASCII diagram is present and non-empty
- [ ] At least 3 components described
- [ ] Each component has Responsibility, Technology, and Interfaces fields filled
- [ ] At least 1 architecture decision documented

**Related sections:** 13 (Application Type), 05 (Integration Layer), 04 (Process Flows)

---

## 04 Process Flow Types

> **Purpose:** Documents the primary business workflows the product supports. Flows are used to generate user stories, test cases, and integration contracts.

```markdown
## Process Flow Types

<!-- REQUIRED: Minimum 3 business workflows. -->

### Flow 1: [Workflow Name]
- **Description:** What this workflow accomplishes
- **Trigger:** What starts this flow
- **Actor(s):** Who initiates or participates

**Steps:**
1. [Step description]
2. [Step description]
3. [Step description — include decision point if applicable: "If X then Y, else Z"]
4. [Step description]
5. [Step description]

**Decision Points:**
| At Step | Condition | Yes Path | No Path |
|---------|-----------|----------|---------|
| | | | |

**Success Criteria:** [What defines a successful completion of this flow]

---

### Flow 2: [Workflow Name]
- **Description:**
- **Trigger:**
- **Actor(s):**

**Steps:**
1.
2.
3.
4.
5.

**Decision Points:**
| At Step | Condition | Yes Path | No Path |
|---------|-----------|----------|---------|
| | | | |

**Success Criteria:**

---

### Flow 3: [Workflow Name]
- **Description:**
- **Trigger:**
- **Actor(s):**

**Steps:**
1.
2.
3.
4.
5.

**Decision Points:**
| At Step | Condition | Yes Path | No Path |
|---------|-----------|----------|---------|
| | | | |

**Success Criteria:**
```

**Instructions:**
- Each flow represents a distinct business process — not a UI screen sequence.
- Decision points must reference specific steps by number.
- Success criteria should be observable (testable), not subjective.

**Validation checklist:**
- [ ] Minimum 3 flows defined
- [ ] Each flow has at least 5 steps
- [ ] Each flow has at least 1 decision point documented
- [ ] Each flow has a success criteria statement

**Related sections:** 06 (Use Cases), 07 (Business Rules), 15 (Testing)

---

## 05 Integration Layer

> **Purpose:** Specifies all external system integrations — endpoints, authentication, error handling, and rate limits. This section drives integration contract generation.

```markdown
## Integration Layer

<!-- REQUIRED: One entry per external system integration. -->

### Integration: [System Name]
- **System:** [e.g., Salesforce CRM, Core Banking API]
- **Purpose:** What data or capability this integration provides
- **Integration Type:** REST | SOAP | GraphQL | gRPC | Event/Kafka | File/SFTP

**Endpoints:**
| Method | Path | Purpose | Request Schema | Response Schema |
|--------|------|---------|----------------|-----------------|
| GET | /api/v1/... | | | |
| POST | /api/v1/... | | | |

**Authentication:**
- **Method:** OAuth2 | API Key | mTLS | Basic | JWT
- **Token endpoint:** [URL or N/A]
- **Scopes required:** [e.g., read:accounts, write:transactions]
- **Credential storage:** [e.g., Azure Key Vault, AWS Secrets Manager]

**Error Handling:**
| HTTP Status | Meaning | Retry? | Action |
|-------------|---------|--------|--------|
| 400 | Bad Request | No | Log and reject |
| 401 | Unauthorized | No | Refresh token |
| 429 | Rate Limited | Yes | Exponential backoff |
| 500 | Server Error | Yes | Retry with backoff |
| 503 | Unavailable | Yes | Circuit breaker |

**Rate Limits:**
- Requests per minute: [number or "unknown"]
- Burst limit: [number or "unknown"]
- Throttle strategy: [e.g., token bucket, fixed window]

**Contract Version:** [e.g., v2.1 — date of last verification]

---

### Integration: [System Name]
<!-- Repeat block above for each integration -->
```

**Instructions:**
- Every external API call must be documented here — including internal microservices the product does not own.
- The pipeline will generate integration stubs from this section.
- If a system has no SLA, note it — this is a risk for the NFR section.

**Validation checklist:**
- [ ] Each integration has a defined authentication method
- [ ] Error handling table covers at minimum: 400, 401, 429, 500, 503
- [ ] Rate limits are documented (even if unknown — flag them)
- [ ] Contract version or last-verified date is present

**Related sections:** 09 (NFRs), 10 (Security), 08 (Data Requirements)

---

## 06 Use Cases

> **Purpose:** The most critical section. Defines the exact behavior of the system from the user's perspective. Use cases are the primary input to code generation and test planning.

```markdown
## Use Cases

<!--
REQUIRED: Minimum 3 use cases.
Each use case MUST have a UC-XXX identifier.
Exception flows are required: minimum 2 per use case.
Main flow must have minimum 5 steps.
-->

---

### UC-001: [Use Case Title]

| Field | Value |
|-------|-------|
| **ID** | UC-001 |
| **Title** | [Short, action-oriented title] |
| **Actor(s)** | [Primary actor, Secondary actors] |
| **Priority** | Critical \| High \| Medium \| Low |

**Preconditions:**
- [Condition that must be true before this use case can begin]
- [Condition 2]

**Trigger:** [What event or action initiates this use case]

**Main Flow:**
| Step | Actor | Action | System Response |
|------|-------|--------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

**Alternative Flows:**
<!-- Variations of the happy path that still succeed -->

**AF-001-01: [Alternative Flow Title]**
- At step [N]: [Condition that triggers this alternative]
- [Steps describing the alternative path]
- Rejoins main flow at step [N] OR ends with [outcome]

**Exception Flows:**
<!-- Error conditions and failure modes — minimum 2 per use case -->

**EF-001-01: [Exception Title]**
- At step [N]: [Condition that triggers this exception]
- System: [What the system does in response]
- User: [What the user sees/can do]
- Resolution: [How normal flow can be resumed, or final state]

**EF-001-02: [Exception Title]**
- At step [N]:
- System:
- User:
- Resolution:

**Postconditions:**
- **Success:** [State of the system after successful completion]
- **Failure:** [State of the system after an exception that cannot be resolved]

**Business Rules Referenced:** [e.g., BR-001, BR-003]

**Data Elements:**
| Element | Source | Destination | Validation |
|---------|--------|-------------|------------|
| | | | |

**Security Requirements Referenced:** [e.g., SEC-001, SEC-002]

**Success Criteria:**
- [Observable, testable statement of what "done" means for this use case]
- [Second criterion]

---

### UC-002: [Use Case Title]
<!-- Copy the full UC-001 block and fill in -->

---

### UC-003: [Use Case Title]
<!-- Copy the full UC-001 block and fill in -->
```

**Instructions:**
- UC-XXX IDs must be unique and sequential.
- Main flow steps must be granular enough that a developer can implement each step as a discrete function.
- Alternative flows describe valid variations (e.g., user chooses a different option). Exception flows describe errors and failures.
- Business Rules must reference IDs from section 07. Security refs must reference IDs from section 10.

**Validation checklist:**
- [ ] Minimum 3 use cases with UC-XXX IDs
- [ ] Each use case has at least 5 main flow steps
- [ ] Each use case has at least 2 exception flows (EF-XXX)
- [ ] Each use case has at least 1 alternative flow (AF-XXX)
- [ ] Business rules references point to valid BR-XXX IDs in section 07
- [ ] Security references point to valid SEC-XXX IDs in section 10
- [ ] All postconditions (success and failure) are defined

**Related sections:** 07 (Business Rules), 08 (Data Requirements), 10 (Security), 15 (Testing)

---

## 07 Business Rules

> **Purpose:** Defines the formal business logic that governs system behavior. Rules are referenced from use cases and are enforced during code generation validation.

```markdown
## Business Rules

<!--
REQUIRED: Minimum 10 rules with BR-XXX identifiers.
Each rule must have: description, condition, action, applies-to, priority, type.
-->

| ID | Rule Name | Description | Condition | Action | Applies To | Priority | Type |
|----|-----------|-------------|-----------|--------|------------|----------|------|
| BR-001 | | | | | | Critical \| High \| Medium \| Low | Validation \| Calculation \| Authorization \| Workflow \| Constraint |
| BR-002 | | | | | | | |
| BR-003 | | | | | | | |
| BR-004 | | | | | | | |
| BR-005 | | | | | | | |
| BR-006 | | | | | | | |
| BR-007 | | | | | | | |
| BR-008 | | | | | | | |
| BR-009 | | | | | | | |
| BR-010 | | | | | | | |

<!--
Extended detail for complex rules (optional but recommended for Critical/High rules):
-->

### BR-001 Detail: [Rule Name]
- **Full Description:** [Detailed explanation of the rule]
- **Example:** [Concrete example showing the rule in action]
- **Exceptions:** [Any conditions where this rule does not apply]
- **Source:** [Regulatory requirement, business policy, or technical constraint]
```

**Instructions:**
- `Type` categories: Validation (input checks), Calculation (computed values), Authorization (access control), Workflow (process sequencing), Constraint (data integrity).
- Every BR-XXX referenced in section 06 (Use Cases) must exist here.
- `Applies To` should reference use case IDs (UC-XXX) or component names.

**Validation checklist:**
- [ ] Minimum 10 rules with BR-XXX IDs
- [ ] Every BR-XXX referenced in section 06 exists in this table
- [ ] Each rule has all 6 required fields filled (description, condition, action, applies-to, priority, type)
- [ ] At least 2 rules of type Authorization
- [ ] At least 2 rules of type Validation

**Related sections:** 06 (Use Cases), 08 (Data Requirements), 10 (Security)

---

## 08 Data Requirements

> **Purpose:** Defines the data model — entities, attributes, relationships, and storage strategy. This section drives schema generation and data validation rules.

```markdown
## Data Requirements

<!--
REQUIRED: Minimum 3 entities with minimum 5 attributes each.
-->

### Entity: [EntityName]
- **Description:** What this entity represents
- **Storage:** [e.g., PostgreSQL, MongoDB, Redis, Azure Blob]
- **PII:** [Yes | No — if Yes, list PII fields below]

**Attributes:**
| Field | Type | Required | Description | Validation Rule |
|-------|------|----------|-------------|-----------------|
| id | UUID | Yes | Primary key | Auto-generated |
| created_at | DateTime | Yes | Record creation timestamp | ISO 8601 |
| updated_at | DateTime | Yes | Last update timestamp | ISO 8601 |
| | | | | |
| | | | | |

**PII Fields (if applicable):**
| Field | Sensitivity | Encryption Required | Masking Rule |
|-------|-------------|---------------------|--------------|
| | High \| Medium \| Low | Yes \| No | [e.g., last 4 digits visible] |

---

### Entity: [EntityName]
<!-- Repeat the block above -->

---

### Entity: [EntityName]
<!-- Repeat the block above -->

---

### Relationships
| From Entity | Relationship | To Entity | Cardinality | Notes |
|-------------|-------------|-----------|-------------|-------|
| | has many | | 1:N | |
| | belongs to | | N:1 | |
| | has one | | 1:1 | |

### Input Schema
<!-- REQUIRED: For each API/event entry point, define the input contract. -->
| Endpoint / Event | Field | Type | Required | Constraints / Validation |
|------------------|-------|------|----------|--------------------------|
| `POST /resource` | `name` | string | Yes | 1–80 chars, non-empty |
| `POST /resource` | `amount` | decimal | Yes | > 0, max 2 decimal places |
| `event.resource.updated` | `resource_id` | UUID | Yes | Must exist in primary entity table |
| | | | | |

### Output Schema
<!-- REQUIRED: For each endpoint/event, define the response/payload contract. -->
| Endpoint / Event | Field | Type | Required | Notes |
|------------------|-------|------|----------|-------|
| `POST /resource` (201) | `id` | UUID | Yes | Generated server-side |
| `POST /resource` (201) | `created_at` | DateTime | Yes | ISO 8601 UTC |
| `POST /resource` (4xx) | `error.code` | string | Yes | Stable machine-readable code |
| `POST /resource` (4xx) | `error.message` | string | Yes | Human-readable, no PII |
| | | | | |

### Storage Strategy
| Store Type | Technology | Use Case | Retention Policy |
|------------|-----------|----------|-----------------|
| Primary DB | | Transactional data | |
| Cache | | Session / hot data | |
| Object Store | | Files, documents | |
| Search Index | | Full-text search | |

### Data Security
- **Encryption at rest:** [e.g., AES-256 via database TDE]
- **Encryption in transit:** [e.g., TLS 1.3 mandatory]
- **Key management:** [e.g., Azure Key Vault, AWS KMS]
- **Backup strategy:** [e.g., daily snapshots, 30-day retention, geo-redundant]
```

**Instructions:**
- Every entity used in section 06 (Use Cases) Data Elements table must be defined here.
- PII fields require explicit encryption and masking rules — the pipeline will flag missing security controls.
- Validation rules should reference business rules (BR-XXX) where applicable.

**Validation checklist:**
- [ ] Minimum 3 entities defined
- [ ] Each entity has at least 5 attributes
- [ ] All attributes have Type, Required, and Validation Rule fields filled
- [ ] PII fields have encryption and masking rules specified
- [ ] Relationships table covers all inter-entity links
- [ ] Storage strategy and data security sections are complete

**Related sections:** 06 (Use Cases), 07 (Business Rules), 10 (Security)

---

## 09 Non-Functional Requirements

> **Purpose:** Defines measurable quality attributes the system must achieve. NFRs drive infrastructure sizing, SLA commitments, and acceptance testing criteria.

```markdown
## Non-Functional Requirements

<!--
REQUIRED: Minimum 15 NFRs across all 5 categories (minimum 2 per category).
Each NFR must have a measurable target — no subjective statements.
-->

### Performance
| ID | Requirement | Metric | Target | Measurement Method |
|----|-------------|--------|--------|--------------------|
| NFR-P01 | Page load time | Time to Interactive | < 2s on 4G | Lighthouse CI |
| NFR-P02 | API response time | p95 latency | < 300ms | APM tool |
| NFR-P03 | | | | |

### Scalability
| ID | Requirement | Metric | Target | Measurement Method |
|----|-------------|--------|--------|--------------------|
| NFR-S01 | Concurrent users | Active sessions | 10,000 | Load test |
| NFR-S02 | Throughput | Requests per second | 1,000 RPS | Load test |
| NFR-S03 | | | | |

### Availability
| ID | Requirement | Metric | Target | Measurement Method |
|----|-------------|--------|--------|--------------------|
| NFR-A01 | System uptime | Availability % | 99.9% (8.7h/yr downtime) | Uptime monitor |
| NFR-A02 | RTO | Recovery time | < 4 hours | DR drill |
| NFR-A03 | RPO | Data loss window | < 1 hour | Backup audit |

### Security
| ID | Requirement | Metric | Target | Measurement Method |
|----|-------------|--------|--------|--------------------|
| NFR-SEC01 | Auth failure lockout | Failed attempts before lock | 5 attempts | Penetration test |
| NFR-SEC02 | Session timeout | Idle timeout | 30 minutes | Security audit |
| NFR-SEC03 | | | | |

### Reliability
| ID | Requirement | Metric | Target | Measurement Method |
|----|-------------|--------|--------|--------------------|
| NFR-R01 | Error rate | % of failed requests | < 0.1% | Error tracking |
| NFR-R02 | MTBF | Mean time between failures | > 720 hours | Incident log |
| NFR-R03 | | | | |
```

**Instructions:**
- Every NFR must have a numeric target — "fast" or "reliable" are not acceptable.
- Measurement methods must be tooling-specific where possible (Lighthouse, k6, Datadog, etc.).
- NFRs feed directly into infrastructure specifications and load test configurations.

**Validation checklist:**
- [ ] Minimum 15 NFRs total
- [ ] At least 2 NFRs in each of the 5 categories
- [ ] Every NFR has a numeric/measurable target
- [ ] Every NFR has a measurement method specified
- [ ] RTO and RPO are defined under Availability

**Related sections:** 05 (Integration Layer), 10 (Security), 15 (Testing)

---

## 10 Security and Compliance

> **Purpose:** Defines security controls, compliance standards, and encryption requirements. This section is a code generation prerequisite — no secure code can be generated without it.

```markdown
## Security and Compliance

### Security Requirements
<!--
REQUIRED: Minimum 5 requirements with SEC-XXX identifiers.
-->
| ID | Requirement | Implementation | Priority | Validation Method |
|----|-------------|----------------|----------|-------------------|
| SEC-001 | Authentication | OAuth2 + PKCE with MFA enforcement | Critical | Pen test |
| SEC-002 | Authorization | RBAC with least-privilege model | Critical | Code review |
| SEC-003 | Data encryption in transit | TLS 1.3 mandatory, TLS 1.2 minimum | Critical | SSL scan |
| SEC-004 | Data encryption at rest | AES-256 for all PII fields | Critical | Security audit |
| SEC-005 | Input validation | Sanitize all inputs; parameterized queries only | High | SAST scan |
| SEC-006 | | | | |
| SEC-007 | | | | |

### Compliance Standards
| Standard | Applicability | Key Requirements | Validation Frequency |
|----------|--------------|-----------------|----------------------|
| GDPR | EU user data | Consent, right to erasure, DPA | Annual audit |
| PCI-DSS | Payment card data | Tokenization, no raw card storage | Quarterly scan |
| SOC 2 Type II | Enterprise customers | Access control, availability, confidentiality | Annual audit |
| [Other] | | | |

### Encryption Standards
| Layer | Protocol/Algorithm | Minimum Version | Notes |
|-------|--------------------|-----------------|-------|
| Transport | TLS | 1.3 (1.2 minimum) | Enforce HSTS |
| Storage — PII | AES | 256-bit | Key rotation every 90 days |
| Storage — Passwords | bcrypt / Argon2 | Cost factor >= 12 | Never store plaintext |
| API Keys / Secrets | [Key vault solution] | N/A | No secrets in code |

### Security Controls
- **SAST (Static Analysis):** [Tool name, e.g., SonarQube, Snyk]
- **DAST (Dynamic Analysis):** [Tool name, e.g., OWASP ZAP, Burp Suite]
- **Dependency scanning:** [Tool name, e.g., Dependabot, Snyk]
- **Secret scanning:** [Tool name, e.g., GitGuardian, GitHub Secret Scanning]
- **Penetration testing:** [Frequency, e.g., annually by certified third party]

### Data Privacy
- **PII inventory:** [Reference to section 08 Data Requirements or separate DPA document]
- **Data retention:** [e.g., 7 years for financial records, 90 days for logs]
- **Right to erasure:** [Process for handling deletion requests]
- **Data residency:** [e.g., EU data must remain in EU Azure regions]
```

**Instructions:**
- Every SEC-XXX referenced in section 06 (Use Cases) must exist here.
- TLS and AES entries are mandatory — the pipeline will fail without them.
- Compliance standards must match what was listed in section 01 Document Information.

**Validation checklist:**
- [ ] Minimum 5 security requirements with SEC-XXX IDs
- [ ] TLS version specified under Encryption Standards
- [ ] AES-256 (or justified alternative) specified for storage encryption
- [ ] All compliance standards from section 01 are addressed here
- [ ] All SEC-XXX IDs referenced in section 06 exist in this table
- [ ] Secret management approach is documented

**Related sections:** 01 (Document Information), 06 (Use Cases), 08 (Data Requirements)

---

## 11 User Personas and Actors

> **Purpose:** Describes the people who use the system — their goals, pain points, access levels, and behaviors. The primary persona drives UX and feature prioritization decisions.

```markdown
## User Personas and Actors

<!--
REQUIRED: Minimum 3 personas. Mark exactly one as the primary persona.
-->

### Persona 1: [Persona Name] [PRIMARY]
| Attribute | Value |
|-----------|-------|
| **Role/Title** | [e.g., Senior Loan Officer] |
| **Department** | [e.g., Retail Banking] |
| **Age Range** | [e.g., 35–50] |
| **Tech Proficiency** | Low \| Medium \| High |
| **Usage Frequency** | Daily \| Weekly \| Monthly \| Occasional |

**Goals:**
- [What they want to accomplish with this product]
- [Second goal]
- [Third goal]

**Pain Points (current state):**
- [What frustrates them today — before this product]
- [Second pain point]
- [Third pain point]

**Access Level:** Admin \| Manager \| User \| Read-Only \| API

**Key Use Cases:** UC-001, UC-002 [reference UC-XXX IDs]

**Quote:** "[A representative quote that captures their mindset]"

---

### Persona 2: [Persona Name]
| Attribute | Value |
|-----------|-------|
| **Role/Title** | |
| **Department** | |
| **Age Range** | |
| **Tech Proficiency** | Low \| Medium \| High |
| **Usage Frequency** | Daily \| Weekly \| Monthly \| Occasional |

**Goals:**
-
-

**Pain Points:**
-
-

**Access Level:**

**Key Use Cases:**

---

### Persona 3: [Persona Name]
<!-- Copy the block above and fill in -->

---

### System Actors
<!-- Non-human actors that interact with the system -->
| Actor | Type | Interaction | Authentication |
|-------|------|-------------|----------------|
| [e.g., Payment Gateway] | External System | Webhook callbacks | API Key + IP allowlist |
| [e.g., Scheduler] | Internal Service | Cron job trigger | Service account |
| | | | |
```

**Instructions:**
- Exactly one persona must be marked as [PRIMARY] — this drives default UX decisions.
- Access Level must be consistent with business rules in section 07 (Authorization rules).
- System actors must reference the integration entries from section 05.

**Validation checklist:**
- [ ] Minimum 3 personas defined
- [ ] Exactly one persona marked as PRIMARY
- [ ] Each persona has goals, pain points, and access level
- [ ] Key Use Cases reference valid UC-XXX IDs from section 06
- [ ] System actors are listed with authentication methods

**Related sections:** 06 (Use Cases), 05 (Integration Layer), 07 (Business Rules)

---

## 12 Constraints, Assumptions and Scope

> **Purpose:** Defines what is in scope, what is not, and what assumptions have been made. Prevents scope creep and misaligned expectations during development.

```markdown
## Constraints, Assumptions and Scope

### Technical Constraints
| Constraint | Description | Impact |
|------------|-------------|--------|
| [e.g., Must use existing Oracle DB] | | [e.g., Limits ORM choice] |
| [e.g., No new cloud infrastructure] | | |
| | | |

### Business Constraints
| Constraint | Description | Impact |
|------------|-------------|--------|
| [e.g., Budget cap of $500K] | | |
| [e.g., Go-live before Q4 regulatory deadline] | | |
| | | |

### Assumptions
<!--
List assumptions that, if wrong, would materially change the scope or design.
Each assumption should have an owner and a validation date.
-->
| # | Assumption | Owner | Validation Date | Risk if Wrong |
|---|------------|-------|-----------------|---------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### In-Scope Features
<!--
REQUIRED: List all features that WILL be built in this release.
-->
| Feature | Priority | Phase / Release |
|---------|----------|-----------------|
| | Must Have \| Should Have \| Nice to Have | |
| | | |
| | | |

### Out-of-Scope Features
<!--
Features explicitly excluded from this release (to avoid "but I thought..." conversations).
-->
| Feature | Reason for Exclusion | Future Phase? |
|---------|----------------------|---------------|
| | | Yes \| No \| TBD |
| | | |
| | | |
```

**Instructions:**
- In-scope features are REQUIRED — the pipeline uses them to validate use case coverage.
- Out-of-scope features protect the team from scope creep — be explicit.
- Assumptions must have owners who can verify them before development starts.

**Validation checklist:**
- [ ] At least 3 in-scope features listed with priorities
- [ ] At least 3 out-of-scope features listed
- [ ] All assumptions have owners and validation dates
- [ ] Technical and business constraints are documented

**Related sections:** 02 (Executive Summary), 06 (Use Cases), 13 (Architecture)

---

## 13 Application Type and Architecture

> **Purpose:** Specifies the technology stack selection and service architecture. This section drives which BNAC stack modules are activated for code generation.

```markdown
## Application Type and Architecture

### Language and Framework Selection
<!--
REQUIRED: Select the primary language. This determines which BNAC stack is used.
-->
| Dimension | Selection | Justification |
|-----------|-----------|---------------|
| **Primary Language** | Python \| DotNet \| React \| Flutter | |
| **Framework** | [e.g., FastAPI, ASP.NET Core 8, Next.js 14, Flutter 3.x] | |
| **Secondary Languages** | [e.g., TypeScript for frontend] | |
| **Runtime** | [e.g., Python 3.11, .NET 8, Node 20] | |

### Service Type
| Attribute | Value |
|-----------|-------|
| **Service Type** | Monolith \| Microservices \| Serverless \| Hybrid |
| **API Style** | REST \| GraphQL \| gRPC \| Event-Driven |
| **Frontend Type** | SPA \| SSR \| SSG \| MPA \| Mobile \| None |
| **Deployment Target** | Kubernetes \| App Service \| Lambda \| Container \| VM |

### BNAC Stack Modules Activated
<!--
Auto-resolved by the pipeline based on Language selection above.
Manual override allowed — justify any deviation.
-->
| Module | Auto-Resolved? | Override | Justification |
|--------|---------------|----------|---------------|
| [e.g., react-ts] | Yes | No | |
| [e.g., stacks/dotnet] | Yes | No | |
| [e.g., core/agents] | Yes | No | |

### Reference Files
<!--
The pipeline resolves these automatically based on stack selection.
List any custom reference files that should be injected.
-->
| Reference | Path | Purpose |
|-----------|------|---------|
| Stack rules | [auto-resolved] | Coding standards for selected stack |
| Design system | [auto-resolved] | Component and token library |
| [Custom] | | |

### Infrastructure Diagram
<!-- Optional but recommended for microservices/distributed systems -->
```

**Instructions:**
- Primary Language selection is mandatory — the pipeline will not proceed without it.
- Valid values for Primary Language: `Python`, `DotNet`, `React`, `Flutter`.
- Service Type and API Style combination must be architecturally consistent (e.g., Microservices + REST is fine; Monolith + Event-Driven needs justification).

**Validation checklist:**
- [ ] Primary Language is one of: Python, DotNet, React, Flutter
- [ ] Framework is specified for the chosen language
- [ ] Service Type is defined
- [ ] API Style is defined
- [ ] Deployment Target is specified

**Related sections:** 03 (Architecture Overview), 09 (NFRs), 05 (Integration Layer)

---

## 14 Glossary of Terms

> **Purpose:** Defines domain-specific terms, acronyms, and abbreviations. Ensures all stakeholders use consistent language throughout the PRD and codebase.

```markdown
## Glossary of Terms

<!--
REQUIRED: Minimum 20 terms covering technical terms, business terms, and acronyms.
-->

### Technical Terms
| Term | Definition | Context |
|------|------------|---------|
| [e.g., JWT] | JSON Web Token — a compact, URL-safe token format for claims transmission | Authentication |
| [e.g., PKCE] | Proof Key for Code Exchange — OAuth2 extension for public clients | Security |
| [e.g., Idempotency] | Property where an operation produces the same result regardless of how many times it is executed | API Design |
| | | |
| | | |

### Business Terms
| Term | Definition | Source |
|------|------------|--------|
| [e.g., LTV] | Loan-to-Value ratio — the ratio of a loan amount to the appraised value of the asset | Lending domain |
| [e.g., Drawdown] | The act of withdrawing funds from an approved credit facility | Credit domain |
| | | |
| | | |

### Acronyms
| Acronym | Expansion | Domain |
|---------|-----------|--------|
| PRD | Product Requirements Document | Project Management |
| BNAC | BusinessNext Agentic Coding | Platform |
| API | Application Programming Interface | Technology |
| UC | Use Case | Requirements |
| BR | Business Rule | Requirements |
| NFR | Non-Functional Requirement | Quality |
| PII | Personally Identifiable Information | Privacy |
| RTO | Recovery Time Objective | Availability |
| RPO | Recovery Point Objective | Availability |
| RBAC | Role-Based Access Control | Security |
| | | |
| | | |
```

**Instructions:**
- All acronyms used in the PRD must appear in this glossary.
- Business terms should reference their domain source (regulatory, internal policy, industry standard).
- When in doubt, add a term — it is better to over-define than under-define.

**Validation checklist:**
- [ ] Minimum 20 terms defined (combined across all three tables)
- [ ] All acronyms used in sections 06, 07, 10 are listed here
- [ ] Each term has a definition and context/source

**Related sections:** All sections

---

## 15 Testing and Quality Assurance

> **Purpose:** Defines the testing strategy, coverage requirements, and quality gates. This section drives test plan generation and CI/CD pipeline configuration.

```markdown
## Testing and Quality Assurance

### Testing Strategy
| Level | Type | Tools | Scope | Owner |
|-------|------|-------|-------|-------|
| Unit | Automated | [e.g., Jest, xUnit, pytest] | Individual functions/classes | Developer |
| Integration | Automated | [e.g., Supertest, TestContainers] | API contracts, DB interactions | Developer |
| System | Automated + Manual | [e.g., Playwright, Cypress] | End-to-end user journeys | QA |
| UAT | Manual | [e.g., TestRail] | Business acceptance criteria | Product Owner |
| Performance | Automated | [e.g., k6, JMeter] | NFR targets from section 09 | DevOps |
| Security | Automated + Manual | [e.g., OWASP ZAP, Burp Suite] | Pen test checklist | Security |

### Coverage Requirements
| Layer | Minimum Coverage | Target Coverage | Measurement Tool |
|-------|-----------------|-----------------|-----------------|
| Unit tests — business logic | 80% | 90% | [e.g., Istanbul, Coverage.py] |
| Integration tests — API endpoints | 80% | 90% | [e.g., SonarQube] |
| E2E — critical user journeys (UC-XXX) | 100% of UC-001, UC-002, UC-003 | | |

### Quality Gates
<!--
Gates that must pass before merging to main / deploying to production.
-->
| Gate | Condition | Blocks |
|------|-----------|--------|
| Build | Must compile without errors or warnings | PR merge |
| Unit tests | All pass, coverage >= 80% | PR merge |
| Integration tests | All pass | PR merge |
| SAST scan | Zero Critical or High findings | PR merge |
| Dependency scan | Zero Critical CVEs | PR merge |
| E2E — smoke | Core flows pass | Deploy to staging |
| UAT sign-off | Product Owner approval | Deploy to production |

### Test Data Strategy
- **Approach:** [e.g., synthetic data generated via factories, anonymized production snapshot]
- **PII handling:** [e.g., all PII is masked before use in test environments]
- **Refresh frequency:** [e.g., nightly refresh from anonymized prod snapshot]

### Defect Management
- **Tracking tool:** [e.g., Jira]
- **Severity definitions:**
  - **Critical** — System down, data loss, security breach
  - **High** — Core feature broken, no workaround
  - **Medium** — Feature degraded, workaround exists
  - **Low** — Cosmetic, minor inconvenience
- **SLA:** Critical: 4h fix | High: 1 business day | Medium: 1 sprint | Low: backlog
```

**Instructions:**
- Unit test coverage target of 80% minimum is enforced by the pipeline quality gate.
- E2E tests must cover all use cases marked as Critical or High priority in section 06.
- Quality gates must include at minimum: build pass, unit test pass, SAST pass.

**Validation checklist:**
- [ ] All 6 testing levels are addressed (unit, integration, system, UAT, performance, security)
- [ ] Unit test coverage minimum is >= 80%
- [ ] Quality gates list is defined with conditions and what they block
- [ ] E2E coverage references specific UC-XXX IDs from section 06
- [ ] Test data strategy addresses PII handling

**Related sections:** 06 (Use Cases), 09 (NFRs), 10 (Security)

---

## 16 Success Metrics and KPIs

> **Purpose:** Defines how the product's success will be measured after launch. KPIs align the engineering, product, and business teams on what "done" really means.

```markdown
## Success Metrics and KPIs

<!--
REQUIRED: Minimum 10 KPIs across business, technical, user, and operational categories.
Each KPI must have: baseline, target, timeframe, and measurement method.
-->

### Business KPIs
| KPI | Baseline | Target | Timeframe | Measurement Method |
|-----|----------|--------|-----------|-------------------|
| [e.g., Loan processing time] | [e.g., 5 days] | [e.g., 1 day] | 6 months post-launch | System timestamp diff |
| [e.g., Revenue per user] | | | | |
| [e.g., Process automation rate] | | | | |

### Technical KPIs
| KPI | Baseline | Target | Timeframe | Measurement Method |
|-----|----------|--------|-----------|-------------------|
| [e.g., API p95 latency] | [e.g., 800ms] | [e.g., < 300ms] | Day 1 of production | APM dashboard |
| [e.g., System uptime] | [e.g., 98.5%] | [e.g., 99.9%] | 3 months rolling | Uptime monitor |
| [e.g., Deployment frequency] | [e.g., Monthly] | [e.g., Weekly] | 3 months post-launch | CI/CD metrics |

### User KPIs
| KPI | Baseline | Target | Timeframe | Measurement Method |
|-----|----------|--------|-----------|-------------------|
| [e.g., User adoption rate] | [e.g., 0%] | [e.g., 80% of target users] | 90 days post-launch | Auth logs |
| [e.g., Task completion rate] | | | | |
| [e.g., User satisfaction (CSAT)] | | | | |

### Operational KPIs
| KPI | Baseline | Target | Timeframe | Measurement Method |
|-----|----------|--------|-----------|-------------------|
| [e.g., Mean time to resolve (MTTR)] | | | | |
| [e.g., On-call incident rate] | | | | |
| [e.g., Test coverage] | [e.g., 0%] | [e.g., >= 80%] | Sprint 1 | Coverage report |

### KPI Review Cadence
| Cadence | KPIs Reviewed | Forum | Owner |
|---------|--------------|-------|-------|
| Weekly | Technical KPIs (performance, uptime) | Engineering standup | Tech Lead |
| Monthly | Business + User KPIs | Product review | Product Owner |
| Quarterly | All KPIs — strategic review | Steering committee | Programme Manager |
```

**Instructions:**
- Every KPI must have a numeric baseline (use "0" or "not measured" if unknown, but flag it as a gap).
- Timeframes must be specific (e.g., "90 days post-launch", not "soon").
- KPIs should connect back to the success metrics defined in section 02 (Executive Summary).

**Validation checklist:**
- [ ] Minimum 10 KPIs total across all 4 categories
- [ ] Each KPI has a baseline (even if 0 or "not measured")
- [ ] Each KPI has a numeric target
- [ ] Each KPI has a specific timeframe
- [ ] Each KPI has a measurement method
- [ ] KPI review cadence is defined

**Related sections:** 02 (Executive Summary), 09 (NFRs), 15 (Testing)

---

## 17 Sample Scenarios and Interaction Model

> **Purpose:** Concrete, end-to-end runnable examples for each Use Case from section 06, plus the interaction model (sync / async / streaming) and turn-taking rules between actors. Generated test cases and integration contracts use this section as ground truth.

```markdown
## Sample Scenarios and Interaction Model

### Interaction Model
| Use Case | Interaction Style | Channel | Turn-taking Rule |
|----------|-------------------|---------|------------------|
| UC-001 | Synchronous request/response | HTTPS REST | Single round-trip; client blocks until response |
| UC-002 | Asynchronous fire-and-forget | Message queue | Producer does not wait; ack ≠ completion |
| UC-003 | Streaming | Server-Sent Events / WebSocket | Server pushes; client may cancel |

### Sample Scenario: UC-001 — [Use Case Name]
- **Actor:** [persona from section 11]
- **Preconditions:** [system state, data already present]
- **Input (concrete values):**
  ```json
  { "field_a": "value", "field_b": 42 }
  ```
- **Step-by-step:**
  1. Actor performs [action]
  2. System validates against BR-001
  3. System persists [entity]
  4. System emits [event]
- **Expected output (concrete values):**
  ```json
  { "id": "uuid-here", "status": "created" }
  ```
- **Postconditions:** [observable system state after run]

### Sample Scenario: UC-002 — [Use Case Name]
<!-- Repeat for every Tier-1 (Critical) and Tier-2 (High) use case from section 06. -->

### Edge / Negative Scenarios
| Scenario | Trigger | Expected Behavior | Related BR / FAIL-XXX |
|----------|---------|-------------------|-----------------------|
| Duplicate submission | Same idempotency key | Return original 201, no duplicate write | FAIL-001 |
| Downstream timeout | Integration call > NFR-P02 budget | Surface 504; do not retry inside request | FAIL-002 |
```

**Instructions:**
- Each Critical / High use case from section 06 must have at least one sample scenario with concrete (non-placeholder) input and output values.
- Interaction style must match the API style declared in section 13.
- Edge scenarios must reference an entry in section 19 (Failure Modes & Idempotency).

**Validation checklist:**
- [ ] Every Critical/High UC has at least one sample scenario
- [ ] Each scenario has Input, Steps, Output, Postconditions
- [ ] Interaction model row exists for every UC
- [ ] At least 3 edge / negative scenarios listed

**Related sections:** 06 (Use Cases), 08 (Data Requirements — Input/Output Schema), 19 (Failure Modes), 13 (Application Type)

---

## 18 State Machine Definition

> **Purpose:** Defines finite-state behavior for entities and workflows with explicit transitions, guards, and terminal states. Without this layer the code generator invents its own status enums and the testing layer cannot verify exhaustive transitions.

```markdown
## State Machine Definition

<!-- REQUIRED: At least 1 state machine for every entity / workflow that has more than 2 states. -->

### State Machine: [EntityOrWorkflow Name]
- **Owner Entity:** [entity from section 08]
- **Initial State:** `[state]`
- **Terminal States:** `[state]`, `[state]`

**States:**
| State | Meaning | Allowed Operations | SLA / Time Limit |
|-------|---------|---------------------|------------------|
| `draft` | Not yet submitted | edit, delete | — |
| `submitted` | Awaiting review | review, withdraw | 48h auto-expire |
| `approved` | Active | use, archive | — |
| `rejected` | Terminal | view | — |
| `archived` | Terminal | view | — |

**Transitions:**
| From | Event | To | Guard (Business Rule) | Side Effect | Actor |
|------|-------|----|-----------------------|-------------|-------|
| draft | submit | submitted | BR-001 (mandatory fields present) | Notify reviewer | author |
| submitted | approve | approved | BR-002 (reviewer ≠ author) | Emit event `resource.approved` | reviewer |
| submitted | reject | rejected | — | Persist reason | reviewer |
| approved | archive | archived | — | Remove from active index | system |

**Diagram (ASCII):**
```
[draft] --submit--> [submitted] --approve--> [approved] --archive--> [archived]
                       |                          (terminal)
                       +--reject--> [rejected] (terminal)
```

### State Machine: [SecondEntityOrWorkflow]
<!-- Repeat the block above for each stateful entity/workflow. -->

### Illegal Transition Policy
- **Detection:** Any attempt to transition outside the table above is rejected with `409 Conflict` (or equivalent) and logged.
- **Telemetry:** Emit `state.illegal_transition` metric (see section 21 Observability).
```

**Instructions:**
- One state machine per stateful entity or workflow. Pure CRUD entities without lifecycle do not need one.
- Every transition must reference a Business Rule (BR-XXX) as its guard, or explicitly note "no guard".
- Terminal states must be marked — they are the test exit conditions.

**Validation checklist:**
- [ ] At least 1 state machine defined when any entity has > 2 states
- [ ] Every transition row has From / Event / To / Guard / Actor
- [ ] Terminal states explicitly listed
- [ ] ASCII or table diagram present per machine
- [ ] Illegal transition policy defined

**Related sections:** 08 (Data Requirements), 07 (Business Rules), 19 (Failure Modes), 21 (Observability)

---

## 19 Failure Modes, Concurrency and Idempotency

> **Purpose:** System-level (not just per-UC) failure expectations, concurrency model, and idempotency contract. Undefined failures become production outages; undefined idempotency causes duplicate financial transactions.

```markdown
## Failure Modes, Concurrency and Idempotency

### Failure Modes (system level)
<!-- REQUIRED: Minimum 5 FAIL-XXX entries. -->
| ID | Failure Scenario | Detection | Expected Behavior | Recovery | Visible To |
|----|------------------|-----------|-------------------|----------|------------|
| FAIL-001 | Downstream integration timeout | NFR-P02 budget exceeded | Return 504 + retry-after; circuit-break after 5 fails in 30s | Auto-resume on probe success | client, ops |
| FAIL-002 | Database unavailable | Connection pool exhausted | Return 503; do not lose in-flight queue messages | Pool refresh + leader re-election | ops |
| FAIL-003 | Message queue backpressure | Consumer lag > 10k | Throttle producer; emit `queue.backpressure` metric | Auto-scale consumers | ops |
| FAIL-004 | Auth provider outage | OAuth introspection fails | Honor cached tokens up to TTL; reject new logins with 503 | Resume when provider recovers | client, ops |
| FAIL-005 | Partial write (saga step fails) | Step N succeeded, N+1 failed | Run compensating action for steps 1..N | Saga marked `compensated` | system |
| | | | | | |

### Concurrency Model
| Aspect | Value | Notes |
|--------|-------|-------|
| Locking strategy | Optimistic (version column) \| Pessimistic (row lock) \| None | Per entity from section 08 |
| Conflict resolution | Last-write-wins \| Reject with 409 \| Merge | |
| Max parallelism per actor | [e.g., 1 in-flight write per user_id] | Enforced via rate limiter or queue |
| Transaction boundary | [e.g., per HTTP request, per saga step] | |

### Idempotency Contract
| Endpoint / Event | Idempotency Key Source | Key TTL | Duplicate Behavior |
|------------------|------------------------|---------|---------------------|
| `POST /resource` | Header `Idempotency-Key` (UUID) | 24h | Return original 201 response, no new write |
| `event.payment.charge` | Event `message_id` | 7d | No-op; ack and drop |
| | | | |

### Retry & Backoff Policy
- **Retryable status codes:** [e.g., 502, 503, 504, network errors]
- **Non-retryable:** [e.g., 4xx except 408, 429]
- **Backoff:** Exponential with jitter, base 200ms, cap 30s, max 5 attempts
- **Retry-after honor:** Yes — respect server-provided value
```

**Instructions:**
- FAIL-XXX IDs are global — referenced from sample scenarios (section 17) and tests (section 15).
- Every entity in section 08 with concurrent writers must have a locking strategy.
- Endpoints that mutate state must have an idempotency contract — no exceptions.

**Validation checklist:**
- [ ] Minimum 5 FAIL-XXX entries
- [ ] Concurrency model defined per stateful entity
- [ ] Idempotency key, TTL, and duplicate behavior specified for every state-mutating endpoint
- [ ] Retry/backoff policy documented with retryable codes and caps

**Related sections:** 17 (Sample Scenarios), 18 (State Machine), 09 (NFRs), 21 (Observability)

---

## 20 Governance, AI Guardrails and Observability

> **Purpose:** AI runtime controls (for AI-powered features), prompt/model versioning, and the observability contract that makes production debuggable. Skipping this layer ships AI features that cannot be audited and a production system that is blind.

```markdown
## Governance, AI Guardrails and Observability

### AI Runtime Controls
<!-- REQUIRED only if Application Type (section 13) declares AI / LLM features. Mark "N/A — no AI features" otherwise. -->
| Control | Value | Enforcement |
|---------|-------|-------------|
| Model allowlist | [e.g., `claude-opus-4-*`, `claude-sonnet-4-*` only] | Reject other model IDs at gateway |
| Prompt injection defense | [e.g., system prompt isolation; user input never templated into system instructions] | Gateway + code review |
| Output content filter | [e.g., PII redaction, profanity filter, hallucination check] | Pre-response middleware |
| Token cost ceiling | [e.g., 10k tokens per request, $50 per user per day] | Rate limiter |
| Human-in-the-loop trigger | [e.g., any output marked `confidence < 0.7`] | Workflow gate |

### AI Model and Prompt Versioning
| Asset | Versioning Scheme | Storage | Rollback Time |
|-------|-------------------|---------|----------------|
| Model ID | Pinned semver (`claude-opus-4-7`) | Config | < 5 min |
| System prompt | Git-tracked file, hash in response metadata | Repo | < 5 min |
| Few-shot examples | Versioned dataset reference | Object store + git pointer | < 15 min |
| Fine-tune adapters | If applicable — checksum + dataset hash | Registry | < 30 min |

### Observability Requirements
| Signal | Examples | Required Metadata | Retention |
|--------|----------|-------------------|-----------|
| Logs | Application logs, audit logs | `request_id`, `tenant_id`, `actor_id`, `severity` | 90 days hot, 1y cold |
| Metrics | Latency p50/p95/p99, error rate, throughput, queue depth | Service, endpoint, status | 13 months |
| Traces | Distributed traces with span attributes | `trace_id`, span kind, downstream IDs | 30 days |
| Audit Events | Auth, permission change, data export | Actor, resource, action, result | 7 years |

### Required Dashboards
| Dashboard | Owner | Refresh | Trigger Alerts? |
|-----------|-------|---------|------------------|
| Service Golden Signals (latency, traffic, errors, saturation) | Service team | 1 min | Yes |
| Business KPI dashboard (from section 16) | Product | Daily | No |
| Cost & token usage (if AI) | Platform | Hourly | Yes — budget breach |
| Security & audit | Security | 5 min | Yes — anomalous access |

### Alert Catalog (minimum 5)
| Alert | Condition | Severity | Page? | Runbook |
|-------|-----------|----------|-------|---------|
| `service.error.rate.high` | error_rate > 1% over 5 min | Critical | Yes | [link] |
| `service.latency.p95.breach` | p95 > NFR-P02 target for 5 min | High | Yes | [link] |
| `queue.lag.high` | consumer_lag > 10k for 5 min | High | Yes | [link] |
| `auth.failure.spike` | > 100 failures/min from same IP | Medium | No | [link] |
| `cost.budget.breach` | daily cost > 110% budget | High | Yes | [link] |
```

**Instructions:**
- AI Runtime Controls block is mandatory whenever section 13 declares any AI/LLM feature; otherwise mark "N/A".
- Every NFR in section 09 with a numeric SLO must have a matching alert here.
- Observability retention values must satisfy section 10 (Compliance) — e.g., GDPR may demand shorter log retention.

**Validation checklist:**
- [ ] AI Runtime Controls present (or explicit "N/A — no AI features")
- [ ] Model + prompt versioning scheme defined (if AI)
- [ ] Logs, Metrics, Traces, Audit Events tables all populated
- [ ] At least 5 alerts defined, each with severity and runbook link
- [ ] Retention values consistent with section 10 compliance

**Related sections:** 13 (Application Type), 09 (NFRs), 10 (Security & Compliance), 16 (KPIs)

---

## 21 Deployment Constraints, System Boundary and Configuration Surface

> **Purpose:** Production deployment topology, rollback procedure, system boundary (what is and is not this team's responsibility), and the configuration surface that varies per environment / per tenant. Drives infrastructure-as-code and the CI/CD pipeline.

```markdown
## Deployment Constraints, System Boundary and Configuration Surface

### Environment Topology
| Environment | Purpose | Replica Count | Data Class | SLA |
|-------------|---------|----------------|------------|-----|
| dev | Developer integration | 1 | Synthetic | None |
| staging | Pre-prod / UAT | 2 | Anonymized prod snapshot | 99.0% |
| prod | Customer traffic | ≥ 3 (multi-AZ) | Live | from NFR-A01 |
| dr | Disaster recovery | Warm standby | Async replica | RTO from NFR-A02 |

### Deployment Constraints
- **Region constraints:** [e.g., EU data residency — EU-region clusters only]
- **Allowed deployment windows:** [e.g., Tue–Thu 09:00–17:00 IST, never on month-end day]
- **Blue/green vs rolling:** [strategy + traffic shift increments]
- **Database migration policy:** [e.g., expand → migrate → contract; never destructive in single release]
- **Feature flag dependency:** [if any feature must be flag-gated at launch]

### Rollback Procedure
| Step | Action | Owner | Time Budget |
|------|--------|-------|-------------|
| 1 | Halt new traffic via gateway | On-call | < 2 min |
| 2 | Revert deployment to previous immutable version | Release engineer | < 5 min |
| 3 | Roll back schema if a destructive migration ran | DBA | < 15 min |
| 4 | Validate Golden Signals on previous version | On-call | < 10 min |
| 5 | Post-incident note + RCA scheduling | Incident commander | Same day |

### System Boundary and Ownership
| Capability | This Team Owns | External Owner | Interface (cited from §05) |
|------------|----------------|----------------|----------------------------|
| Authentication | No | Identity Platform team | `auth.introspect` |
| Billing | No | Finance Platform | `billing.charge` event |
| Domain logic (UCs in section 06) | Yes | — | — |
| Persistence layer | Yes | — | — |
| Observability collectors | No | Platform team | OTLP gateway |

### Configuration Surface
<!-- REQUIRED: Every per-environment or per-tenant configurable value. -->
| Key | Type | Scope | Default | Notes / Secret? |
|-----|------|-------|---------|------------------|
| `database.url` | string | env | — | Secret — from vault |
| `feature.x.enabled` | bool | env + tenant | false | Flag-served |
| `rate_limit.per_user` | int | tenant | 100 | RPS |
| `ai.model_id` | string | env | `claude-opus-4-7` | from §20 allowlist |
| `region.allowed` | list[string] | tenant | `["eu-west-1"]` | Drives data residency |

### Secrets Inventory
| Secret | Storage | Rotation | Owner |
|--------|---------|----------|-------|
| DB credentials | Vault | 90 days | DBA |
| API keys to integrations | Vault | 180 days | Service team |
| Signing keys | KMS | 365 days | Security |
```

**Instructions:**
- Every integration listed in section 05 must appear in the System Boundary table marked as External Owner.
- Every key in the Configuration Surface must be sourced from either env vars, a config service, or a feature-flag platform — never hardcoded.
- Rollback time budgets must collectively be ≤ NFR-A02 (RTO).

**Validation checklist:**
- [ ] Environment topology covers dev / staging / prod (DR optional but recommended)
- [ ] Rollback procedure defined with owner and time budget per step
- [ ] System boundary lists every external capability with explicit owner
- [ ] Configuration surface lists every per-env / per-tenant variable
- [ ] Secrets inventory is complete (no plaintext secrets anywhere in PRD)

**Related sections:** 03 (Architecture), 05 (Integration Layer), 09 (NFRs — RTO/RPO), 10 (Security)

---

## 22 Code Generation Context

> **Purpose:** The system metadata the code generator needs to produce code that looks like a senior BN engineer wrote it — not invented folder structures, invented error classes, invented log formats. This is what binds the PRD to the active BNAC stack.

```markdown
## Code Generation Context

### Application Language and Service Type
| Dimension | Value | Notes |
|-----------|-------|-------|
| Primary language | Python \| DotNet \| React \| Flutter | Must match section 13 |
| Service type | api \| web \| mobile \| worker \| hybrid | |
| Runtime | [e.g., Python 3.11, .NET 8, Node 20, Flutter 3.x] | |
| Package manager | [pip / poetry / npm / pnpm / dotnet / pub] | |

### BN Code Conventions
<!-- REQUIRED: Cite the binding rule files from the active stack. -->
| Convention | Source File | Applies To |
|------------|-------------|------------|
| Folder structure | `~/.claude/stacks/<stack>/rules/folder-structure.md` | All code |
| Error envelope | `~/.claude/stacks/<stack>/skills/error-handling/SKILL.md` | API responses |
| Log format | `~/.claude/rules/observability.md` | Service logs |
| Naming (files, classes, fns) | `~/.claude/stacks/<stack>/rules/naming.md` | All code |
| Test layout | `~/.claude/stacks/<stack>/skills/<test-skill>/SKILL.md` | Tests |

### Skill Pack Reference
<!-- REQUIRED: List every BNAC skill this PRD's implementation will activate. -->
| Skill | Source | Why Required by This PRD |
|-------|--------|--------------------------|
| `react-http-request` | core | UC-001 issues outbound HTTP |
| `signalr-pattern` | react | Section 17 declares streaming interaction model |
| `pytest-testing` | python | Section 15 testing strategy |
| `use-design-system` | react | Frontend uses BNDS widgets |
| | | |

### Definition of Done (codegen-visible)
- [ ] All Tier-1 sections of this PRD pass critical rules
- [ ] Every UC-XXX has at least one sample scenario (section 17) with concrete values
- [ ] Every state-mutating endpoint has an idempotency contract (section 19)
- [ ] Every NFR with a numeric SLO has a matching alert (section 20)
- [ ] Every integration in section 05 appears in section 21 system-boundary table
- [ ] Test coverage target from section 15 is encoded in the CI quality gate
- [ ] Rollback procedure (section 21) is exercised in staging before prod release
- [ ] Activity log appended to `<project>/.claude/log.md` per BNAC rule

### Code Generation Inputs Resolved
<!-- This block is populated by the pipeline, not by humans. -->
| Input | Resolution Source | Value |
|-------|-------------------|-------|
| Active stack | section 13 Primary Language | [auto] |
| Skill set | section 22 Skill Pack Reference | [auto] |
| Compliance overlays | section 01 + section 10 | [auto] |
| Test framework | section 15 + stack default | [auto] |
```

**Instructions:**
- This section binds the PRD to the active BNAC stack — it is the contract between PRD authoring (section 13) and code generation.
- Every skill in the Skill Pack Reference must exist in the active stack's `skills/` folder.
- Definition of Done items are reflected in the milestone DoD checklists generated by `bnac-task-planner`.

**Validation checklist:**
- [ ] Application language matches section 13 selection
- [ ] BN Code Conventions table cites real, resolvable rule/skill paths
- [ ] Skill Pack Reference is non-empty and every skill exists in the chosen stack
- [ ] Definition of Done checklist is complete and matches BNAC milestone DoD pattern

**Related sections:** 13 (Application Type), 15 (Testing), 05 (Integration), 21 (Deployment & Boundary)

---

*Template version 3.1 — BNAC PRD Pipeline (22-section schema). Run `bnac prd-validate <path>` to check this document against all validation rules.*
