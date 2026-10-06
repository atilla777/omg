---
name: omg-dev-synthesize
description: Synthesize findings from the current iteration of an OMG development review into an actionable artifact.
---

# Synthesize one review attempt

Load `omg-dev-context` and `omg-dev-review-attempt` and follow both shared contracts before reading or writing an attempt artifact.

Only for already-created workflows with a `synthesize-review` bead; new workflows use the direct review → fix contract.

Claim `synthesize-review`. Validate the producing review report's `schema: omg.review.v1` and `review_step_id`. For roots with `omg.workspace.artifacts_root`, read the producer's `omg.review.markdown_path` and match it to `markdown_report_path` in the JSON before synthesizing. Do not edit code.

Write `review/attempt-<gc.attempt>/synthesis.json` in the validated artifacts directory; require the review bead's recorded report and (when present) Markdown paths in that exact attempt directory. Write `schema: omg.review-synthesis.v1`, integer `attempt`, `source_id`, `workflow_root_id`, `review_step_id`, `synthesis_step_id`, `review_report_path` (worktree-relative path of the recorded review), `verdict: approved|changes_required|blocked` and `required_fixes` with mandatory finding IDs, descriptions and rig-relative affected files. For `blocked`, record this path and `omg.review.blocked_attempt` on the root, explain the question on this bead and **leave it open** in Herdr: gc 1.5.0 otherwise creates another attempt. Otherwise set this bead's `omg.review.synthesis_path` to the absolute file path, read it back, set `gc.outcome=pass` and close only this bead. Do not spawn attempts yourself.
