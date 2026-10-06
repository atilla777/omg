---
name: omg-dev-review-attempt
description: Identify and verify the exact review-loop attempt and its producer beads in an OMG development workflow.
---

# Shared review-attempt identity

Use this contract after loading the assigned review, synthesis, fix or publish skill. Resolve source/root/worktree with `omg-dev-context` first. The step's own skill defines its artifact schema, verdict semantics, and side effects.

1. Review/fix/synthesis beads belong to the `review-loop` of the same `gc.root_bead_id`. Require a positive integer `gc.attempt` and the matching `gc.step_ref` suffix `review-loop.iteration.<attempt>.<step>`; runtime-spawned steps may prepend the formula name. Never select an artifact by the newest filename or by scanning an attempt directory.
2. For `apply-fixes`, follow its blocking `review-scope-check` control to the **closed review bead of this attempt**, matching root, attempt and review step reference. For an already-started workflow with a `synthesize-review-scope-check` blocker, follow that control to this attempt's closed synthesis bead and from there to its closed review. For `synthesize-review`, follow its own `review-scope-check` blocker to the closed review bead. A review bead determines whether its attempt has a `synthesize-review` child: that child means the existing v1 review → synthesis → fix contract, even if the workspace uses `.omg/tasks/`; otherwise the direct v2 review → fix contract applies. A v1 review without its required synthesis is not a v2 approval.
3. Read the exact review/synthesis/fix artifact path from the **matching producer bead's metadata** (`omg.review.report_path`, `omg.review.synthesis_path`, `omg.review.fix_path` as applicable). Validate the file's schema, `source_id`, `workflow_root_id`, `attempt` and producer step ID against the producer bead; validate its links to the preceding bead and report path. If root metadata has `omg.workspace.artifacts_root`, require the attempt files under `review/attempt-<attempt>/` in that recorded root; an older root without it uses the directory recorded by prepare under `docs/tasks/<source-id>/`. Reject cross-attempt, cross-root or missing links; do not guess by path.
4. Publication must establish the **latest** attempt for this root from its beads and passing `review-loop` check, then require its approved review (and v1 synthesis when present) and the same attempt's no-op fix. Approval of an earlier attempt or a review bead alone does not authorize publication. The publish skill adds snapshot, manifest and remote-main checks.
