Invoke the **bnac-developer** agent to orchestrate the full PRD-to-project generation pipeline.

**Agent:** `bnac-developer`
**Target:** `$ARGUMENTS` (path to PRD folder containing validated 22-section PRD)

## What to do

1. Read context: `~/.claude/CLAUDE.md` → project `CLAUDE.md` → `SUMMARY.md` → `milestone-status.md`

2. Locate the PRD folder:
   - If `$ARGUMENTS` is a folder path → use that folder
   - If no arguments → look for `./prds/` or `./functional-specification/prd/`

3. **Pre-check — Validation Gate:**
   - Check if `VALIDATION_REPORT.md` exists in the PRD folder
   - If missing → run `/bnac-pag-verify` first (requires the `pag` profile)
   - If status is BLOCKED → STOP. Display critical failures. User must fix PRD first.
   - If status is PASS → proceed

4. **Execute pipeline steps sequentially:**

   **Step 1 — Validate** (if not already done):
   - Run validation per `pipeline/validation/` rules
   - Generate `VALIDATION_REPORT.md`

   **Step 2 — Generate Technical Specification:**
   - Read `pipeline/prompts/generate-tech-spec.md`
   - Read Section 13 (Application Type) to resolve stack
   - Generate `project-context/project-structure.md` and `project-context/project-tech-stack.md`

   **Step 3 — Generate Skills:**
   - Read `pipeline/prompts/generate-skills.md`
   - Analyze PRD use cases, business rules, integrations
   - Generate project-specific skills in `project/.claude/skills/`

   **Step 4 — Generate Implementation Plan:**
   - Read `pipeline/prompts/generate-plan.md`
   - Break project into milestones with tasks, file counts, agent assignments
   - Generate `project-context/implementation-plan.md`

5. After all steps complete:
   - Display pipeline summary (steps run, files generated, status per step)
   - Log results to `project/.claude/log.md`

## Pipeline Steps

| Step | Prompt | Input | Output |
|------|--------|-------|--------|
| 1 | validation rules | PRD 22 sections | `VALIDATION_REPORT.md` |
| 2 | `generate-tech-spec.md` | PRD Section 13 + stack refs | `project-structure.md`, `project-tech-stack.md` |
| 3 | `generate-skills.md` | PRD + project structure | Project-specific skills |
| 4 | `generate-plan.md` | PRD + tech spec + skills | `implementation-plan.md` |

## Examples

```
/bnac-pipeline-run-all ./prds/payment-service/   → run full pipeline for payment PRD
/bnac-pipeline-run-all                            → auto-detect PRD folder
```

## Error Handling

| Issue | Action |
|-------|--------|
| PRD not validated | Run validation first, then continue |
| Validation BLOCKED | STOP — display failures, user must fix |
| Section 13 missing | Cannot resolve stack — STOP |
| Stack reference files missing | Warn, proceed with manual stack definition |
