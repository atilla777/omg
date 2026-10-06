---
name: omg-dev-review
description: Review one attempt without editing the implementation; persist a structured verdict.
---

# Review one attempt

Load `omg-dev-context` and `omg-dev-review-attempt` and follow both shared contracts before reading or writing an attempt artifact.

Claim the assigned review bead and read closed prepare/plan/implement/document beads for this root and their recorded context and evidence. Inspect code, tests and documentation against the source criteria without editing.

For direct review → fix write `review/attempt-<gc.attempt>/review.json` with `schema: omg.review.v2`; for an existing synthesis attempt use `omg.review.v1` (synthesis supplies `required_fixes`). Include integer `attempt`, `source_id`, `workflow_root_id`, `review_step_id`, `verdict: approved|changes_required|blocked`, and `findings` (unique stable per-attempt IDs, severity, rig-relative affected files and actionable descriptions). For v2 also include `required_fixes`: actionable items with nonempty `finding_ids` referencing findings, descriptions and rig-relative affected files; `changes_required` needs at least one, `approved` needs neither findings nor required fixes.

For roots with `omg.workspace.artifacts_root`, create `review/attempt-<gc.attempt>/` inside that validated directory and write `review.md` **in the same attempt directory** as `review.json`; include `markdown_report_path` (worktree-relative path of `review.md`) and `reviewed_files` in the JSON. Inventory `git -C <worktree> ls-files -m -o -d --exclude-standard -z`, record exactly these rig-relative paths with SHA-256 of each regular file (null for deletions), reject symlinks and unrelated changes. The map is a snapshot of **everything** reviewed for publication. The Markdown file explains the verdict and findings for this source/root/attempt without duplicating large prose in the bead. Older roots without that metadata write only `review.json` in their prepared directory. Record the exact JSON path as bead `omg.review.report_path` and, when written, the Markdown path as `omg.review.markdown_path`. Read files and metadata back. On `blocked`, record the reason and question on the review bead, leave it open in Herdr until the human answers: closing it would let gc 1.5.0 advance the iteration. Otherwise set `gc.outcome=pass` and close only this bead. If review or inputs are incomplete, leave it open with notes. For an already-started v1 synthesis workflow, keep the prior behavior: close the review with its v1 verdict and let `omg-dev-synthesize` handle `blocked`.
