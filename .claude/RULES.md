# Enterprise Rules — 10 Rules

> These rules apply across all 7 BNAC profiles. The 5 core rules apply universally; the 5 React rules apply when the React profile is installed.
> Violation of any "Must Never" rule is a blocking error.

---

## Active Rules

### 1. Context-First Execution (`rules/context-first.md`)

**Must always:** Read context before executing any command, skill, or agent action.

Read in order:
1. `~/.claude/CLAUDE.md` → platform rules
2. `project/.claude/CLAUDE.md` → project overrides (if exists)
3. `project/.claude/SUMMARY.md` → project state (if exists)
4. `project/.claude/milestone-status.md` → active milestone (if exists)
5. `project/.claude/memory/MEMORY.md` → typed long-term memory index (if exists; Phase CMM)
6. `project/.claude/context/carry-forward.md` → compact summary of completed milestones/phases (if exists; Phase CMM)

Steps 5–6 are conditional — projects without `memory/` or `context/` continue to work. Default load is summary-only; agents may opt up to a completed milestone's full `.md` detail when explicitly needed (regression, cross-milestone refactor, user request).

**Must never:** Execute a command without first reading the context chain. Read a completed milestone's full detail when its summary is sufficient.

---

### 2. Git Workflow (`rules/git-workflow.md`)

**Must always:** Follow conventional commit format: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `style`, `perf`, `ci`, `build`

Branch strategy: `main` (production), `develop` (integration), `feature/<ticket>-<desc>`, `fix/<ticket>-<desc>`

**Must never:**
- Use `git --no-verify` — fix the hook, don't skip it
- Force-push to `main` or `develop`
- Commit secrets (API keys, passwords, tokens, connection strings)

---

### 3. Coding Standards (`rules/coding-standards.md`)

**Must always:** Follow stack-appropriate naming conventions, code quality rules, and security standards.

Key rules:
- No `any` types (TypeScript) — use proper types
- No magic numbers — use named constants
- No commented-out code — use git history
- Parameterized queries — never concatenate user input into SQL
- Input validation at system boundaries
- No secrets in code

**Must never:** Commit code with known security vulnerabilities.

---

### 4. Activity Logging (`rules/activity-logging.md`)

**Must always:** Log every significant action to `project/.claude/log.md` with timestamp, command, context read, files modified, and result.

**Must never:** Batch logs or skip logging failures (failed actions are valuable context too).

---

### 5. Memory Management (`rules/memory-management.md`) — Phase CMM 2026-05-21

**Must always:** Use the typed memory store at `project/.claude/memory/` for facts that should survive across sessions and milestones. Pick the right type for each entry:
- `user` — role, preferences, knowledge
- `feedback` — corrections + confirmations (with **Why** and **How to apply** lines)
- `project` — deadlines, decisions, motivation (with **Why** and **How to apply** lines)
- `reference` — pointers to external systems (Linear, Grafana, Slack)

Maintain `MEMORY.md` as the index (one line per memory, ≤ 200 lines). Use `/bnac-memory <add|list|forget|search>` rather than editing the files by hand.

**Must never:** Save code patterns, git history, debugging recipes, or ephemeral task state in memory — those belong in code, commits, or active milestone files. Save anything that conflicts with current project state; update or remove instead.

---

## React Rules (5)

> Requires React-TS stack (`bnac install --profile react`). Located in `stacks/react-ts/rules/`.
> These rules apply to all React+TS+BNDS projects in addition to the 4 core rules above.

### 5. Separation Pattern (`stacks/react-ts/rules/separation-pattern.md`)

**Must always:** Follow the 8-file component structure. Respect import boundaries.

Every component: `.types.ts` → `.util.ts` → `.hooks.ts` → `.tsx` → `.scss` → `.test.tsx` → `.stories.tsx` → `index.ts`

**Must never:** Import `.util.ts` directly in `.tsx`. Put business logic in `.tsx`. Import BNDS in `.hooks.ts`.

---

### 6. DS Compliance (`stacks/react-ts/rules/ds-compliance.md`)

**Must always:** Use BNDS components for all rendering. Use design tokens for all CSS values. Use utility classes first.

**Must never:** Use raw HTML elements (`<div>`, `<button>`, `<input>`, etc.). Hardcode CSS values (`16px`, `#333`). Override BNDS internals.

---

### 7. SCSS Files (`stacks/react-ts/rules/scss-files.md`)

**Must always:** Use `var(--bnds-g-*)` tokens for every value. Use BEM naming.

**Must never:** Hardcode `px`, `#hex`, `rgb()` values. Use `!important`. Nest deeper than 3 levels.

---

### 8. Component Files (`stacks/react-ts/rules/component-files.md`)

**Must always:** Use BNDS components for all rendering. Use `React.forwardRef`. Set `displayName`. Import styles as SCSS module.

**Must never:** Contain business logic (validation, API calls). Import `.util.ts` directly. Use inline styles.

---

### 9. Types Files (`stacks/react-ts/rules/types-files.md`)

**Must always:** Contain only interfaces, types, enums. Use PascalCase naming. Name props interface `ComponentNameProps`.

**Must never:** Import from React, BNDS, or runtime libraries. Contain implementation code.

---

## Profile Rule Coverage

| Profile | Rules folder | Rule files | Notes |
|---------|--------------|-----------|-------|
| `core` (baseline) | `core/rules/` | 5 | Apply to all profiles (`context-first`, `git-workflow`, `coding-standards`, `activity-logging`, `memory-management`) |
| `react` | `stacks/react-ts/rules/` | 5 | Listed above |
| `bnac`, `pag`, `ui`, `dotnet`, `python`, `flutter` | — | 0 | Stack constraints encoded in agent/skill content rather than separate rule files |

The 5 core rules apply universally regardless of profile. Stack-specific constraints for non-React profiles live inside the corresponding agents and skills (e.g. `dotnet-compliance-checker` enforces .NET conventions; `python-security-checker` enforces OWASP/bandit findings) so authoring guidance and enforcement live next to each other rather than being split across a separate rules tree.

---

## Future Rules

If patterns recur across multiple profiles, they may graduate into formal rule files in a future milestone. Candidates: cross-profile a11y baseline (WCAG 2.2 AA), cross-profile RTL baseline.
