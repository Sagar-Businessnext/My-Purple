# Cross-Reference Validation

> **Type:** Consistency checks
> **Policy:** Cross-reference failures are reported as warnings unless they indicate a dangling reference (a reference to a non-existent ID), which is treated as a critical failure.

---

## Overview

Cross-reference validation checks consistency *across* PRD sections. A PRD can satisfy every within-section rule and still contain contradictions — a use case that cites a business rule that does not exist, or a KPI with no link to any stated objective. Cross-reference checks catch those gaps before they become defects in generated code.

---

## CR-001: Use Case → Business Rule References

**Check:** Every `BR-XXX` identifier cited within a use case step must exist as a defined business rule in Section 07.

**How to verify:**
1. Extract all `BR-\d{3}` tokens from Section 06 (Use Cases).
2. Extract all `BR-\d{3}` IDs defined in Section 07 (Business Rules).
3. Confirm every cited BR ID exists in the Section 07 set.

**Pass:** All BR references in use cases resolve to a defined business rule in Section 07.

**Fail (Critical):** Any `BR-XXX` cited in a use case does not exist in Section 07. This is a dangling reference — the generated code would enforce a rule with no specification.

**Remediation:** Either add the missing business rule to Section 07 or remove the dangling reference from the use case.

---

## CR-002: Use Case → Security Requirement References

**Check:** Every `NFR-SEC-XXX` identifier cited within a use case must exist as a defined security requirement in Section 10.

**How to verify:**
1. Extract all `NFR-SEC-\d{3}` tokens from Section 06 (Use Cases).
2. Extract all security requirement IDs defined in Section 10 (Security Requirements).
3. Confirm every cited NFR-SEC ID exists in the Section 10 set.

**Pass:** All NFR-SEC references in use cases resolve to a defined security requirement in Section 10.

**Fail (Critical):** Any `NFR-SEC-XXX` cited in a use case does not exist in Section 10. Dangling security references are blocking — a security gap cannot be inferred from context.

**Remediation:** Add the missing security requirement to Section 10 or correct the reference in the use case.

---

## CR-003: Process Flow → Use Case Traceability

**Check:** Each process flow documented in Section 04 must map to at least one use case in Section 06.

**How to verify:**
1. List all process flows from Section 04.
2. Check each flow for an explicit reference to a `UC-XXX` ID, or verify that the flow's name or purpose matches a use case title.
3. Every flow must be traceable to ≥ 1 use case.

**Pass:** All process flows reference at least 1 use case by `UC-XXX` ID or by unambiguous name match.

**Fail (Warning):** Any process flow has no traceability to a use case. This indicates undocumented functionality — the flow describes behaviour not captured in the use case model.

**Remediation:** Add a `UC-XXX` reference to the process flow, or create a new use case that covers the flow's behaviour.

---

## CR-004: Use Case → Entity References

**Check:** Every data entity referenced within a use case must be defined in Section 08 (Data Requirements).

**How to verify:**
1. Extract entity names and references from Section 06 use case descriptions, data elements, and step descriptions.
2. Extract entity names defined in Section 08.
3. Each entity referenced in a use case must appear in Section 08.

**Pass:** All entity references in use cases resolve to a defined entity in Section 08.

**Fail (Warning):** Any entity referenced in a use case is not defined in Section 08. Undefined entities produce gaps in the data model.

**Remediation:** Add the missing entity definition to Section 08 or correct the entity name reference in the use case.

---

## CR-005: Persona Access Levels → Use Case Actors

**Check:** Personas defined in Section 11 must align with the actor roles declared in Section 06 use cases. Every persona must appear as an actor in at least one use case, and every use case actor must correspond to a defined persona or external system.

**How to verify:**
1. Extract persona names and roles from Section 11.
2. Extract actor names from all use cases in Section 06.
3. Match persona names to actor names (case-insensitive, allowing for minor label variation).
4. Flag any persona with zero use case appearances, and any actor with no matching persona or identified external system.

**Pass:** Every persona appears as an actor in ≥ 1 use case; every use case actor maps to a persona or a documented external system.

**Fail (Warning):** Any persona is not represented in any use case (orphaned persona), or any actor has no corresponding persona definition.

**Remediation:** Update use case actors to match persona names, or add missing personas to Section 11.

---

## CR-006: KPI → Business Objective Traceability

**Check:** Each KPI defined in Section 16 should reference or be traceable to at least one business objective from Section 02.

**How to verify:**
1. Extract business objective IDs or titles from Section 02.
2. For each KPI in Section 16, check for an explicit objective reference (objective ID, quote, or paraphrase).
3. Every KPI should be linkable to ≥ 1 business objective.

**Pass:** All KPIs reference at least 1 business objective from Section 02 (directly or by clear derivation).

**Fail (Warning):** Any KPI has no stated connection to a business objective. Unmeasured objectives and disconnected KPIs are a governance risk.

**Remediation:** Add an explicit reference to the related business objective in each KPI definition, or add a new objective to Section 02 that the KPI supports.

---

## CR-007: NFR Categories → Architecture Components

**Check:** The NFR categories defined in Section 09 should cover the architectural components described in Section 03. Each major component should have at least one NFR that governs its behaviour.

**How to verify:**
1. List all named architectural components from Section 03.
2. For each component, check Section 09 for NFRs that reference or apply to that component.
3. Components with no applicable NFR are flagged.

**Pass:** Every major architectural component has ≥ 1 applicable NFR in Section 09.

**Fail (Warning):** Any architectural component has no governing NFR. Un-governed components introduce undefined quality expectations that become defects in production.

**Remediation:** Add NFRs in Section 09 for each ungoverned component, or explicitly note that the component inherits NFRs from a parent system.

---

## CR-008: Sample Scenarios → Use Case References

**Check:** Every sample scenario in Section 17 cites a `UC-XXX` that exists in Section 06, and every Critical/High use case in Section 06 has at least one sample scenario in Section 17.

**How to verify:**
1. Extract `UC-\d{3}` tokens cited as scenario headers in Section 17.
2. Extract all UC IDs from Section 06 and their priority.
3. Confirm every Section-17 UC reference resolves to a defined UC.
4. Confirm every Critical/High UC has ≥ 1 scenario block.

**Pass:** All scenario→UC citations resolve AND every Critical/High UC has coverage.

**Fail (Warning):** Dangling UC reference in Section 17, OR a Critical/High UC has no scenario coverage.

**Remediation:** Add the missing scenario, or correct the UC ID in the scenario header.

---

## CR-009: State Machine → Entity References

**Check:** Each state machine in Section 18 declares an "Owner Entity" that is defined in Section 08 (Data Requirements).

**How to verify:**
1. Extract every `Owner Entity:` value from Section 18 state-machine blocks.
2. Extract entity names defined in Section 08.
3. Each owner entity must resolve to a Section 08 entity.

**Pass:** Every state machine's owner entity exists in Section 08.

**Fail (Warning):** A state machine owner entity is not defined in Section 08.

**Remediation:** Add the entity to Section 08 or correct the owner-entity reference.

---

## CR-010: State Machine Guards → Business Rule References

**Check:** Every transition guard in Section 18 that cites `BR-XXX` resolves to a business rule defined in Section 07.

**How to verify:**
1. Extract `BR-\d{3}` tokens from the Guard column of every state-machine transition table.
2. Extract `BR-\d{3}` IDs defined in Section 07.
3. Confirm every cited guard exists in the Section 07 set.

**Pass:** All transition-guard BR references resolve.

**Fail (Warning):** A transition guard cites a non-existent BR.

**Remediation:** Define the BR in Section 07 or correct the transition guard reference.

---

## CR-011: Idempotency Contract → Input Schema Endpoints (CRITICAL)

**Check:** Every state-mutating endpoint declared in Section 08 (Input Schema) has a row in the Section 19 Idempotency Contract table, and every endpoint in the idempotency table exists in Section 08.

**How to verify:**
1. Extract endpoint identifiers (e.g., `POST /resource`) from Section 08 Input Schema.
2. Extract endpoint identifiers from Section 19 Idempotency Contract.
3. Confirm bidirectional coverage for mutating verbs (POST / PUT / PATCH / DELETE) and emitted events.

**Pass:** Every mutating endpoint in Section 08 has an idempotency row, and every Section 19 row maps to a real Section 08 endpoint.

**Fail (Critical):** Mutating endpoint with no idempotency contract OR idempotency row referencing a non-existent endpoint.

**Remediation:** Add the missing idempotency row to Section 19 or define the endpoint in Section 08.

---

## CR-012: System Boundary → Integration References (CRITICAL)

**Check:** Every integration documented in Section 05 appears as a row in Section 21's System Boundary table with explicit External Owner, and no Section 21 system-boundary row references an integration absent from Section 05.

**How to verify:**
1. Extract integration names from Section 05 (inbound/outbound APIs, third-party services).
2. Extract Capability + Interface columns from Section 21's System Boundary table.
3. Confirm bidirectional mapping.

**Pass:** Every Section 05 integration appears in Section 21 with External Owner ≠ "this team", and vice versa.

**Fail (Critical):** Integration listed in Section 05 but missing from Section 21 boundary OR Section 21 row referencing a non-existent integration.

**Remediation:** Reconcile the integration list — add the missing row or remove the orphan.

---

## CR-013: Skill Pack Reference → Active Stack (CRITICAL)

**Check:** Every skill listed in Section 22's Skill Pack Reference resolves to a real skill folder in the active stack (resolved from Section 13 Primary Language → `~/.claude/stacks/<stack>/skills/<skill-name>/SKILL.md` or `~/.claude/core/skills/<skill-name>/SKILL.md`).

**How to verify:**
1. Read Section 13 Primary Language to determine active stack.
2. Extract skill names from Section 22 Skill Pack Reference table.
3. For each skill, check existence in `stacks/<active>/skills/<name>/` or `core/skills/<name>/`.

**Pass:** Every skill name resolves to a real skill folder.

**Fail (Critical):** Any skill name does not resolve.

**Remediation:** Correct the skill name, install the missing skill, or switch to an alternative skill that exists in the active stack.

---

## CR-014: Alert Catalog → NFR Numeric SLOs

**Check:** Every NFR in Section 09 with a numeric SLO target has a matching alert in Section 20's Alert Catalog.

**How to verify:**
1. Extract NFRs from Section 09 where the Target column contains a numeric value (e.g., `< 300ms`, `99.9%`, `< 0.1%`).
2. Extract alerts from Section 20 Alert Catalog and their Condition values.
3. Match by NFR ID reference, metric name, or component.

**Pass:** Every numeric-SLO NFR has a matching alert.

**Fail (Warning):** Numeric-SLO NFR with no alert defined.

**Remediation:** Add an alert in Section 20 referencing the NFR ID, OR drop the numeric SLO if it is not operationally enforceable.

---

## Scoring Formula

The BNAC PRD validator computes three scores after running all critical and warning rules plus cross-reference checks.

### Critical Score
```
Critical Score = (Critical Rules Passed / 44) x 100
```
Represents structural completeness. Must reach 100% for the pipeline to proceed.

### Warning Score
```
Warning Score = (Warning Rules Passed / 31) x 100
```
Represents best-practice coverage and PRD quality above the baseline.

### Overall Score
```
Overall Score = (Critical Score x 0.8) + (Warning Score x 0.2)
```
The weighted composite score. Critical quality drives 80% of the result; warning quality contributes 20%.

---

## Status Thresholds

| Overall Score | Status | Meaning |
|---------------|--------|---------|
| 95 – 100% | **Excellent** | PRD is production-ready. Pipeline proceeds with full confidence. |
| 85 – 94% | **Good** | PRD is solid. Minor gaps exist but do not block generation. Review warnings before sprint start. |
| 70 – 84% | **Acceptable** | PRD has notable gaps. Pipeline proceeds but generated artefacts may require manual review. Resolve warnings before implementation. |
| 50 – 69% | **Needs Work** | PRD has significant quality gaps. Technical leads should review and improve the PRD before proceeding. |
| < 50% | **Incomplete** | PRD is not ready for development. Substantial content is missing or inadequate. Return to author for major revision. |

---

## Hard Gate

**All 44 critical rules MUST pass regardless of the Overall Score.**

A PRD with an Overall Score of 97% but a single critical failure is **BLOCKED**. The Overall Score is not used to override or compensate for critical failures. Critical rules are individually evaluated — no averaging, no weighting, no bypass.

The pipeline emits a `BLOCKED` status if any of the following conditions are true:
- Any critical rule fails (RULE-001 through RULE-2201)
- Any critical dangling reference is found (CR-001, CR-002, CR-011, CR-012, or CR-013 failure)
- The Critical Score is less than 100%

The pipeline emits a `PROCEED` status only when:
- All 44 critical rules pass (Critical Score = 100%)
- No critical dangling references exist
- The Overall Score is computed and attached to the validation report

Warning failures and non-critical cross-reference failures are included in the report but do not change `PROCEED` to `BLOCKED`.
