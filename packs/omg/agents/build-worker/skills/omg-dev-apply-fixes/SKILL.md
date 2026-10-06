---
name: omg-dev-apply-fixes
description: Apply the required findings of precisely one review attempt and record test evidence.
---

# Apply review fixes

Load `omg-dev-context` and `omg-dev-review-attempt` and follow both shared contracts before reading or writing an attempt artifact.

Claim the assigned `apply-fixes` bead. For the direct review → fix workflow require the producing review artifact's `schema: omg.review.v2`; for an already-started workflow with synthesis require `omg.review-synthesis.v1` from that attempt's synthesis bead. For `changes_required`, apply only `required_fixes` and run relevant tests; for `approved`, change nothing, verify test evidence and record `status=no_op`. On `blocked`, do not close and ask the human. Write `review/attempt-<gc.attempt>/fix.json` in the validated artifacts directory. For direct review → fix write `schema: omg.review-fix.v2`, integer `attempt`, `source_id`, `workflow_root_id`, `review_step_id`, `review_report_path` (worktree-relative path to this review bead's report), `fix_step_id`, `status: applied|no_op`, `addressed_finding_ids`, rig-relative changed files, `tests` (`command`, `outcome: pass|fail`, observed output) and remaining concerns. For an existing synthesis workflow write the previous `omg.review-fix.v1` with `synthesis_step_id` instead of review links. Applied fixes require passing tests and all mandatory finding IDs. Record the exact path in this bead's `omg.review.fix_path`, read it back, set `gc.outcome=pass` and close only this bead after passing checks. Failed tests leave it open with a reason. Do not commit, close the source or create another iteration.
