---
name: cross-llm-consensus
description: Consensus-of-two-models review protocol for critical gates — runs the same artifact through two distinct models, classifies AGREE / PARTIAL / DISAGREE, surfaces deltas. Used by bnac-cross-llm-reviewer.
user-invocable: false
argument-hint: ""
---

A single LLM reviewing a critical artifact is a single point of failure — model bias, prompt drift, or context-loss can let real defects through. Running the same artifact through two distinct models and reconciling their findings catches the cases where one model misses something the other catches. This skill defines that protocol, closing gap #7 from [v2-vs-v3-comparison.md](../../../../../dark-factory/gap-v2-bn-harness/v2-vs-v3-comparison.md) §8.

**Authoritative source:** This skill body. The per-review record (`project/.claude/cross-llm-review-<gate>.md`) is the per-invocation instance.

## Additional Resources

- [reference/consensus-algorithm.md](reference/consensus-algorithm.md) — how to classify AGREE / PARTIAL / DISAGREE; how to merge findings; thresholds for escalation
- [reference/model-pairing.md](reference/model-pairing.md) — which model pair to use per gate; rationale for distinctness

## Steps

1. **Identify the gate** — PRD validation, code review of security-critical code, release approval, or any operator-specified gate. The gate determines which artifact is reviewed and which finding-classes are surfaced.
2. **Choose the model pair** — see [reference/model-pairing.md](reference/model-pairing.md). Default: primary `claude-opus-4-7`, secondary `claude-sonnet-4-6`. The pair MUST be distinct in family + size; same model called twice does not satisfy this skill.
3. **Run both models on the same artifact with the same instructions** — identical prompt, identical context. Differences in output are signal.
4. **Extract structured findings** from each — every finding has: id, severity (critical / high / medium / low / info), location (file:line or section ID), and a one-line description.
5. **Classify each finding** per [reference/consensus-algorithm.md](reference/consensus-algorithm.md):
   - `AGREE` — both models found the same issue (same severity, same location, same description match within similarity threshold)
   - `PARTIAL` — same issue, different severity OR same location but different description
   - `DISAGREE` — found by exactly one model, not the other
6. **Compute the gate verdict:**
   - **PASS** — both models report zero `critical` and zero `high` findings (`AGREE` zeros on both severities)
   - **PASS-WITH-CAVEAT** — zero AGREE criticals/highs, but ≥ 1 DISAGREE critical OR ≥ 2 DISAGREE highs → escalate for human review; do NOT auto-pass
   - **FAIL** — ≥ 1 AGREE critical OR ≥ 1 AGREE high
7. **Write the consensus record** — `project/.claude/cross-llm-review-<gate>.md` with the full finding table classified, the verdict, both raw model outputs (as appendices for audit), and the timestamp.
8. **Log** to `project/.claude/log.md`.

## Rules

- **The two models MUST be distinct in family or significantly different in size** — Calling the same model twice is not consensus; it is replay. The pair table in [model-pairing.md](reference/model-pairing.md) enforces this.
- **Identical inputs** — Same prompt, same context window, same tool access. Differences must come from the model, not the input.
- **Findings are evidence, not opinions** — Every finding must cite a file:line or section ID. "This feels risky" is not a finding.
- **DISAGREE is not noise — it is the signal this skill exists for** — A DISAGREE critical finding means one model caught something the other missed. Escalate it; do not majority-rules away.
- **Severity is the model's call; classification is the algorithm's call** — The classifier does not re-grade severity. If model A says `critical` and model B says `high`, that is a `PARTIAL` finding at the higher severity (`critical`).
- **The verdict is mechanical, not LLM-decided** — `PASS` / `PASS-WITH-CAVEAT` / `FAIL` is computed from the finding table per the rules above; no third model is called to "judge" the verdict.
- **The verdict is non-blocking by default** — Consensus review produces a record; it does not automatically refuse a downstream gate. Operators wire the verdict into gates explicitly (e.g., as an optional entry guard on pipeline T04 or T07).
- **Audit the raw outputs** — Both raw model outputs are appended to the record verbatim. Without them, the classification cannot be reproduced.
- **Cost is bounded** — Two model calls per gate. No third opinion. If the verdict is ambiguous (`PASS-WITH-CAVEAT`), escalate to a human, not a third model — humans break ties, not LLMs.
