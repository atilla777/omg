---
name: omg-dev-document
description: Align project documentation with an implemented OMG development subtask and record its outcome.
---

# Document the implementation

1. Claim and inspect `omg-development.document` in the selected rig; verify the root's source ID, the closed implement blocker, the closed plan and prepare steps, and their common root. Read the paths from predecessor notes, then read `context.md`, `implementation-plan.md` and `test-results.md` **in the prepared worktree**. Check that the recorded test outcome passed; an absent or failing result blocks this step.
2. Compare implemented behavior and acceptance criteria with the project's user/developer documentation. Update the relevant docs in the prepared worktree, or explicitly record why no documentation changes are needed. Check changed documentation links and any applicable docs checks. Do not assert that code was reviewed, merged or published.
3. Write `docs/tasks/<source-id>/documentation-result.md` summarizing source ID, branch, rig-relative plan and test evidence paths, documentation changed (or justified none) and checks. Keep absolute worktree path only in Beads notes, never in publishable files. Record the absolute artifact path and documentation/check results on this step's notes and read them back. Set `gc.outcome=pass` and close only the document step after the evidence exists and checks pass; leave it open with a reason on failure. The source bead remains open for review and later publication work.
