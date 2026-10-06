---
name: omg-orchestrator
description: Route OMG feature requirements conversations, saved requirement lookups and Beads decomposition requests in the Gas City orchestrator.
---

# OMG orchestrator

Determine whether the user wants to discuss/save feature requirements, find/show earlier requirements, decompose a saved specification, or proceed to execution. For requirements, load `omg-requirements` and follow its rig-selection, agreement and retrieval procedure. For decomposition, load `omg-decompose` and use its confirmed plan and `omg-gc` procedures; find the saved specification even if this is a new dialogue. The orchestrator's working directory belongs to the city, not necessarily the user's rig; never assume its `docs/` or Beads database belongs to the project.

Requirements can be agreed and saved, and a separately confirmed decomposition can create Beads source tasks. Choosing a formula, execution and publishing are not yet available in OMG. Explain that limit when requested; do not launch a built-in Gas City formula as a substitute. Saving a specification is not permission to create tasks, and creating tasks is not permission to execute them. When returning to a conversation, look up saved specifications and existing Beads rather than relying on chat memory.

When asked to confirm that this skill loaded, reply with `omg-entrypoint-ready`.
