Invoke the **bnac-developer** agent to undo the last generation, install, or modification.

**Agent:** `bnac-developer`
**Target:** `$ARGUMENTS` (optional — `install`, `generation`, `commit`, or specific file/folder)

## What this command does

`/bnac-undo` is the agent-facing complement to `bnac rollback` (M13). It selects the right reversal mechanism for the kind of change being undone:

| Kind of change                    | Reversal mechanism                        |
|-----------------------------------|-------------------------------------------|
| `bnac install` / `bnac update`    | `bnac rollback --target <t>`              |
| Code generation (file edits)      | `git restore <paths>` or `git revert`     |
| Last commit                       | `git revert HEAD` (preferred over reset)  |
| File-level mistake (uncommitted)  | `git restore <path>` for tracked files    |
| Pipeline-generated artifacts      | Delete generated artifact + run pipeline again |

## What to do

1. Determine the kind of change by reading recent context:
   - `project/.claude/log.md` — the latest entry tells you what happened
   - `git status` and `git log --oneline -5` — what's in flight
   - For install/update issues: read `install-state.json` for the active target

2. Choose the safest reversal:
   - **Install/update issues** → run `bnac rollback --target <target> --dry-run` first, then without `--dry-run` after confirming the snapshot diff. Never delete `install-state.json` manually.
   - **Code edits committed** → `git revert <sha>` to create a new commit that undoes the change. Avoid `git reset --hard` unless the work is uncommitted and the user explicitly asks for it.
   - **Code edits uncommitted** → `git restore <paths>` for specific files, or `git stash` if the user wants to keep the diff for later.
   - **Generated docs / scaffolds** → delete the generated tree and re-run the originating command.

3. Confirm with the user *before* taking destructive action when:
   - More than 5 files are affected
   - The change touches files outside `project/.claude/` and outside the current working tree
   - Reverting would discard work that has not been pushed to a remote

4. After the reversal:
   - Run `bnac doctor --target <target>` if it was an install/update revert
   - Run `npm run build` (or the project's build) if it was a code revert
   - Append an `undo` entry to `project/.claude/log.md` describing what was reversed and why

## Why prefer `git revert` over `git reset`

`git revert` creates a new commit that inverts an old one. It preserves history, works after the change has been pushed, and is reversible itself. `git reset --hard` rewrites history and silently destroys uncommitted work — only use it when both the user explicitly asks and the work is local to the working tree.

## Why prefer `bnac rollback` over manual file restore

`bnac rollback` replays a snapshot that captured every tracked file's contents *plus* the install state. Manual file copying loses the state.json and leaves `bnac doctor`/`bnac update` referencing a phantom install. Always use `bnac rollback` for install/update reversals.

## Examples

```
/bnac-undo                                    → infer from latest log entry, propose reversal
/bnac-undo install                            → bnac rollback --target claude
/bnac-undo commit                             → git revert HEAD
/bnac-undo src/components/UserCard/           → git restore src/components/UserCard/
/bnac-undo last                               → most recent change of any kind
```

## Limits

- This command does not undo wiki edits or PRD generation that hit external systems.
- It does not undo work that has been merged to a protected branch — that requires a follow-up PR.
- It does not bypass branch protection or signed-commit requirements.
