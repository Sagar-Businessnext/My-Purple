Invoke the **bnac-cross-llm-reviewer** agent to run a consensus-of-two-models review on a critical artifact.

**Agent:** `bnac-cross-llm-reviewer`
**Target:** `$ARGUMENTS` (path to the artifact + `--gate <gate-name>` + optional `--primary <model>` `--secondary <model>`)

## What to do

1. Delegate to the `bnac-cross-llm-reviewer` agent with `$ARGUMENTS`.

2. The agent will:
   - **Read** the `cross-llm-consensus` skill (pairing rules + consensus algorithm)
   - **Read** the artifact under review
   - **Resolve** the model pair from the gate (with operator overrides applied); reject same-model or same-family+tier pairs
   - **Apply** the author / reviewer separation rule
   - **Run** the primary model and secondary model on identical input
   - **Normalize** both outputs into the canonical finding schema
   - **Pairwise match** and **classify** each finding as AGREE / PARTIAL / DISAGREE-A / DISAGREE-B
   - **Compute** verdict — PASS / PASS-WITH-CAVEAT / FAIL — mechanically from the counts
   - **Write** `project/.claude/cross-llm-review-<gate>.md` with summary, classified findings, and both raw outputs as appendices
   - **Print** a short verdict summary

3. After completion, log results to `project/.claude/log.md`.

## Supported gates

| Gate name | Default pair | When to use |
|---|---|---|
| `prd-validation` | opus-4-7 + sonnet-4-6 | After `/bnac-pag-verify` passes; before pipeline T04 |
| `code-review-security` | opus-4-7 + opus-4-6 | Before merging security-critical code |
| `code-review-standard` | sonnet-4-6 + haiku-4-5 | Optional consensus on standard PRs |
| `release-approval` | opus-4-7 + opus-4-6 | Before `/bnac-go-nogo approve` on major releases |
| `state-machine-guard-audit` | sonnet-4-6 + haiku-4-5 | Optional consensus on guard evaluation for pipeline T08 / T09 |

## Examples

```
/bnac-cross-llm-review prds/payment-service/ --gate prd-validation
/bnac-cross-llm-review src/auth/ --gate code-review-security
/bnac-cross-llm-review prds/loan-origination/ --gate prd-validation --primary opus-4-7 --secondary opus-4-6
```

## Why this exists

A single LLM is a single point of failure for critical gates — model bias, prompt drift, or context loss can let real defects through. Running the same artifact through two distinct models catches the cases where one model misses something the other catches. This command closes **gap #7** from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

The verdict is non-blocking by default — it produces a record. To make it a hard gate, wire it as an optional entry guard on pipeline T04 (md-files → code-gen) or T07 (acceptance-testing → release-prod) via the `bnac-pipeline-state-tracker`.

## Cost

Two model calls per review. ~70k tokens in, ~9k out for a typical 22-section PRD. Refuses artifacts > 100k tokens; chunk first.
