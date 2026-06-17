# Consensus Algorithm

How to combine two models' findings into a verdict.

## Step 1 — Normalize findings

Each model produces a list of findings. Normalize into the canonical schema:

| Field | Type | Required |
|---|---|---|
| id | string | Yes — internal to the run (`A-001`, `B-001`); used to track classification |
| severity | enum | Yes — `critical` / `high` / `medium` / `low` / `info` |
| location | string | Yes — `file:line` or section ID (e.g., `06/UC-003 step 4` or `src/payments.ts:142`) |
| description | string | Yes — one line, ≤ 200 chars |
| evidence | string | Yes — quote of the offending text or a precise paraphrase |
| category | enum | Yes — `correctness` / `security` / `performance` / `style` / `compliance` / `traceability` / `other` |

Anything that doesn't fit the schema is dropped with a `dropped-finding` log entry, not silently coerced.

## Step 2 — Pairwise match

For every model-A finding, look for a model-B finding that is a match. A match satisfies all of:

| Field | Match rule |
|---|---|
| location | Exact match (after normalizing relative paths) OR within ±3 lines for `file:line` form |
| category | Same category |
| description | Token-overlap similarity ≥ 0.6 (Jaccard on lowercased descriptions, after stopword removal) OR same `id` pattern (e.g., both flag `BR-007`) |

A model-A finding can match at most one model-B finding; the highest-similarity B-finding wins ties.

## Step 3 — Classify

| Classification | Pairwise outcome | Severity used in verdict |
|---|---|---|
| `AGREE` | Matched; same severity | The (shared) severity |
| `PARTIAL` | Matched; different severity | The **higher** of the two severities |
| `DISAGREE` | Unmatched (found by exactly one model) | The (sole) severity |

## Step 4 — Compute counts

For each severity, compute four totals:

| Severity | AGREE count | PARTIAL count | DISAGREE-A count | DISAGREE-B count |
|---|---|---|---|---|
| critical | N | N | N | N |
| high | N | N | N | N |
| medium | N | N | N | N |
| low | N | N | N | N |
| info | N | N | N | N |

## Step 5 — Verdict

Apply in order; stop at first match:

| # | Condition | Verdict |
|---|---|---|
| 1 | AGREE.critical ≥ 1 OR AGREE.high ≥ 1 | `FAIL` |
| 2 | PARTIAL.critical ≥ 1 OR PARTIAL.high ≥ 1 (treated as the higher severity per Step 3) | `FAIL` |
| 3 | DISAGREE.critical ≥ 1 (from either model) | `PASS-WITH-CAVEAT` (escalate) |
| 4 | DISAGREE.high ≥ 2 (from either model, combined) | `PASS-WITH-CAVEAT` (escalate) |
| 5 | None of the above | `PASS` |

`PASS-WITH-CAVEAT` is the escalation signal — one model found a critical or two highs that the other missed; a human must adjudicate.

## Step 6 — Escalation payload (for PASS-WITH-CAVEAT)

When verdict is `PASS-WITH-CAVEAT`, the record includes an `## Escalation` block listing:

- Which findings need adjudication (the unmatched criticals + highs)
- Which model raised each one
- The matching attempt (the closest model-B finding, if any, and why it did not match)
- Suggested human reviewer (operator-named; default `tech-lead` of the gate's owning team)

## Worked example

Models A (Opus 4.7) and B (Sonnet 4.6) reviewing a PRD.

### Model A findings

| id | severity | location | description |
|---|---|---|---|
| A-001 | critical | 06/UC-005 step 4 | Cites BR-099 not defined in §07 |
| A-002 | high | 19 idempotency table | POST /refunds missing idempotency contract |
| A-003 | medium | 09/NFR-PERF-002 | p95 target lacks measurement tool |

### Model B findings

| id | severity | location | description |
|---|---|---|---|
| B-001 | critical | 06/UC-005 step 4 | BR-099 referenced but undefined |
| B-002 | medium | 19 idempotency table | Refund endpoint lacks Idempotency-Key |
| B-003 | high | 20 alert catalog | NFR-AVAIL-002 has no matching alert |

### Pairwise match

- A-001 ↔ B-001 — same location, same description token-overlap → match
- A-002 ↔ B-002 — same location, same category, description similarity ≥ 0.6 → match
- A-003 — no match
- B-003 — no match

### Classification

| Pair | Classification | Severity used |
|---|---|---|
| A-001 / B-001 | AGREE | critical |
| A-002 / B-002 | PARTIAL | high (A's higher severity wins) |
| A-003 | DISAGREE-A | medium |
| B-003 | DISAGREE-B | high |

### Counts

| Severity | AGREE | PARTIAL | DISAGREE-A | DISAGREE-B |
|---|---|---|---|---|
| critical | 1 | 0 | 0 | 0 |
| high | 0 | 1 | 0 | 1 |
| medium | 0 | 0 | 1 | 0 |

### Verdict

Rule #1 fires: AGREE.critical = 1 → **FAIL**.

The full PRD review record records the FAIL, lists A-001 / B-001 as the blocking AGREE finding, and notes A-002/B-002 (PARTIAL high) plus B-003 (DISAGREE high) as supporting evidence the PRD still needs work.
