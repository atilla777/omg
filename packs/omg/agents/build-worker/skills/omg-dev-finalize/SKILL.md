---
name: omg-dev-finalize
description: Summarize an approved OMG review loop and its durable attempt history without publishing or closing the source.
---

# Finalize reviewed development

Claim `omg-development.finalize` in the selected rig; require the review-loop control blocker closed with `gc.outcome=pass`. Read the root's source ID and all review-loop attempt beads by `gc.root_bead_id`, `gc.step_ref`, `gc.attempt` in Beads. Verify the latest synthesis is approved and its fix is a no-op with matching IDs; collect earlier attempts and their results. Record `docs/tasks/<source-id>/development-result.md` in the prepared worktree with the plan, implementation/test evidence, docs changes, review and fix artifact paths by attempt, check outcome, remaining work and source status. Record the path and summary on the finalize bead, set `gc.outcome=pass` and close only this step. If the control outcome or artifacts are missing, leave the step open with the reason. Never publish to `main` or close the source bead.
