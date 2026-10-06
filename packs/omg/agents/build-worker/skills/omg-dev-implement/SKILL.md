---
name: omg-dev-implement
description: Implement an OMG development source in its prepared worktree and record actual test evidence.
---

# Implementation and tests

1. Claim and inspect `omg-development.implement` in the selected rig; read its root and `gc.var.source_id`. Read the closed `plan` blocker and, through its blocker, the closed `prepare` step (`bd -C <rig-path> dep list <id> --type blocks --json` and `bd -C <rig-path> show <id> --json`). Require all three beads to share `gc.root_bead_id`. Verify the source and `context.md` in the prepare notes, and read the exact implementation plan path recorded on the plan step. Never use the step ID to derive branch, worktree or artifact paths.
2. Implement the agreed scope in the prepared worktree. Add or update meaningful relevant tests and run them from that worktree. If tests cannot run, fail, or the plan is no longer appropriate, record the blocker and ask for guidance rather than claiming success. Do not edit another worktree or commit/push to `main`.
3. Write `docs/tasks/<source-id>/test-results.md` with executed commands, observed results (including failures and subsequent fixes), environment and date; list rig-relative changed files and remaining caveats. No local absolute paths in publishable artifacts: record the absolute worktree path and test-results path only in implement bead notes. Read back the evidence and verify `git -C <worktree> status --short` reflects the intended work; set `gc.outcome=pass` and close only the implement step if the relevant checks passed and the artifact is present. Do not commit in this or later review/fix steps: publication owns the single task commit. This is the **only initial implementation step**; later fixes use `omg-dev-apply-fixes`.
