---
name: omg-dev-document
description: Update durable project documentation separately from task workflow evidence.
---

# Document implementation

1. Claim `omg-development.document`; verify the closed implement, plan and prepare steps belong to the same root and source. Read the recorded plan/test paths and prepared context in the task worktree. A missing or failing test result blocks this step.
2. Compare behavior with acceptance criteria; explicitly update **durable** project documentation in `docs/` where needed, or explain why none is necessary. Check links and applicable documentation checks. Operational reports belong only to the prepared task artifacts root, not `docs/`.
3. For new roots require the recorded `omg.workspace.artifacts_root` and matching source ID/worktree, ensure the absolute path stays inside the worktree without symlink escape, and write `documentation-result.md` there; older roots use their prepared `docs/tasks/<source-id>/` directory. Summarize source ID, rig-relative plan and test paths, documentation changes and checks. Record its exact path and result in this bead's notes; read it back, set `gc.outcome=pass` and close only this step after checks pass. Otherwise leave it open with a reason. Leave documentation changes uncommitted for review and publish.
