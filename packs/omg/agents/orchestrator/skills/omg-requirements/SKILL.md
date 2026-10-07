---
name: omg-requirements
description: Use when interviewing a user about feature behavior, agreeing, saving, finding or revising requirements in a Gas City rig's docs/ directory.
---

# OMG feature requirements

This skill handles feature behavior, not implementation planning, Beads or formula execution. Speak in the user's language. The agreed specification in the rig is the durable source of truth for development; do not rely on the current conversation surviving.

## Select the rig and document

1. Run `gc rig list --json` from the city context to obtain registered rig names and absolute paths. Select the project the user meant, excluding the HQ/city rig unless explicitly requested. If the user did not identify a rig and there is more than one plausible project, ask which one. If there is no project rig, explain that a rig must be attached before saving; do not write to the city. Confirm that the selected path is the rig's project root before using files there.
2. For a new feature, use `docs/requirements/<slug>.md` **under that rig**. The slug is a short lowercase ASCII kebab-case name of the feature. Check for an existing file with the same name before writing. If it exists, ask whether this is an update to that feature or a distinct feature; never silently replace another specification.
3. For an earlier feature or an update, inspect Markdown files in the selected rig's `docs/requirements/`, search titles/content if necessary, and ask which document the user means if matches are ambiguous. Read the chosen file before describing it or changing it. If the directory does not exist, report that there are no OMG specifications there; do not invent one. A user may provide a specific `docs/` path: verify it is inside the selected rig and read it directly.

## Ground the discussion

Before proposing behavior, read the selected rig's applicable project vision, overall product specification, development rules (including `AGENTS.md` and linked rules where present), existing feature requirements and relevant `docs/` conventions. Discover their actual locations; do not assume OMG's own project documents apply to every rig. Read relevant existing behavior in the project when documentation alone cannot answer a material question. Distinguish agreed behavior from aspirations, drafts and current implementation. Cite relevant document paths in discussion and, when useful, link them from the specification. If sources disagree with each other or with the user's request, explain the conflict and ask which behavior should govern; do not silently choose one. If a source is missing, ask for the intended authority only when it matters; do not invent a project policy.

## Interview and stress-test

Start with what the user and project already establish; ask **one material question at a time**, with a concise suggested answer or concrete options when helpful. Find out who uses the feature and why, the desired outcome and main flow, inputs and observable outputs, permissions or relevant constraints, scope and exclusions, and what success looks like. Probe ambiguous terms and decisions with concrete examples. Do not ask for information already clear from the repo, demand irrelevant details, or turn the interview into a fixed questionnaire.

Test the proposed behavior with applicable counterexamples: empty/invalid input, missing or stale data, duplicate actions, concurrent changes, unavailable dependencies, permissions, interruption/retry, and effects on existing users or data. Ask the user to decide material cases rather than guessing defaults. Record only relevant scenarios; do not generate a generic edge-case checklist in the spec. Separate unresolved blockers from explicitly deferred, out-of-scope questions. If a material behavior remains undecided or conflicts with project rules, stop short of claiming the specification is approved.

## Propose and agree on behavior

Shape a human-readable specification describing **what the feature must do**, not how to implement it. Include the problem/goal, actors and meaningful user scenarios (user stories or concrete flows where useful), scope and exclusions, behavior in important failure/edge cases, and observable acceptance criteria tied to those scenarios. Keep technical plans, file/module choices, internal algorithms and Beads/formula decisions out of feature requirements; externally visible integration constraints may belong here. Make criteria specific enough that a developer and user can tell whether the result satisfies them.

Record the reason for significant product-behavior choices alongside the decision in the specification, including the relevant alternative or constraint when it explains the trade-off; do not turn every answer into a decision log. Suggest a separate ADR only when a choice is costly to reverse, surprising without context, **and** involves a real trade-off. Ask before creating one and follow the rig's existing ADR conventions and `omg-okf` if it lives under `docs/`. Do not require an ADR or glossary for ordinary requirements. Never let a proposed ADR substitute for agreeing on observable behavior.

After resolving material questions, present a **brief approval summary**: goal, boundaries, main and edge-case behavior, acceptance criteria and significant decisions; for an update, identify what changes and whether existing tasks or agreed behavior may be affected. Explicitly ask the user to confirm this result **before writing or revising**. A request to discuss is not consent to save; explicit approval of an already-presented summary is sufficient. Preserve still-valid agreed content on updates, and re-confirm changed behavior rather than silently replacing it.

## Save and retrieve

Load `omg-okf` before writing or revising the approved specification as an OKF v0.2 concept in the selected rig's `docs/requirements/<slug>.md`. Create `docs/requirements/` only after agreement if necessary. Use `type: Feature Specification`, a descriptive title and sections `Цель`, `Границы` and `Критерии приёмки` (translate headings if the conversation is in another language); add readable sections for scenarios, important exceptions and decision rationale when relevant. Keep deferred questions clearly separate from approved behavior; never present unresolved blockers as agreed requirements. For an existing specification, follow `omg-okf` to bring that file into the format without migrating unrelated documents. Keep project-specific details in the specification, not in the pack. Read the saved file back and show the user its rig, relative path and a brief summary of what was saved. If the write failed or format validation fails, say so; never report an unsaved draft as saved.

For lookup, show the saved content or a faithful summary with its relative path, and use it as context for the next discussion. Do not create a Beads task, epic, convoy, workflow or execution as a side effect of saving or viewing requirements. For a separate request to decompose saved requirements, load `omg-decompose`; formula execution remains unavailable.
