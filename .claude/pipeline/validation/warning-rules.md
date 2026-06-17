# Warning Validation Rules — 31 Rules (Recommended)

> **Type:** Non-blocking
> **Count:** 31 rules (25 baseline + 6 added 2026-05-21 for sections 17–22)
> **Policy:** Failures do not block code generation but lower the Overall Score and reduce pipeline confidence. Each warning is a concrete recommendation to improve PRD quality.

---

## Overview

Warning rules enforce best-practice completeness beyond the critical baseline. A PRD can pass all critical rules and still have significant gaps in clarity, traceability, and design specificity. Warning rules surface those gaps so teams can address them before development starts — not after.

Warnings contribute 20% of the Overall Score. Projects with many unresolved warnings tend to accumulate rework during implementation.

---

## Section 01 — Document Information

### RULE-102: Stakeholder Coverage
- **Section:** 01 — Document Information
- **Check:** At least 3 stakeholders are identified by name, role, or team
- **Pass:** ≥ 3 stakeholders listed with name or role
- **Fail:** Fewer than 3 stakeholders identified, or stakeholder list is missing

### RULE-103: Document Version Present
- **Section:** 01 — Document Information
- **Check:** A document version number is present (e.g., `v1.0`, `1.2.0`, `Draft 3`)
- **Pass:** Version number present in document header or metadata block
- **Fail:** No version number found in document information section

---

## Section 02 — Executive Summary

### RULE-203: Key Capabilities List
- **Section:** 02 — Executive Summary
- **Check:** At least 5 key capabilities or differentiating features are listed
- **Pass:** ≥ 5 key capabilities enumerated
- **Fail:** Fewer than 5 key capabilities listed, or capabilities section is absent

---

## Section 03 — Architecture Overview

### RULE-302: Architecture Diagram Present
- **Section:** 03 — Architecture Overview
- **Check:** An architecture diagram, diagram reference, or diagram description (C4, block diagram, sequence diagram) is present
- **Pass:** At least 1 diagram or diagram reference is present (inline Mermaid, PlantUML, image link, or detailed description)
- **Fail:** No diagram or diagram reference in the architecture section

### RULE-303: Component Descriptions
- **Section:** 03 — Architecture Overview
- **Check:** Each named architectural component has a brief description of its responsibility
- **Pass:** All components named in the architecture section have at least 1 sentence describing their role
- **Fail:** Any component is named without a description

---

## Section 04 — Process Flows

### RULE-402: Flow Diagrams Present
- **Section:** 04 — Process Flows
- **Check:** Each process flow includes a diagram, diagram reference, or a step-by-step visual description
- **Pass:** ≥ 1 diagram or structured visual description per flow
- **Fail:** Any process flow has no diagram or structured step-by-step description

### RULE-403: Success Criteria Per Flow
- **Section:** 04 — Process Flows
- **Check:** Each process flow documents its success criteria (what defines a successful execution of the flow)
- **Pass:** Every process flow has at least 1 success criterion
- **Fail:** Any process flow is missing success criteria

---

## Section 05 — Integration Requirements

### RULE-502: API Endpoints Specified
- **Section:** 05 — Integration Requirements
- **Check:** For each external integration, at least the primary API endpoint(s) or interface contract is specified
- **Pass:** Every documented integration includes at least 1 endpoint, URL pattern, or interface contract
- **Fail:** Any integration is documented without an endpoint or interface specification

### RULE-503: Integration Error Handling Defined
- **Section:** 05 — Integration Requirements
- **Check:** Error handling strategy is defined for each external integration (timeout, retry, fallback, or circuit-breaker approach)
- **Pass:** Every integration has an error handling strategy described
- **Fail:** Any integration lacks an error handling specification

---

## Section 06 — Use Cases

### RULE-604: Minimum Alternative Flows Per Use Case
- **Section:** 06 — Use Cases
- **Check:** Each use case documents at least 2 alternative flows (valid alternative paths that do not represent errors)
- **Pass:** Every use case has ≥ 2 alternative flows
- **Fail:** Any use case has fewer than 2 alternative flows

### RULE-606: Actors Defined
- **Section:** 06 — Use Cases
- **Check:** Each use case explicitly identifies all participating actors (users, systems, or external entities)
- **Pass:** Every use case lists its actors
- **Fail:** Any use case is missing actor identification

### RULE-607: Preconditions and Postconditions
- **Section:** 06 — Use Cases
- **Check:** Each use case documents both preconditions (what must be true before the flow starts) and postconditions (what is true after the flow completes)
- **Pass:** Every use case has at least 1 precondition and 1 postcondition
- **Fail:** Any use case is missing preconditions or postconditions

### RULE-608: Business Rules Referenced in Use Cases
- **Section:** 06 — Use Cases
- **Check:** Use cases that apply business rules reference them by `BR-XXX` ID
- **Pass:** All business-rule-applying steps in use cases contain at least 1 `BR-XXX` reference
- **Fail:** Any use case step that enforces a business rule does not cite a `BR-XXX` ID

### RULE-609: Data Elements Specified
- **Section:** 06 — Use Cases
- **Check:** Each use case identifies the key data elements it reads, creates, or modifies
- **Pass:** Every use case lists relevant data elements or entities
- **Fail:** Any use case has no data element specification

---

## Section 07 — Business Rules

### RULE-703: All Six Rule Components Present
- **Section:** 07 — Business Rules
- **Check:** Each business rule documents all 6 standard components: ID, Name, Description, Rationale, Enforcement Point, and Exceptions
- **Pass:** Every business rule contains all 6 components
- **Fail:** Any business rule is missing one or more of the 6 components

### RULE-704: Priority Assigned to Business Rules
- **Section:** 07 — Business Rules
- **Check:** Each business rule has a priority level assigned (e.g., Critical, High, Medium, Low)
- **Pass:** All business rules have an explicit priority level
- **Fail:** Any business rule is missing a priority assignment

---

## Section 08 — Data Requirements

### RULE-803: Entity Relationships Documented
- **Section:** 08 — Data Requirements
- **Check:** Relationships between entities are documented (one-to-many, many-to-many, etc.)
- **Pass:** At least the primary inter-entity relationships are described, including cardinality
- **Fail:** No entity relationships documented, or all entities are described in isolation

### RULE-804: Storage Strategy Defined
- **Section:** 08 — Data Requirements
- **Check:** The data storage strategy is defined (e.g., relational database, document store, event store, data warehouse) with a rationale
- **Pass:** At least 1 storage technology or approach is named with a brief rationale
- **Fail:** No storage strategy described

---

## Section 09 — Non-Functional Requirements

### RULE-904: Monitoring Strategy for NFRs
- **Section:** 09 — Non-Functional Requirements
- **Check:** A monitoring and alerting strategy is described to ensure NFR targets are met in production
- **Pass:** Monitoring approach is documented for at least the Performance and Availability NFR categories
- **Fail:** No monitoring strategy present in the NFR section

---

## Section 11 — User Personas

### RULE-1101: Minimum Personas Defined
- **Section:** 11 — User Personas
- **Check:** At least 3 user personas are defined
- **Pass:** ≥ 3 personas present, each with a name and role description
- **Fail:** Fewer than 3 personas defined

### RULE-1102: Primary Persona Identified
- **Section:** 11 — User Personas
- **Check:** One persona is explicitly designated as the primary persona (the main user the product is designed for)
- **Pass:** Exactly 1 persona is labelled as primary or identified as the primary user
- **Fail:** No persona is designated as primary, or multiple personas are marked primary without differentiation

---

## Section 12 — Scope Definition

### RULE-1201: Constraints Documented
- **Section:** 12 — Scope Definition
- **Check:** At least 3 project constraints are documented (technical, budget, regulatory, timeline, or resource constraints)
- **Pass:** ≥ 3 constraints present
- **Fail:** Fewer than 3 constraints documented

### RULE-1203: Out-of-Scope Features Listed
- **Section:** 12 — Scope Definition
- **Check:** Features and capabilities explicitly excluded from this release are listed
- **Pass:** ≥ 1 out-of-scope item is explicitly stated
- **Fail:** No out-of-scope items listed; scope only describes what is included

---

## Section 14 — Glossary

### RULE-1403: Technical Terms Defined
- **Section:** 14 — Glossary
- **Check:** Technology-specific or platform-specific terms used in the PRD are defined in the glossary
- **Pass:** All technical terms that are non-obvious to a business reader have glossary entries
- **Fail:** Technical terms are used without definition; a non-technical reader cannot understand key sections

### RULE-1404: Business Terms Defined
- **Section:** 14 — Glossary
- **Check:** Domain-specific or company-specific business terms used in the PRD are defined in the glossary
- **Pass:** All business domain terms specific to the organisation or industry have glossary entries
- **Fail:** Business domain terms are used without definition; a new team member cannot understand key sections

---

## Section 17 — Sample Scenarios

### RULE-1703: Edge / Negative Scenarios Coverage
- **Section:** 17 — Sample Scenarios and Interaction Model
- **Check:** At least 3 edge or negative scenarios listed, each linked to a FAIL-XXX from section 19 or a BR-XXX from section 07
- **Pass:** ≥ 3 edge scenarios with explicit references
- **Fail:** Fewer than 3 edge scenarios, or references missing

---

## Section 18 — State Machine Definition

### RULE-1803: State Machine Diagram Present
- **Section:** 18 — State Machine Definition
- **Check:** Each defined state machine has either an ASCII diagram or a transition matrix in addition to the table
- **Pass:** All state machines include a visual / matrix representation
- **Fail:** One or more state machines lack a diagram or matrix

---

## Section 19 — Failure Modes, Concurrency and Idempotency

### RULE-1903: Retry & Backoff Policy Documented
- **Section:** 19 — Failure Modes, Concurrency and Idempotency
- **Check:** Retry & Backoff Policy block lists retryable codes, non-retryable codes, backoff strategy, and max attempts
- **Pass:** All four sub-fields populated
- **Fail:** Any sub-field missing or vague (e.g., "exponential" without parameters)

---

## Section 20 — Governance, AI Guardrails and Observability

### RULE-2003: Alert Per NFR With Numeric SLO
- **Section:** 20 — Governance, AI Guardrails and Observability
- **Check:** Every NFR in section 09 with a numeric SLO has a matching alert in the Alert Catalog
- **Pass:** All numeric-SLO NFRs have a corresponding alert
- **Fail:** One or more numeric-SLO NFRs have no alert defined

---

## Section 21 — Deployment, System Boundary and Configuration Surface

### RULE-2103: Configuration Surface Completeness
- **Section:** 21 — Deployment, System Boundary and Configuration Surface
- **Check:** Configuration Surface table includes Key, Type, Scope, Default, and Secret-flag columns populated for every per-env or per-tenant variable
- **Pass:** All rows fully populated; no plaintext secret values
- **Fail:** Any row missing fields, or a Secret-flag value is contradicted by a plaintext default

---

## Section 22 — Code Generation Context

### RULE-2202: Definition Of Done Checklist Complete
- **Section:** 22 — Code Generation Context
- **Check:** Definition of Done checklist includes (a) per-UC sample scenario, (b) idempotency contract, (c) alert per SLO NFR, (d) integration → system-boundary mapping, (e) test coverage gate, (f) activity-log append
- **Pass:** All six DoD items present
- **Fail:** One or more DoD items missing

---

## Scoring Impact

Warning rules contribute 20% of the Overall Score (see `cross-reference.md` for the formula). Resolving all 31 warning rules improves the Overall Score by up to 20 percentage points and directly increases the confidence level of the generated pipeline output.

Each unresolved warning is included in the validation report with a recommended remediation action. Warnings are never promoted to critical failures at a later gate — but they are surfaced again at the code-review and quality-gate stages if the relevant implementation artefact cannot be traced back to a PRD specification.
