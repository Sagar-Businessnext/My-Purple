# Model Pairing per Gate

Which two models to use for each cross-LLM review gate, and why the pair must be distinct.

## Pairing principle

The point of consensus is to surface findings one model missed. Two calls to the same model do not satisfy this — they are replay, not review. Pairs must differ in **family or significantly in capability tier**. Same family + same tier is rejected by the agent as a misconfiguration.

## Default pairs by gate

| Gate | Primary | Secondary | Rationale |
|---|---|---|---|
| PRD validation (T04 entry) | `claude-opus-4-7` | `claude-sonnet-4-6` | Opus catches structural / cross-reference gaps; Sonnet's faster scan catches surface-level inconsistencies missed when Opus over-summarizes |
| Code review — security-critical | `claude-opus-4-7` | `claude-opus-4-6` | Two recent Opus releases; cross-version catches regressions in security-sensitive reasoning between training cuts |
| Code review — standard | `claude-sonnet-4-6` | `claude-haiku-4-5` | Cheaper pair; appropriate for non-security code paths where the cost-of-miss is lower |
| Release approval (T07 entry, optional) | `claude-opus-4-7` | `claude-opus-4-6` | High-stakes; same as security-critical |
| State-machine guard audit (T08 / T09 entry, optional) | `claude-sonnet-4-6` | `claude-haiku-4-5` | Lower stakes; gates the downstream consumers, not the release itself |

## Operator override

Operators may pass `--primary <model>` and `--secondary <model>` to override the defaults. The agent enforces:

1. Both must be in the allowed model list (`claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`)
2. They must not be the same model ID
3. They should not be the same model family + size (e.g., `claude-opus-4-6` paired with `claude-opus-4-6` is rejected as identical; `claude-opus-4-7` paired with `claude-opus-4-6` is allowed because the version differs)

## When NOT to run cross-LLM review

| Scenario | Reason |
|---|---|
| Low-stakes scratch work | Cost-of-miss is low; one model is sufficient |
| Already-PASS gates with no recent code change | Re-running consensus on unchanged input wastes tokens |
| The reviewing model and the authoring model would be the same | Author bias — if Opus 4.7 wrote the PRD, do not let Opus 4.7 be one of the two reviewers; substitute Sonnet 4.6 + Opus 4.6 |

## Author / reviewer separation

The reviewer pair must NOT include the model that authored the artifact being reviewed. If Opus 4.7 wrote the PRD, the review pair becomes Sonnet 4.6 + Opus 4.6. The agent reads the artifact's `Generated-By:` frontmatter (if present) to enforce this; if the field is missing, the agent warns but proceeds.

## Token budget

Two model calls per review. For a 22-section PRD (~30k tokens), expect:

| Model | Tokens in | Tokens out | Approx cost |
|---|---|---|---|
| Opus 4.7 | 30k | 5k | high |
| Sonnet 4.6 | 30k | 4k | medium |

Total per review: ~70k tokens in, ~9k out. Operators should not invoke cross-LLM review on artifacts > 100k tokens without first chunking them; the agent refuses oversized inputs by default.

## Pair stability

A given gate should use the same pair across consecutive runs unless an operator explicitly changes the pair. Switching pairs mid-project produces noisy false-positive `DISAGREE` findings (one pair found something a new pair does not, but it's a model difference, not a real change). The agent records the pair in the consensus record so this is auditable.
