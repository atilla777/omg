---
name: omg-human-dialog
description: Explain OMG work and ask people for decisions in clear language, one question at a time, across orchestrator and worker sessions.
---

# Talking with people

Use this method whenever a skill asks a person for a decision or reports a result, including a stopped or partly completed operation. It governs the **human-facing message**, not exact names stored in Beads, commands, artifacts or metadata.

1. Speak in the person's language. Start with the meaning of the situation: what was found or done, why their input matters, and what happens next. Use short sentences and everyday words. Avoid unexplained jargon or borrowed English words when a clear local equivalent exists. Keep literal IDs, paths, commands, type names and widely understood abbreviations when needed for accuracy; explain their meaning briefly on first use. Do not translate identifiers or hide an error behind a reassuring summary.
2. Before asking, look up facts already available in the project and its records. Ask **one material decision per message**, with only the context needed to decide it. Do not bundle a question about choosing a project with a question about starting work. When offering choices, including yes/no approval, label them `1.`, `2.`, etc., make each independently selectable by replying with one number, and mark one as recommended with a short reason. A harness choice tool is fine when available, but include numbers in the visible option labels; never depend on the tool being present. If a choice cannot responsibly be recommended, say why. For a genuinely open-ended answer, ask one focused question without inventing artificial choices. Accept a clear answer in words as well as a digit; clarify only when it is ambiguous.
3. In a report, distinguish verified facts from pending work and uncertainty. Say what was done, the present state, and the next concrete action or decision (including who needs to act). If nothing remains, say so rather than suggesting another operation. For an interruption, state what is known to have changed, what is unverified, and how to resume safely. Do not imply that a launched workflow finished, that review approval means publication, or that an open step proves a person is being asked a question. Use concise headings and only the details needed for this request; keep precise IDs and paths so the person can return later.

For Gas City operation reports, follow the result shape in `assets/reports/gc-result.md` in this pack when accessible. The essential headings are **Что сделано**, **Текущее состояние**, **Что дальше** (translated to the person's language). Read the template if accessible; the headings and rules above remain sufficient when an imported pack's asset path is unavailable in the session.
