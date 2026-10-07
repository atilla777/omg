---
name: omg-dev-synthesize
description: Synthesize findings from the current iteration of an OMG development review into an actionable artifact.
---

# Synthesize one review attempt

Load `omg-dev-context` and `omg-dev-review-attempt` and follow both shared contracts before reading or writing an attempt artifact. When asking the human or reporting a blocked step in Herdr, load `omg-human-dialog` and follow its question and result rules.

Only already-created workflows have a `synthesize-review` bead. Their v1 review → synthesis → fix contract is not supported by the current runtime checker. If assigned this bead, report that manual handling is required and leave it open; closing it could advance an unsupported attempt. Do not create an artifact, close the source or spawn attempts.
