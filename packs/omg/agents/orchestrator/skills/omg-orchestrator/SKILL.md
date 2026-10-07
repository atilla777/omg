---
name: omg-orchestrator
description: Route OMG requirements, Beads decomposition, explicit probe or development launch and workflow status requests in the Gas City orchestrator.
---

# OMG orchestrator

Load `omg-human-dialog` for all human-facing questions and reports. Determine whether the user wants to discuss/save feature requirements, find/show earlier requirements, decompose a saved specification, explicitly launch a supported probe or development task, or inspect an existing execution. For requirements, load `omg-requirements` and follow its rig-selection, agreement and retrieval procedure. For decomposition, load `omg-decompose` and use its confirmed plan and `omg-gc` procedures; find the saved specification even if this is a new dialogue. For launch or observation, load `omg-gc` and use its manual launch/status procedure, including rig and source-ID selection. The orchestrator's working directory belongs to the city, not necessarily the user's rig; never assume its `docs/` or Beads database belongs to the project.

Requirements can be agreed and saved, and a separately confirmed decomposition can create Beads source tasks. Supported launch mappings are `omg-probe → omg-probe` (diagnostic) and `omg-development → omg-development` (preparation, plan, implementation/tests, documentation, bounded review/fix, direct origin/main publication and source closure); never route `omg-research`, `omg-bugfix` or an unknown type. Explain the absence of other formulas without substituting a built-in formula. Saving a specification is not permission to create tasks, and creating tasks is not permission to execute them. The user's explicit development launch authorizes the complete formula for this one ready source, including publication; when reporting status distinguish review approval, publication and source closure. Observation does not require new permission to launch. On returning to a conversation, look up saved specifications, source beads and workflow records rather than relying on chat memory.

When asked to confirm that this skill loaded, reply with `omg-entrypoint-ready`.
