Initialize project context files. One command, flag-driven shape — replaces `/bnac-init-claude-md`, `/bnac-init-project-local`, and `/bnac-quick-project`.

**Agent:** none (this command runs directly, no agent delegation)
**Target:** `$ARGUMENTS` — `[--minimal] [--root] [project-name]`

## Shape modes

| Mode (flags) | Writes | Replaces legacy command |
|---|---|---|
| **default** (no flags) | `.claude/{CLAUDE.md, SUMMARY.md, milestone-status.md, log.md}` | `/bnac-init-project-local` |
| **`--minimal`** | `.claude/{CLAUDE.md, milestone-status.md, log.md}` (skip SUMMARY.md) | `/bnac-quick-project` |
| **`--root`** | `<cwd>/CLAUDE.md` at repo root (in addition to the `.claude/` bundle) | `/bnac-init-claude-md` |
| **`--root --minimal`** | Root `CLAUDE.md` + minimal `.claude/` bundle | combo |
| **`--root` alone, no `.claude/` written** | use `--root --no-local` for the legacy `init-claude-md` exact behavior | `/bnac-init-claude-md` (strict) |

Flags compose. `[project-name]` is optional; defaults to the cwd basename.

## What to do

1. Parse flags from `$ARGUMENTS`:
   - `--minimal` → skip `SUMMARY.md`
   - `--root` → also write `<cwd>/CLAUDE.md` at repo root
   - `--no-local` → skip the `.claude/` bundle entirely (only meaningful with `--root`)
   - Remaining positional → project name (else use cwd basename)

2. Detect the project stack from `cwd` (best-effort; fall back to `unknown`):
   - `package.json` + `tsconfig.json` + `react` dep → `react-ts`
   - `package.json` (no react) → `node`
   - `*.csproj` / `*.sln` → `dotnet`
   - `pyproject.toml` / `requirements.txt` / `setup.py` → `python`
   - `pubspec.yaml` → `flutter`
   - `index.html` + `*.css|*.scss` (no framework) → `ui`
   - otherwise → `unknown`

3. **If `--root`** — check if `<cwd>/CLAUDE.md` already exists:
   - If yes → show its first 10 lines and ask before overwriting. Never silently clobber.
   - If no → read `~/.claude/templates/project-CLAUDE.md`, apply placeholders, write to `<cwd>/CLAUDE.md`.

4. **Unless `--no-local`** — check if `.claude/` already exists:
   - If yes → warn the user and ask before overwriting any individual file.
   - If no → create the directory.

5. Write `.claude/` files from templates (skip rows the flags exclude):

   | File | Template Source | Created when |
   |------|-----------------|--------------|
   | `.claude/CLAUDE.md`         | `project-CLAUDE.md` | always (unless `--no-local`) |
   | `.claude/SUMMARY.md`        | `SUMMARY.md`        | unless `--minimal` |
   | `.claude/milestone-status.md` | `milestone-status.md` | always (unless `--no-local`) |
   | `.claude/log.md`            | `log.md`            | always (unless `--no-local`) |
   | `.claude/memory/MEMORY.md`  | `MEMORY.md`         | always (unless `--no-local`) — typed long-term memory index |
   | `.claude/context/carry-forward.md` | `carry-forward.md` | always (unless `--no-local`) — compact history (empty stub until first milestone completes) |

6. Replace template placeholders in every file written:
   - `{{PROJECT_NAME}}` → resolved project name
   - `{{STACK}}` → detected stack from step 2
   - `{{TIMESTAMP}}` → current date (`YYYY-MM-DD`)
   - `{{DATE}}` → current date
   - `{{TIME}}` → current time (`HH:mm`)

7. Append a `session-start` entry to `.claude/log.md` (if it exists) per the activity-logging rule.

8. Print the next-steps summary (see Output).

## Output

```
✅ Project context initialized

Wrote:
  CLAUDE.md                    (root)            ← only with --root
  .claude/CLAUDE.md            (overrides)
  .claude/SUMMARY.md                              ← skipped with --minimal
  .claude/milestone-status.md
  .claude/log.md
  .claude/memory/MEMORY.md                        ← typed memory index (loaded per context-first step 5)
  .claude/context/carry-forward.md                ← compact history stub (loaded per context-first step 6; populated as milestones complete)

Stack detected: <stack>

Next steps:
  1. Fill in .claude/CLAUDE.md with build commands and conventions
  2. Fill in .claude/SUMMARY.md with architecture and decisions (if present)
  3. Set up milestones in .claude/milestone-status.md
  4. Add memory entries with /bnac-memory add <type> "<content>" as you learn project facts
  5. carry-forward.md will auto-populate as you /bnac-milestone complete each milestone
```

## Examples

```
/bnac-init                          → full bundle (CLAUDE.md + SUMMARY.md + milestone-status.md + log.md in .claude/)
/bnac-init my-dashboard             → full bundle, custom project name
/bnac-init --minimal                → skip SUMMARY.md (lightweight/prototype init)
/bnac-init --minimal my-prototype   → minimal bundle, custom name
/bnac-init --root                   → full bundle + root CLAUDE.md (auto-loaded by Claude Code)
/bnac-init --root --no-local        → root CLAUDE.md only, no .claude/ bundle
/bnac-init --root --minimal         → root CLAUDE.md + minimal .claude/ bundle
```

## When to upgrade from `--minimal` to full

If a prototype grows past exploratory scope, re-run `/bnac-init` without `--minimal` to add `SUMMARY.md`. Existing files are preserved unless you explicitly approve overwrite.

## Two-tier resolution (why `.claude/CLAUDE.md` and `<cwd>/CLAUDE.md` can co-exist)

| File | Loaded by | Purpose |
|------|-----------|---------|
| `<cwd>/CLAUDE.md`             | Claude Code automatically (repo-root convention) | Primary, always-on project context |
| `<cwd>/.claude/CLAUDE.md`     | BNAC two-tier resolver (overrides global)        | Project-specific overrides on top of `~/.claude/CLAUDE.md` |

Both can co-exist. Use `--root` if you want the repo-root variant on top of the `.claude/` bundle.
