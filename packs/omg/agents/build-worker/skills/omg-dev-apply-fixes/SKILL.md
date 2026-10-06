---
name: omg-dev-apply-fixes
description: Apply the required findings of precisely one review attempt and record test evidence.
---

# Apply review fixes

Claim the assigned `apply-fixes` bead. Read its `gc.root_bead_id`, `gc.attempt`, and blocking `synthesize-review-scope-check` control via `bd -C <rig-path> dep list <step-id> --type blocks --json`. Follow its blocker to the closed synthesis bead; require the same root/attempt and the `gc.step_ref` suffix `review-loop.iteration.<attempt>.synthesize-review`. Read **that bead's** `omg.review.synthesis_path`; validate schema, step IDs, source/root/attempt. Do not search for the latest file. Verify the worktree recorded by prepare.

For `changes_required`, apply only required fixes and run relevant tests; for `approved`, change nothing, verify test evidence and record `status=no_op`. On `blocked`, do not close and ask the human. For new roots resolve `fix.json` with `python3 <resolver> --worktree <worktree> --task <source-id> --mkdir --attempt <attempt> attempt fix.json` (pack `assets/scripts/task_workspace.py`); require it inside the recorded `omg.workspace.artifacts_root`. Older roots without that metadata retain `docs/tasks/<source-id>/review/attempt-<attempt>/fix.json`. Write `schema: omg.review-fix.v1`, integer `attempt`, `source_id`, `workflow_root_id`, `synthesis_step_id`, `fix_step_id`, `status: applied|no_op`, `addressed_finding_ids`, rig-relative changed files, `tests` (`command`, `outcome: pass|fail`, observed output) and remaining concerns. Applied fixes require passing tests and all mandatory finding IDs. Record the exact path in this bead's `omg.review.fix_path`, read it back, set `gc.outcome=pass` and close only this bead after passing checks. Failed tests leave it open with a reason. Do not commit, close the source or create another iteration.
