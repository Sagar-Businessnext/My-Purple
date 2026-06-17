# States and Transitions

The 8 pipeline stages from the BN AI Dark Factory contract, plus one `uninitialized` source state and two terminal states.

## State table

| State | Tier | Purpose | Entry guards | Exit guards | Auto-evidence file |
|---|---|---|---|---|---|
| `uninitialized` | source | No pipeline run started for this project | — | `init` invoked | — |
| `spec-intake` | 1 | Stakeholder brief captured (the 22-layer intake) | brief file present | `brief.md` non-empty + author named | `prds/<product>/brief.md` |
| `ai-spec` | 2 | PRD authored from intake via `pag-doc-writer` | brief present | 22-section PRD exists | `prds/<product>/prd-*.md` (multi-file or single-file) |
| `md-files` | 3 | PRD validated; ID registry built; cross-refs resolve | PRD present | `VALIDATION_REPORT.md` status = `PROCEED` (Critical 44/44) | `prds/<product>/VALIDATION_REPORT.md` |
| `code-gen` | 4 | Code generated from PRD via stack-specific developer agents | VALIDATION_REPORT PROCEED + tech spec generated | `project-context/project-structure.md` + generated source present | `project-context/{project-structure,project-tech-stack,implementation-plan}.md` |
| `security` | 5 | Security scan + threat model | code-gen complete | SAST / DAST / secret-scan pass; security-review.md status = PASS | `project/.claude/security-review.md` |
| `acceptance-testing` | 6 | Build + type check + lint + tests + UAT | security pass | `bnac-quality-gate` ✅ on every check; UAT sign-off | `project/.claude/quality-gate-report.md`, `project/.claude/uat-signoff.md` |
| `release-prod` | 7 | Production release with stakeholder GO/NO-GO | quality-gate PASS + `release-approval.md` status = GO | deployment receipt present | `project/.claude/release-approval.md`, `project/.claude/deploy-receipt-<env>.md` |
| `post-release-monitoring` | 8 | Stage-8 streams: KPI evidence + runtime observability | release deployed | KPI evidence stream running for ≥ 1 review cycle | `project/.claude/kpi-evidence/*.md` |
| `released-archived` | terminal | Successful run, archived | post-release-monitoring complete + retention period satisfied | — | — |
| `aborted` | terminal | Run aborted (any tier) | abort invoked with reason | — | `project/.claude/abort-reason.md` |
| `frozen` | suspended | Run paused (operator decision) | freeze invoked | — | — |

`uninitialized` is the source state, `released-archived` and `aborted` are terminal, `frozen` is a suspended state that any non-terminal state can enter and exit.

## Transition table

| # | From | Action | To | Guard summary | Side effect |
|---|---|---|---|---|---|
| T01 | uninitialized | init | spec-intake | Project workspace exists | Create `pipeline-state.md` with new `run_id` |
| T02 | spec-intake | advance ai-spec | ai-spec | brief.md exists + author named | Emit `pipeline.advanced` event |
| T03 | ai-spec | advance md-files | md-files | PRD has 22 sections present | Emit `pipeline.advanced` event |
| T04 | md-files | advance code-gen | code-gen | VALIDATION_REPORT.md status = PROCEED | Trigger tech-spec + plan generation |
| T05 | code-gen | advance security | security | Generated source compiles; quality-gate ✅ on build+type+lint | Schedule security scan |
| T06 | security | advance acceptance-testing | acceptance-testing | security-review.md status = PASS | Trigger full quality-gate run |
| T07 | acceptance-testing | advance release-prod | release-prod | quality-gate-report.md = PASS + uat-signoff.md present + `release-approval.md` status = GO | Trigger deployment |
| T08 | release-prod | advance post-release-monitoring | post-release-monitoring | deploy-receipt present | Start KPI evidence collection (Gap #9 — `bnac-kpi-tracker`) |
| T09 | post-release-monitoring | advance released-archived | released-archived | ≥ 1 KPI review cycle complete + retention met | Mark `run_id` terminal |
| T10 | any non-terminal | rollback `<prev>` | `<prev>` | Operator authorization | Append rollback rationale to state file |
| T11 | any non-terminal | freeze | frozen | — | Record freeze reason and freeze timestamp |
| T12 | frozen | unfreeze | (prior state) | — | Resume from frozen-from state |
| T13 | any non-terminal | abort `<reason>` | aborted | Operator authorization + non-empty reason | Write `abort-reason.md` |
| T14 | terminal (released-archived / aborted) | init | spec-intake (new run) | — | Create new state file with new `run_id`; archive prior |

## Guards in detail

### Guard: VALIDATION_REPORT PROCEED

Used by T04. Pass requires both:

1. File `prds/<product>/VALIDATION_REPORT.md` exists
2. The Summary table contains `Status | PROCEED` (i.e., 44/44 critical PASS + no critical CR failures)

### Guard: quality-gate PASS

Used by T07. Pass requires `project/.claude/quality-gate-report.md` with all four lines:

- Build ✅
- Type check ✅
- Lint ✅ or ⚠️ (warnings allowed)
- Tests ✅

A single ❌ on any of build / type / tests = FAIL.

### Guard: release-approval GO

Used by T07. Pass requires `project/.claude/release-approval.md` with:

- Decision: `GO` (case-sensitive)
- Approver name + role + signoff timestamp populated
- Quality-gate report referenced by hash or path

This is the connection point to **Gap #8** — the stakeholder GO/NO-GO bundle writes this file; the state machine consumes it.

### Guard: KPI evidence stream

Used by T09. Pass requires at least one file in `project/.claude/kpi-evidence/` with a status of `cycle-1-complete`. This is the connection point to **Gap #9** — the KPI tracker writes evidence files; the state machine consumes them.

## Illegal transition policy

Any `(current, action)` pair not in the transition table is rejected. The agent must:

1. Refuse the action
2. Return the list of legal actions from the current state
3. Log the rejection with timestamp + current state + attempted action
4. Not modify the state file

There is no override flag. Rolling back is a separate explicit action (T10).

## Cross-references to other Wave-2 gaps

| Gap | Closure artifact | Consumed by |
|---|---|---|
| #2 (this skill) | `pipeline-state.md` | All operators |
| #7 (cross-LLM review) | `cross-llm-review-<gate>.md` | Optional entry guard on T04 (md-files → code-gen) and T07 (acceptance-testing → release-prod) for projects that enable cross-LLM consensus |
| #8 (GO/NO-GO) | `release-approval.md` | Required entry guard on T07 |
| #9 (KPI tracker) | `kpi-evidence/*.md` | Required entry guard on T09 |
