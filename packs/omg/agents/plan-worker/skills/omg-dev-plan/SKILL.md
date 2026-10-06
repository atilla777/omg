---
name: omg-dev-plan
description: Produce the technical implementation plan for a prepared OMG development source bead.
---

# Technical plan

1. Claim and inspect the assigned `omg-development.plan` step and its root in the selected rig using `bd -C <rig-path>`. Read the `prepare` blocker through `bd -C <rig-path> dep list <step-id> --type blocks --json`; require its closed result and matching `gc.root_bead_id`. Verify the root's `gc.var.source_id` and read the exact source and the prepare notes. Open `context.md` at the path recorded there; verify branch, worktree, source ID and root against Beads. Use the worktree, not the city or rig main worktree.
2. Read the source's acceptance criteria and referenced requirements in the rig (if any), inspect relevant project code, then write `docs/tasks/<source-id>/implementation-plan.md` in the prepared worktree. Include the intended change, affected files, decisions/risks, relevant test commands and their expected outcomes, and the relationship to each acceptance criterion. Do not implement code in this step. Ask the user in the Herdr session if a design decision is blocked.
3. Record the plan path and a concise plan summary in this step's notes. Read the plan back, verify it belongs to this source and worktree, set `gc.outcome=pass` and close only the plan step. On missing context or incomplete plan, record the blocker and leave it open.
