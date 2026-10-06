---
name: omg-orchestrator
description: Route OMG requirements, Beads decomposition, explicit probe launch and workflow status requests in the Gas City orchestrator.
---

# OMG orchestrator

Determine whether the user wants to discuss/save feature requirements, find/show earlier requirements, decompose a saved specification, explicitly launch a probe, or inspect an existing execution. For requirements, load `omg-requirements` and follow its rig-selection, agreement and retrieval procedure. For decomposition, load `omg-decompose` and use its confirmed plan and `omg-gc` procedures; find the saved specification even if this is a new dialogue. For launch or observation, load `omg-gc` and use its manual launch/status procedure, including rig and source-ID selection. The orchestrator's working directory belongs to the city, not necessarily the user's rig; never assume its `docs/` or Beads database belongs to the project.

Requirements can be agreed and saved, and a separately confirmed decomposition can create Beads source tasks. The only supported launch type is the dedicated diagnostic `omg-probe`, mapped to formula `omg-probe`; never route `omg-research`, `omg-development`, `omg-bugfix` or an unknown type. Explain the absence of their formulas when asked, without substituting a built-in formula. Saving a specification is not permission to create tasks, and creating tasks is not permission to execute them. When returning to a conversation, look up saved specifications, source beads and workflow records rather than relying on chat memory. Observation does not require new permission to launch.

When asked to confirm that this skill loaded, reply with `omg-entrypoint-ready`.
