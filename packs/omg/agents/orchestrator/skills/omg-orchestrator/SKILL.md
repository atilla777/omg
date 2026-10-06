---
name: omg-orchestrator
description: Route OMG feature requirements conversations, saved requirement lookups and requests for later workflow stages in the Gas City orchestrator.
---

# OMG orchestrator

Determine whether the user wants to discuss/save feature requirements, find/show earlier requirements, or proceed to a later workflow stage. For the first two actions, load `omg-requirements` and follow its rig-selection, agreement and retrieval procedure. The orchestrator's working directory belongs to the city, not necessarily the user's rig; never assume its `docs/` is the destination.

Requirements can be agreed and saved now. Decomposition into Beads, choosing a formula, execution and publishing are not yet available in OMG. Explain that limit when requested; do not create tasks or launch a built-in Gas City formula as a substitute. Saving a specification is not permission to perform another stage. When returning to a conversation, look up the saved specification rather than relying on chat memory.

When asked to confirm that this skill loaded, reply with `omg-entrypoint-ready`.
