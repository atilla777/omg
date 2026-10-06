---
name: omg-dev-review
description: Review one specific iteration of an OMG development workflow without editing implementation files.
---

# Review the current implementation

Claim the assigned review bead in the selected rig. Read `gc.root_bead_id`, `gc.step_ref`, and `gc.attempt` on the bead; require a positive attempt number and a step reference ending in `review-loop.iteration.<attempt>.review` (runtime-spawned attempts may prepend the formula name). Read the root's `gc.var.source_id` and the closed prepare/plan/implement/document beads for this root; read their recorded paths and worktree context. Check the current code, test evidence and documentation against source acceptance criteria and plan. Do not change code or documentation. Use `bd -C <rig-path>` for all Beads reads and writes.

Write `docs/tasks/<source-id>/review/attempt-<attempt>/review.json` **in the prepared worktree**. JSON fields: `schema: omg.review.v1`, integer `attempt`, `source_id`, `workflow_root_id`, `review_step_id`, `verdict: approved|changes_required|blocked`, and `findings` (list with stable per-attempt IDs, severity, affected files and actionable descriptions). For approval use an empty findings list; for a blocker describe the reason. The artifact must refer to this attempt only; do not copy a previous verdict without checking the current implementation. Record its absolute path as bead metadata `omg.review.report_path`, read it back, set `gc.outcome=pass` and close **only** this review bead. If inputs are missing or the review cannot be completed, leave the step open with notes instead of asserting approval. Report `blocked` for a genuine review decision requiring human intervention, so the synthesis step can stop this attempt.
