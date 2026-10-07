---
name: omg-dev-implement
description: Implement an OMG development source in its prepared worktree and record actual test evidence.
---

# Implement and test

Load `omg-dev-context` and use its checks to resolve the source, worktree and recorded artifacts directory (including already-started workflows).

1. Claim `omg-development.implement`; read its closed plan blocker and that step's closed prepare blocker via `bd -C <rig-path> dep list <id> --type blocks --json` and `bd -C <rig-path> show <id> --json`. Require the plan's **recorded path** and read the context from prepare notes.
2. Implement the agreed scope in the task worktree. If implementation creates or changes durable documentation under `docs/`, load `omg-okf` before writing it; leave operational task artifacts under the validated artifacts directory. Add relevant tests and run them there. On failed tests or changed assumptions record a blocker and ask for guidance; do not commit or push.
3. Write `test-results.md` in the validated artifacts directory. Include executed commands, observed results, environment, rig-relative changed files and remaining caveats. Record its exact absolute path in the implement bead notes, read it back, verify `git -C <worktree> status --short`, then set `gc.outcome=pass` and close only this step if checks passed. On failure keep the bead open with evidence and reason. Fixes in subsequent review attempts use a different skill. Leave changes uncommitted for review; only publish commits the approved snapshot.
