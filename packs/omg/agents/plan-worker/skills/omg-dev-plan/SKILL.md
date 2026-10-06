---
name: omg-dev-plan
description: Write a technical plan for an OMG development task in its prepared worktree.
---

# Plan implementation

Load `omg-dev-context` and use its checks to resolve the source, worktree and recorded artifacts directory (including already-started workflows).

1. Claim `omg-development.plan` and inspect its closed prepare blocker through `bd -C <rig-path> dep list <step-id> --type blocks --json`. Verify the recorded `context.md` and branch.
2. Read source acceptance criteria and its linked rig requirements (if any). Write `implementation-plan.md` in the validated artifacts directory. Write the intended changes, rig-relative affected files, decisions, test commands and expected outcomes, and coverage of each criterion. Do not implement here. Ask the human in Herdr if blocked.
3. Record the exact plan path and a concise summary in this bead's notes. Read the file back, set `gc.outcome=pass` and close only plan when complete; otherwise leave it open with the reason.
