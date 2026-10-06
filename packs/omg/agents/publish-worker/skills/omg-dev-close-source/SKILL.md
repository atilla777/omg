---
name: omg-dev-close-source
description: Close the original OMG development source only after independently confirming its publication on origin/main.
---

# Close the published source

Load `omg-dev-context` to validate the original source and prepared workspace before confirming publication of this already-started workflow.

1. Claim `omg-development.close-source` in the selected rig. Verify the closed publish blocker (`gc.step_id=omg-development.publish`, same `gc.root_bead_id`, `gc.outcome=pass`) and the root's `gc.var.source_id`, `omg.publish.commit`, `omg.publish.report_path`, `omg.publish.status=published`. Read the report and manifest paths in the recorded worktree, require matching source/root IDs and `schema: omg.publication.v1`, and verify the published commit contains the manifest, implementation, tests and review evidence listed there. Require the source bead has type `omg-development` and is still open (or already closed with this same SHA on retry). Never close a workflow step, input convoy or epic in its place.
2. Read `git ls-remote origin refs/heads/main` and fetch main into `refs/remotes/origin/main`; require the published commit is an ancestor of the remote main, local main contains it, and the report's commit is the exact task commit. If the remote is inaccessible or the evidence cannot be confirmed, leave source and this step open with reason. Do not infer publication from a local commit or successful push output alone.
3. On success, set source metadata `omg.publish.commit=<sha>`, `omg.publish.report_path=<path>`, `gc.outcome=pass`, then close **only** the source with reason including SHA; read it back and confirm `status=closed`, `gc.outcome=pass`, and exact SHA. If already closed with that SHA on a retry, verify evidence and do not reclose. Only then set `gc.outcome=pass` and close this step. Read a dependent source bead with `bd -C <rig-path> show <dependent-id> --json` / `bd -C <rig-path> ready --json` when one exists and report whether its blocking dependency cleared. Do not route the dependent bead automatically.
