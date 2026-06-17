Invoke the **bnac-skill-creator** agent to author a new skill folder (`<slug>/SKILL.md` + `<slug>/reference/*.md`) following BNAC conventions.

**Agent:** `bnac-skill-creator`
**Target:** `$ARGUMENTS` (kebab-case skill slug, required — e.g., `phase-template`, `pag-critical-rules`, `react-hook-patterns`)

## What to do

1. Delegate to the `bnac-skill-creator` agent with these instructions:
   - If `$ARGUMENTS` is a kebab-case slug → infer the target profile from the slug prefix (e.g., `react-*` → `src/stacks/react-ts/skills/`, `pag-*` → `src/stacks/pag/skills/`, otherwise `src/core/skills/`) and author at that location, OR (for user-authored skills) at `<cwd>/.claude/skills/<slug>/`
   - If the slug looks unusual (no recognizable prefix and no matching reference skills) → flag it and confirm the destination with the user before writing
   - If no arguments → **default to the current working folder's basename** (kebab-cased) as the slug. Tell the user which slug was inferred before authoring. Only ask for clarification if the basename is empty or cannot be normalized to kebab-case.

2. The bnac-skill-creator agent will:
   - **Read** context chain (`~/.claude/CLAUDE.md`, reference SKILL.md files of similar shape)
   - Resolve target path: `core/skills/` (cross-stack) or `stacks/<profile>/skills/` (profile-scoped)
   - Identify skill type — procedural / template / lookup / mixed
   - **Read** 2 reference skill folders of matching type to model after
   - **Write** `<slug>/SKILL.md` with frontmatter, purpose, Additional Resources, Steps/Format/Lookup, Rules
   - **Write** 1–3 reference files under `<slug>/reference/` with the authoritative content
   - **Read** SKILL.md to verify reference links resolve

3. After completion, log results to `project/.claude/log.md`

## Examples

```
/bnac-skill-create phase-template            → core baseline, template skill, in core/skills/
/bnac-skill-create pag-critical-rules        → PAG profile, lookup skill (34 rules table)
/bnac-skill-create react-hook-patterns       → React profile, procedural skill, custom hook authoring
/bnac-skill-create owasp-python              → Python profile, lookup skill, security audit checks
```
