---
name: omg-gc
description: Use Gas City rig discovery and Beads CLI to inspect, create and verify OMG feature epics and typed source subtasks without routing or running them.
---

# OMG Gas City / Beads: decomposition operations

This skill currently covers **only** rig discovery and Beads issue creation/inspection for decomposition. It does not support formula selection, routing, workflow launch or execution status. Use it from `omg-decompose` after the user confirms the work breakdown.

## Select and inspect

- From the city context use `gc rig list --json` to obtain the registered rig name, absolute project path and Beads state. Do not treat the city/HQ rig as the project by default. Confirm the chosen path is the project root. Use `bd -C <rig-path>` for **every** Beads operation; never let cwd implicitly select the city's Beads database.
- Check `bd -C <rig-path> config get types.custom` before creation. The three OMG source types are `omg-research`, `omg-development` and `omg-bugfix`. If a required type is missing, ask the user before changing rig configuration; if authorized, append only missing values to the existing comma-separated `types.custom` (preserve Gas City service types and any other custom types), then read it back. A missing type must not be replaced by a built-in `task` type. If Beads is uninitialized or the rig is not writable, stop and report it; do not initialize or attach a rig implicitly.
- Before creating, inspect existing issues in the **selected rig** (`bd -C <rig-path> list --all --limit 0 --json`, `bd -C <rig-path> show <id> --json` as needed) for the same specification path and epic. Do not equate an empty default `bd list` or its first page with no prior work. If the state is ambiguous, ask the user before changing it.

## Persist the confirmed graph

Use `bd -C <rig-path> create '<epic title>' --type epic --description '<purpose and rig-relative docs/requirements/...md reference>' --acceptance '<epic completion criteria>' --silent` and capture its returned ID. For each approved subtask use `bd -C <rig-path> create '<title>' --type <omg-type> --parent <epic-id> --description '<scope and rig-relative spec reference>' --acceptance '<observable criteria>' --silent`. Pass user content safely as arguments or a body file, never interpolate it into a shell command. Retain the temporary-label-to-Beads-ID map.

Once all subtasks exist, for each confirmed prerequisite add `bd -C <rig-path> dep add <dependent-id> <prerequisite-id>` (default `blocks`: the first issue is blocked by the second). Do not create a blocking edge from a child to the epic; `--parent` supplies hierarchy. If any write fails, stop and report the partial graph for deliberate reconciliation, rather than recreating it. Never invoke `gc sling`, `gc formula cook`, `gc route`, `bd ready` as a dispatch trigger, or any execution command.

Read back the epic and each child with `bd -C <rig-path> show <id> --json`, and blocking edges with `bd -C <rig-path> dep list <id> --type blocks --json`. Confirm children have the intended parent, type, requirements reference and acceptance criteria, and that the edge direction matches the confirmed plan. Present actual IDs and relationships, not just CLI success messages.
