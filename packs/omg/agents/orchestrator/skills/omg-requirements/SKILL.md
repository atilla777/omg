---
name: omg-requirements
description: Use when discussing, agreeing, saving, finding or showing feature requirements in the docs/ directory of a Gas City rig.
---

# OMG feature requirements

This skill handles only feature specifications, not Beads or formula execution. Speak in the user's language. A saved file is the durable context; do not rely on the current conversation surviving.

## Select the rig and document

1. Run `gc rig list --json` from the city context to obtain registered rig names and absolute paths. Select the project the user meant, excluding the HQ/city rig unless explicitly requested. If the user did not identify a rig and there is more than one plausible project, ask which one. If there is no project rig, explain that a rig must be attached before saving; do not write to the city. Confirm that the selected path is the rig's project root before using files there.
2. For a new feature, use `docs/requirements/<slug>.md` **under that rig**. The slug is a short lowercase ASCII kebab-case name of the feature. Check for an existing file with the same name before writing. If it exists, ask whether this is an update to that feature or a distinct feature; never silently replace another specification.
3. For an earlier feature or an update, inspect Markdown files in the selected rig's `docs/requirements/`, search titles/content if necessary, and ask which document the user means if matches are ambiguous. Read the chosen file before describing it or changing it. If the directory does not exist, report that there are no OMG specifications there; do not invent one. A user may provide a specific `docs/` path: verify it is inside the selected rig and read it directly.

## Agree and save

Discuss the feature's goal, scope (including relevant exclusions), and observable acceptance criteria. Resolve material open questions with the user before claiming agreement. Summarize the proposed specification and ask the user to confirm it **before writing or revising**. Do not treat a request to discuss as consent to save; if the user explicitly approves an already-presented specification, that approval is sufficient. For updates, explain what will change and preserve agreed content that is still valid.

Save the agreed specification as Markdown in the selected rig's `docs/requirements/<slug>.md`. Create `docs/requirements/` only after agreement if necessary. Use a descriptive title and sections `Цель`, `Границы` and `Критерии приёмки` (translate headings if the conversation is in another language); record concrete decisions and unresolved questions separately when applicable. Keep project-specific details in the specification, not in the pack. Read the saved file back and show the user its rig, relative path and a brief summary of what was saved. If the write failed, say so; never report an unsaved draft as saved.

For lookup, show the saved content or a faithful summary with its relative path, and use it as context for the next discussion. Do not create a Beads task, epic, convoy, workflow or execution as a side effect of saving or viewing requirements. If asked to proceed to those stages, explain the current OMG limit.
