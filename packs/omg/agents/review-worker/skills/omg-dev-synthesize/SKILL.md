---
name: omg-dev-synthesize
description: Synthesize findings from the current iteration of an OMG development review into an actionable artifact.
---

# Synthesize one review attempt

Claim `synthesize-review`. Follow its blocking `review-scope-check` control to the closed review bead of this attempt (not the newest file). Require matching `gc.root_bead_id`, `gc.attempt` and `gc.step_ref` suffix `review-loop.iteration.<attempt>.review`; runtime-spawned attempts may prepend the formula name. Read **that bead's** `omg.review.report_path`; validate its schema, source/root/attempt and `review_step_id`. For new roots read the same bead's `omg.review.markdown_path` and match it to `markdown_report_path` in the JSON before synthesizing. Do not edit code.

For new roots resolve `synthesis.json` through `python3 <resolver> --worktree <worktree> --task <source-id> --mkdir --attempt <attempt> attempt synthesis.json` (pack `assets/scripts/task_workspace.py`); require it and the review report to be inside the recorded task artifacts root. Older roots without that metadata retain `docs/tasks/<source-id>/review/attempt-<attempt>/synthesis.json`. Write `schema: omg.review-synthesis.v1`, integer `attempt`, `source_id`, `workflow_root_id`, `review_step_id`, `synthesis_step_id`, `review_report_path` (worktree-relative path of the recorded review), `verdict: approved|changes_required|blocked` and `required_fixes` with mandatory finding IDs, descriptions and rig-relative affected files. For `blocked`, record this path and `omg.review.blocked_attempt` on the root, explain the question on this bead and **leave it open** in Herdr: gc 1.5.0 otherwise creates another attempt. Otherwise set this bead's `omg.review.synthesis_path` to the absolute file path, read it back, set `gc.outcome=pass` and close only this bead. Do not spawn attempts yourself.
