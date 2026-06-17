# Critical Validation Rules — 44 Rules (Must Pass All)

> **Type:** Blocking
> **Count:** 44 rules (34 baseline + 10 added 2026-05-21 for sections 17–22)
> **Policy:** ALL 44 must pass before development can begin. A single failure blocks code generation.

---

## Overview

Critical rules enforce structural completeness, content adequacy, and domain coverage. They are checked by the PRD validator before any pipeline stage runs. No override or bypass is permitted — every critical rule is a hard gate.

---

## Section 01 — Overall Structure

### RULE-001: All Required Sections Present
- **Section:** 01 — Overall Structure
- **Check:** Verify the PRD contains all 22 mandatory sections (numbered 01–22)
- **Pass:** All 22 sections are present with their standard headings
- **Fail:** One or more sections are missing or have non-standard headings

### RULE-002: No Empty Sections
- **Section:** 01 — Overall Structure
- **Check:** Each of the 22 sections contains at least 100 lines of substantive content
- **Pass:** All sections meet or exceed 100 lines of content
- **Fail:** Any section has fewer than 100 lines of content

### RULE-003: No Placeholder Text
- **Section:** 01 — Overall Structure
- **Check:** Sections 01–09 contain no placeholder tokens: `TBD`, `TODO`, `PLACEHOLDER`, `[INSERT]`, `[TBD]`, `[TODO]`
- **Pass:** Zero placeholder tokens found in sections 01–09
- **Fail:** One or more placeholder tokens detected in sections 01–09

---

## Section 02 — Executive Summary

### RULE-201: Product Vision Adequacy
- **Section:** 02 — Executive Summary
- **Check:** The product vision statement contains more than 50 words
- **Pass:** Vision statement word count > 50
- **Fail:** Vision statement is absent or ≤ 50 words

### RULE-202: Quantified Business Objectives
- **Section:** 02 — Executive Summary
- **Check:** At least 3 business objectives are stated with measurable, quantified targets (numbers, percentages, or time-bound goals)
- **Pass:** ≥ 3 objectives with quantified targets are present
- **Fail:** Fewer than 3 quantified objectives, or objectives are qualitative only

### RULE-204: Success Metrics With Targets
- **Section:** 02 — Executive Summary
- **Check:** Success metrics are defined with specific target values (e.g., "reduce churn by 15% within 6 months")
- **Pass:** ≥ 1 success metric with a numeric or time-bound target is present
- **Fail:** No success metrics with targets, or metrics are undefined/vague

---

## Section 04 — Process Flows

### RULE-401: Minimum Process Flows Documented
- **Section:** 04 — Process Flows
- **Check:** At least 3 end-to-end process flows are documented with steps
- **Pass:** ≥ 3 process flows present, each with a sequence of steps
- **Fail:** Fewer than 3 process flows documented

---

## Section 05 — Integration Requirements

### RULE-501: External Integrations Documented
- **Section:** 05 — Integration Requirements
- **Check:** All external systems, APIs, and third-party services are explicitly documented
- **Pass:** At least 1 external integration is documented with name, purpose, and direction (inbound/outbound)
- **Fail:** No integrations documented, or section only contains generic placeholder text

---

## Section 06 — Use Cases

### RULE-601: Minimum Use Cases Defined
- **Section:** 06 — Use Cases
- **Check:** At least 3 detailed use cases are documented
- **Pass:** ≥ 3 use cases present
- **Fail:** Fewer than 3 use cases present

### RULE-602: Use Case ID Format
- **Section:** 06 — Use Cases
- **Check:** Every use case has a unique ID matching the pattern `UC-XXX` (where XXX is a zero-padded 3-digit number)
- **Pass:** All use case IDs match `UC-\d{3}` format and are unique
- **Fail:** Any use case ID is missing, malformed, or duplicated

### RULE-603: Main Flow Step Minimum
- **Section:** 06 — Use Cases
- **Check:** Each use case has a main success flow with at least 5 numbered steps
- **Pass:** Every use case main flow contains ≥ 5 steps
- **Fail:** Any use case main flow has fewer than 5 steps

### RULE-605: Minimum Exception Flows Per Use Case
- **Section:** 06 — Use Cases
- **Check:** Each use case documents at least 2 exception or error flows
- **Pass:** Every use case has ≥ 2 exception flows
- **Fail:** Any use case has fewer than 2 exception flows

### RULE-610: Measurable Success Criteria
- **Section:** 06 — Use Cases
- **Check:** Each use case specifies measurable success criteria (observable, testable outcomes)
- **Pass:** Every use case contains at least 1 measurable success criterion
- **Fail:** Any use case is missing measurable success criteria or criteria are non-testable

---

## Section 07 — Business Rules

### RULE-701: Minimum Business Rules Defined
- **Section:** 07 — Business Rules
- **Check:** At least 10 business rules are documented in this section
- **Pass:** ≥ 10 business rules present
- **Fail:** Fewer than 10 business rules present

### RULE-702: Business Rule ID Format
- **Section:** 07 — Business Rules
- **Check:** Every business rule has a unique ID matching the pattern `BR-XXX` (where XXX is a zero-padded 3-digit number)
- **Pass:** All business rule IDs match `BR-\d{3}` format and are unique
- **Fail:** Any business rule ID is missing, malformed, or duplicated

---

## Section 08 — Data Requirements

### RULE-801: Minimum Entities Defined
- **Section:** 08 — Data Requirements
- **Check:** At least 3 data entities (domain objects, database tables, or data models) are defined
- **Pass:** ≥ 3 entities present
- **Fail:** Fewer than 3 entities defined

### RULE-802: Minimum Attributes Per Entity
- **Section:** 08 — Data Requirements
- **Check:** Each entity has at least 5 attributes documented, each with an explicit data type
- **Pass:** Every entity contains ≥ 5 typed attributes
- **Fail:** Any entity has fewer than 5 attributes, or any attribute is missing its data type

### RULE-805: Security Classification for PII Entities
- **Section:** 08 — Data Requirements
- **Check:** Any entity storing personally identifiable information (PII) must have an explicit security classification and protection mechanism documented
- **Pass:** All PII-containing entities have security classification and protection details
- **Fail:** Any PII entity is missing security classification or protection specification

---

## Section 09 — Non-Functional Requirements (NFRs)

### RULE-901: Minimum NFRs Defined
- **Section:** 09 — Non-Functional Requirements
- **Check:** At least 15 non-functional requirements are documented
- **Pass:** ≥ 15 NFRs present
- **Fail:** Fewer than 15 NFRs present

### RULE-902: NFR Category Coverage
- **Section:** 09 — Non-Functional Requirements
- **Check:** NFRs cover all 5 mandatory categories: Performance, Security, Scalability, Availability, and Usability
- **Pass:** At least 1 NFR exists in each of the 5 mandatory categories
- **Fail:** Any of the 5 mandatory categories has zero NFRs

### RULE-903: Measurable NFR Targets
- **Section:** 09 — Non-Functional Requirements
- **Check:** Each NFR specifies a measurable, quantified target (e.g., "response time < 200ms at p95", "99.9% uptime")
- **Pass:** All NFRs have numeric or time-bound measurable targets
- **Fail:** Any NFR lacks a measurable target or uses vague language like "fast" or "reliable"

---

## Section 10 — Security Requirements

### RULE-1001: Minimum Security Requirements
- **Section:** 10 — Security Requirements
- **Check:** At least 5 explicit security requirements are documented
- **Pass:** ≥ 5 security requirements present
- **Fail:** Fewer than 5 security requirements present

### RULE-1002: Compliance Standards Identified
- **Section:** 10 — Security Requirements
- **Check:** Applicable compliance and regulatory standards (e.g., GDPR, SOC 2, PCI-DSS, ISO 27001) are explicitly identified
- **Pass:** At least 1 compliance standard is named with scope of applicability
- **Fail:** No compliance standards identified, or section only contains generic security boilerplate

### RULE-1003: Encryption Specification
- **Section:** 10 — Security Requirements
- **Check:** Both transport encryption (TLS) and data-at-rest encryption (AES or equivalent) are explicitly specified
- **Pass:** TLS specification and AES (or equivalent) at-rest encryption are both present
- **Fail:** Either TLS or AES at-rest encryption is missing from the specification

---

## Section 12 — Scope Definition

### RULE-1202: In-Scope Features Listed
- **Section:** 12 — Scope Definition
- **Check:** A defined list of in-scope features or capabilities is present
- **Pass:** ≥ 1 explicitly labelled "in-scope" list of features is documented
- **Fail:** No in-scope features list, or scope section only contains narrative text without a feature enumeration

---

## Section 13 — Application Type

### RULE-1301: Application Type Specified
- **Section:** 13 — Application Type
- **Check:** The application type is explicitly declared (e.g., web application, mobile app, API service, desktop app, microservice)
- **Pass:** Application type is named and unambiguous
- **Fail:** Application type is absent or described only in vague terms

### RULE-1302: Architecture Pattern Defined
- **Section:** 13 — Application Type
- **Check:** The primary architecture pattern is defined (e.g., monolith, microservices, event-driven, CQRS, layered/MVC)
- **Pass:** Architecture pattern is explicitly named and described
- **Fail:** No architecture pattern stated, or pattern is implied but not declared

---

## Section 14 — Glossary

### RULE-1401: Minimum Glossary Terms
- **Section:** 14 — Glossary
- **Check:** At least 20 terms are defined in the glossary
- **Pass:** ≥ 20 glossary entries present
- **Fail:** Fewer than 20 glossary entries

### RULE-1402: All Acronyms Expanded
- **Section:** 14 — Glossary
- **Check:** Every acronym used in the PRD appears in the glossary with its full expansion
- **Pass:** All acronyms in the document have a matching glossary entry with full expansion
- **Fail:** Any acronym used in the PRD is missing from the glossary

---

## Section 15 — Testing Strategy

### RULE-1501: Testing Strategy Defined
- **Section:** 15 — Testing Strategy
- **Check:** A testing strategy is documented covering at least the types of testing to be performed (unit, integration, e2e, etc.)
- **Pass:** Testing strategy is present with at least 2 test types described
- **Fail:** No testing strategy present, or section is empty/placeholder

### RULE-1502: Code Coverage Target
- **Section:** 15 — Testing Strategy
- **Check:** A minimum code coverage target of 80% or higher is specified
- **Pass:** Coverage target ≥ 80% is explicitly stated
- **Fail:** No coverage target specified, or target is below 80%

---

## Section 16 — KPIs and Metrics

### RULE-1601: Minimum KPIs Defined
- **Section:** 16 — KPIs and Metrics
- **Check:** At least 10 Key Performance Indicators (KPIs) are defined
- **Pass:** ≥ 10 KPIs present
- **Fail:** Fewer than 10 KPIs present

### RULE-1602: KPI Measurement Methods
- **Section:** 16 — KPIs and Metrics
- **Check:** Each KPI specifies how it will be measured (data source, method, or tool)
- **Pass:** All KPIs include a measurement method
- **Fail:** Any KPI lacks a stated measurement method

### RULE-1604: KPI Target Values With Timeframes
- **Section:** 16 — KPIs and Metrics
- **Check:** Each KPI has a target value and a timeframe for achievement (e.g., "reduce MTTR to < 1hr within Q2 2025")
- **Pass:** All KPIs have both a numeric/measurable target value and an associated timeframe
- **Fail:** Any KPI is missing a target value or a timeframe

---

## Section 17 — Sample Scenarios and Interaction Model

### RULE-1701: Sample Scenarios For Critical/High Use Cases
- **Section:** 17 — Sample Scenarios and Interaction Model
- **Check:** Every use case marked Critical or High in section 06 has at least one sample scenario with non-placeholder concrete Input, Steps, Output, Postconditions
- **Pass:** ≥ 1 scenario per Critical/High UC with all four fields populated
- **Fail:** Any Critical/High UC has zero scenarios, or scenarios contain placeholder tokens in Input/Output blocks

### RULE-1702: Interaction Model Row Per Use Case
- **Section:** 17 — Sample Scenarios and Interaction Model
- **Check:** The Interaction Model table contains one row per UC from section 06 specifying interaction style, channel, and turn-taking rule
- **Pass:** Every UC-XXX from section 06 appears in the table
- **Fail:** One or more UCs missing from the interaction model table

---

## Section 18 — State Machine Definition

### RULE-1801: State Machine When Required
- **Section:** 18 — State Machine Definition
- **Check:** If any entity in section 08 declares more than 2 distinct lifecycle states, a state machine is defined for it
- **Pass:** Every stateful entity has a corresponding `State Machine:` block
- **Fail:** A stateful entity is referenced but has no state machine, OR section is empty when it should not be

### RULE-1802: Transitions Have Guards and Terminal States Marked
- **Section:** 18 — State Machine Definition
- **Check:** For each defined state machine, every transition row has From / Event / To / Guard / Actor, and terminal states are explicitly listed
- **Pass:** All transition rows complete; terminal states declared
- **Fail:** Any transition row is incomplete OR terminal states not identified

---

## Section 19 — Failure Modes, Concurrency and Idempotency

### RULE-1901: Minimum Failure Modes Documented
- **Section:** 19 — Failure Modes, Concurrency and Idempotency
- **Check:** At least 5 FAIL-XXX entries are defined with Detection, Expected Behavior, Recovery, and Visible To fields
- **Pass:** ≥ 5 FAIL-XXX entries fully populated
- **Fail:** Fewer than 5 entries, or any entry missing required fields

### RULE-1902: Idempotency Contract For Mutating Endpoints
- **Section:** 19 — Failure Modes, Concurrency and Idempotency
- **Check:** Every state-mutating endpoint declared in section 08 Input Schema has an idempotency-contract row with key source, TTL, and duplicate behavior
- **Pass:** All mutating endpoints have idempotency rows
- **Fail:** One or more mutating endpoints lack an idempotency contract

---

## Section 20 — Governance, AI Guardrails and Observability

### RULE-2001: AI Runtime Controls When AI Declared
- **Section:** 20 — Governance, AI Guardrails and Observability
- **Check:** If section 13 declares any AI/LLM feature, AI Runtime Controls and AI Model & Prompt Versioning tables are populated; otherwise the section explicitly states "N/A — no AI features"
- **Pass:** Either both AI tables populated (when AI present) or explicit N/A note (when absent)
- **Fail:** AI feature declared but controls absent or partial

### RULE-2002: Observability Coverage
- **Section:** 20 — Governance, AI Guardrails and Observability
- **Check:** All four observability tables (Logs, Metrics, Traces, Audit Events) contain at least one row, and at least 5 alerts are defined with severity and runbook link
- **Pass:** All four tables non-empty AND ≥ 5 alerts present
- **Fail:** Any table empty OR fewer than 5 alerts

---

## Section 21 — Deployment, System Boundary and Configuration Surface

### RULE-2101: Rollback Procedure With Time Budgets
- **Section:** 21 — Deployment, System Boundary and Configuration Surface
- **Check:** Rollback procedure has at least 3 steps, each with Action / Owner / Time Budget, and the sum of time budgets is ≤ the RTO declared in section 09 (NFR-A02)
- **Pass:** ≥ 3 steps, all fields present, total ≤ RTO
- **Fail:** Fewer than 3 steps, missing fields, or total time budget exceeds RTO

### RULE-2102: System Boundary Lists Every Integration
- **Section:** 21 — Deployment, System Boundary and Configuration Surface
- **Check:** Every integration documented in section 05 appears as a row in the System Boundary table with explicit External Owner
- **Pass:** All section-05 integrations present in the system-boundary table
- **Fail:** One or more integrations missing or marked owned by "this team"

---

## Section 22 — Code Generation Context

### RULE-2201: Skill Pack Reference Resolves
- **Section:** 22 — Code Generation Context
- **Check:** Every skill listed in the Skill Pack Reference table exists in the active stack's `skills/` folder (resolved from section 13 Primary Language)
- **Pass:** All skill names resolve to real skill folders
- **Fail:** One or more skill names do not resolve, or the table is empty

---

## Enforcement

- The PRD validator runs all 44 critical rules before any code generation step.
- A single critical failure stops the pipeline immediately with a `BLOCKED` status.
- The failure report lists each failing rule ID, the section, and the specific content that caused the failure.
- No override flag, skip parameter, or manual approval can bypass critical rule failures.
- Fix the PRD content and re-submit to the validator.
