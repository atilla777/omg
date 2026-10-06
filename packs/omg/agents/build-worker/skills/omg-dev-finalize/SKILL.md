---
name: omg-dev-finalize
description: Finish an already-started legacy OMG workflow whose formula includes a finalize step.
---

# Legacy finalize (existing workflow only)

This step is not created by new `omg-development` workflows. For an existing workflow, require its review-loop blocker closed with `gc.outcome=pass`. Read its source ID and review-loop attempt beads by root, step reference and attempt. Verify latest synthesis approved and fix no-op with matching IDs. Write `development-result.md` in the **prepared** artifact directory recorded by this workflow (old runs use `docs/tasks/<source-id>/`), with attempt history and rig-relative artifact references. Do not assert publication.

Write `publish-manifest.json` in that same directory with `schema: omg.publish-manifest.v1`, source/root/review-loop IDs, prepared base SHA and `files` (rig-relative changed paths mapped to SHA-256, or null for a deleted file). Inventory `git ls-files -m -o -d --exclude-standard -z` in the task worktree, excluding the manifest itself; reject unrelated paths, symlinks, absolute local paths in publishable files and dirty index. Read the manifest back and compare its hashes with the files; record its absolute path as `omg.publish.manifest_path` on the root and in finalize notes. Set `gc.outcome=pass` and close only this step after successful verification. Otherwise leave it open. Never call `publish-development.py`.
