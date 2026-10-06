---
name: omg-dev-implement
description: Implement an OMG development source in its prepared worktree and record actual test evidence.
---

# Implement and test

1. Claim `omg-development.implement`; read its closed plan blocker and that step's closed prepare blocker via `bd -C <rig-path> dep list <id> --type blocks --json` and `bd -C <rig-path> show <id> --json`. Require a common `gc.root_bead_id`, source ID from the root, and the plan's **recorded path**. Read the context from prepare notes and verify the recorded worktree; never derive it from this step's ID. Older roots without `omg.workspace.artifacts_root` keep their prepared `docs/tasks/<source-id>/` path.
2. Implement the agreed scope in the task worktree. Add relevant tests and run them there. On failed tests or changed assumptions record a blocker and ask for guidance; do not commit or push.
3. For new roots resolve `test-results.md` through the pack's `assets/scripts/task_workspace.py` (`--worktree <worktree> --task <source-id> artifact test-results.md`); for older roots use their prepared directory. Write executed commands, observed results, environment, rig-relative changed files and remaining caveats. Record its exact absolute path in the implement bead notes, read it back, verify `git -C <worktree> status --short`, then set `gc.outcome=pass` and close only this step if checks passed. On failure keep the bead open with evidence and reason. Fixes in subsequent review attempts use a different skill.
