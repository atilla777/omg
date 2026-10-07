---
name: omg-dev-document
description: Update durable project documentation separately from task workflow evidence.
---

# Document implementation

Load `omg-dev-context` and use its checks to resolve the source, worktree and recorded artifacts directory (including already-started workflows).

1. Claim `omg-development.document`; verify the closed implement, plan and prepare steps belong to the same root and source. Read the recorded plan/test paths and prepared context in the task worktree. A missing or failing test result blocks this step.
2. Compare behavior with acceptance criteria; explicitly update **durable** project documentation in `docs/` where needed, or explain why none is necessary. Before writing any such file load `omg-okf` and apply it to each created or edited document, including converting a pre-OKF document when touched. Check links and applicable documentation checks. Operational reports belong only to the prepared task artifacts root, not `docs/`; the shared OKF skill does not apply to them, including older workflow artifacts in `docs/tasks/<source-id>/`.
3. Write `documentation-result.md` in the validated artifacts directory. Summarize source ID, rig-relative plan and test paths, documentation changes and checks. Record its exact path and result in this bead's notes; read it back, set `gc.outcome=pass` and close only this step after checks pass. Otherwise leave it open with a reason. Leave documentation changes uncommitted for review and publish.
