---
name: omg-decompose
description: Plan and create a feature epic and typed source subtasks in Beads from an agreed specification in a Gas City rig, without starting execution.
---

# OMG feature decomposition

Use this skill only when the user asks to turn a saved, agreed feature specification into Beads work. Speak in the user's language. Load `omg-requirements` to select the rig and find/read the specification, and `omg-gc` for the Beads operations. The city working directory is not the project rig.

## Prepare the plan

1. Identify the selected rig and read the actual Markdown file under its `docs/requirements/`. If there are multiple candidate rigs or specifications, ask which one. Do not create tasks from an unsaved draft or from chat memory. Check that the specification contains a goal, scope and acceptance criteria; resolve material gaps with the user instead of inventing decisions.
2. Check whether this specification already has an epic or subtasks in the selected rig (inspect existing Beads, including closed issues). If one exists, show its IDs and ask whether the user wants to inspect or revise it; do not silently create a duplicate or silently modify existing tasks. If a previous creation stopped part-way, identify the existing IDs and agree on how to finish it before any further write.
3. Propose a **work breakdown**, not a technical implementation plan: epic title, purpose and completion criteria; for each source subtask, a short title, `omg-research`, `omg-development` or `omg-bugfix`, scope, observable acceptance criteria and any prerequisite subtasks that block it. Assign temporary labels (A, B, C) to explain dependencies. Only include justified edges, keep the graph acyclic, and distinguish independent work from sequential work. Include the relative specification path in every proposed issue. Ask the user to confirm the complete plan before writing Beads. Agreement to save requirements alone does not authorize decomposition.

## Create and show

After confirmation, use the rig-scoped procedures in `omg-gc`: verify support for all proposed types without overwriting existing Gas City types; create one `epic`, then its typed children with `--parent`, acceptance criteria and specification reference; add only the confirmed blocking edges (`dependent` blocked by `prerequisite`). Record each returned ID. Never use `gc sling`, `gc formula cook`, `gc route` or any other operation that assigns work or starts a workflow. If creation or verification fails, stop, report what was actually created and its IDs, and do not claim success or repeat the whole creation blindly.

Read back the epic, children and blocking edges from Beads. Compare title, type, parent, acceptance criteria, reference and dependencies with the approved plan; if anything differs, describe it instead of claiming completion. Show the user the rig, relative specification path, epic ID, each child ID/type and which prerequisite IDs block it. Make clear these are source tasks only; execution requires a separate request and a supported formula.
