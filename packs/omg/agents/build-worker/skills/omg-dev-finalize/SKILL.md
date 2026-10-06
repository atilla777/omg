---
name: omg-dev-finalize
description: Summarize an approved OMG review loop and its durable attempt history without publishing or closing the source.
---

# Finalize reviewed development

Claim `omg-development.finalize` in the selected rig; require the review-loop control blocker closed with `gc.outcome=pass`. Read the root's source ID and all review-loop attempt beads by `gc.root_bead_id`, `gc.step_ref`, `gc.attempt` in Beads. Verify the latest synthesis is approved and its fix is a no-op with matching IDs; collect earlier attempts and their results. Record `docs/tasks/<source-id>/development-result.md` in the prepared worktree with the plan, implementation/test evidence, docs changes, review and fix **rig-relative** artifact paths by attempt, check outcome and source status **as of review**. Do not include local absolute paths or assert that publication already happened.

After writing and reading back the result, resolve the helper from the root's `gc.formula_source` as sibling `../assets/scripts/publish-development.py`. From the prepared `context.md` read the base SHA, then run `python3 <helper> snapshot --rig <rig-path> --worktree <worktree> --source <source-id> --root <root-id> --base-sha <base-sha> --review-loop <review-loop-id> --manifest <worktree>/docs/tasks/<source-id>/publish-manifest.json`. Read the generated JSON, verify its source, root, approved review-loop ID and files against actual worktree status; stop if any file was not part of this source's reviewed change. Record its absolute path on the root as `omg.publish.manifest_path` and in this step's notes. Set `gc.outcome=pass` and close only finalize after the result and snapshot both exist. On missing inputs, unreviewed changes or script failure, record the reason and leave finalize open. Do not publish to `main` or close the source bead here.
