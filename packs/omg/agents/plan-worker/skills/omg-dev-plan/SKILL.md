---
name: omg-dev-plan
description: Write a technical plan for an OMG development task in its prepared worktree.
---

# Plan implementation

1. Claim `omg-development.plan` and inspect its closed prepare blocker through `bd -C <rig-path> dep list <step-id> --type blocks --json`. Require a matching `gc.root_bead_id`, source ID from the root's `gc.var.source_id`, and the prepared `omg.workspace.path`. For new runs require `omg.workspace.artifacts_root` too. Verify the recorded `context.md`, branch and worktree. Older roots without `omg.workspace.artifacts_root` use the path recorded in prepare notes under `docs/tasks/<source-id>/`; never silently switch an active run.
2. Read source acceptance criteria and its linked rig requirements (if any). Resolve `implementation-plan.md` with the pack's `assets/scripts/task_workspace.py` (`--worktree <worktree> --task <source-id> artifact implementation-plan.md`) for new roots; for an older run use its prepared artifact directory. Write the intended changes, rig-relative affected files, decisions, test commands and expected outcomes, and coverage of each criterion. Do not implement here. Ask the human in Herdr if blocked.
3. Record the exact plan path and a concise summary in this bead's notes. Read the file back, set `gc.outcome=pass` and close only plan when complete; otherwise leave it open with the reason.
