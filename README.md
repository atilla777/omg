# OMG — Oh My Gas City

OMG is a [Gas City](https://github.com/gastownhall/gascity) pack for three core software development processes:

1. **Define requirements** — discuss a feature with an agent and approve its specification. OMG saves it in the selected project's (rig's) `docs/requirements/` and publishes the approved change directly to `origin/main` without a second approval. A separate breakdown into an epic and Beads tasks needs its own approval. If publication fails, the file remains local and development does not start from it. Saving and publishing requirements do not start implementation.
2. **Implement requirements (features)** — explicitly start an approved `omg-development` task. The [v2 formula](packs/omg/formulas/omg-development.toml) prepares a worktree, plans and implements the change, runs tests, updates documentation, reviews and fixes the result, and publishes directly to `origin/main` after successful review. The formula describes the method; applying it creates a Beads workflow. After publication and source closure, OMG checks whether all epic children are complete and each development task's commit is present in remote `main` before closing the epic.
3. **Fix bugs** — a planned core process. OMG can record `omg-bugfix` tasks, but does not yet provide a bug-fix formula or support launching them.

The pack lives in [`packs/omg/`](packs/omg/pack.toml) and provides a city-scoped OpenCode orchestrator, Agent Skills, the development formula, and a separate diagnostic [`omg-probe` formula](packs/omg/formulas/omg-probe.toml). The orchestrator helps choose a rig, recover saved requirements, create approved tasks, and explicitly launch supported work without requiring users to memorize `gc` commands. Workflow artifacts stay local to the task worktree under `.omg/tasks/<source-id>/artifacts/`; Beads stores work state and links, while `docs/` holds durable project documentation. The shared [`omg-okf` skill](packs/omg/skills/omg-okf/SKILL.md) applies Google OKF v0.2 to new or edited durable documents in a rig's `docs/` directory.

See [pack contracts](docs/pack-contracts.md), [project vision](docs/project-vision.md), [workflow requirements](docs/workflow-requirements.md), and [skill architecture](docs/skill-architecture.md) for details. Development rules are in [AGENTS.md](AGENTS.md). Licensed under [MIT](LICENSE).

## Set up OMG on a developer machine

These instructions target the tested `gc 1.5.0` configuration with OpenCode and Herdr. Keep three locations distinct: the **OMG source checkout** (for running `omg-install` and linting `packs/omg`), the **Gas City city** (where the OMG pack is imported), and the **user's Git project** (registered with the city as a rig). For example, `/home/aleksei/plums/omg` is the OMG checkout, `~/omg-city` is a separate city, and `/home/aleksei/plums/slyx` is a separate project/rig. Do not copy or clone OMG's sources or pack into the user project.

1. **Install prerequisites.** Follow the official [Gas City installation guide](https://github.com/gastownhall/gascity/blob/main/docs/getting-started/installation.md) for `gc` and its dependencies (including Git, tmux, Beads `bd`, and Dolt). Install [OpenCode](https://opencode.ai/docs/) and [Herdr](https://github.com/gastownhall/gascity/blob/main/docs/reference/herdr-provider.md), and configure access to the models you intend to use. Check the installed tools:

   ```sh
   gc version
   bd version
   opencode --version
   herdr --version
   ```

2. **Configure OpenCode model tiers from the OMG checkout.** Open the OMG repository root in an independent OpenCode session. If you already have a checkout, use it; otherwise clone OMG to a separate location of your choice, outside the user project. For the existing checkout:

   ```sh
   cd /home/aleksei/plums/omg
   opencode
   ```

   Ask OpenCode: **“Load the `omg-install` skill and set up OMG on this computer.”** The [installation skill](.opencode/skills/omg-install/SKILL.md) checks `gc` and model availability, then carefully adds global `standard` (`openai/gpt-6-luna`) and `advanced` (`openai/gpt-6-sol`) OpenCode agents without changing your default agent or unrelated settings. It configures the machine's global OpenCode, not the rig, and is not part of the imported GC pack. If you change the global agent configuration later, restart affected OpenCode/GC sessions.

3. **Create a city and configure its runtime.** For `gc 1.5.0`, the initialization wizard does not accept `opencode` as `--default-provider`; initialize with `codex` and `--no-start`, then edit `~/omg-city/city.toml` before starting the city:

   ```sh
   gc init --template minimal --default-provider codex --no-start ~/omg-city
   ```

   Set `provider = "opencode"` in the existing `[workspace]` table. Set or add these tables, retaining the other generated settings:

   ```toml
   [providers.opencode]
   base = "builtin:opencode"

   [session]
   provider = "herdr"
   ```

   OMG roles already use `session = "tmux"` so their OpenCode terminals are visible in Herdr. The minimal template's `mayor` role is unrelated to OMG.

4. **Check the project's Git mainline before OMG workflows.** OMG publishes approved requirements and development results directly to `origin/main`. The project must have a local `main` branch with a commit, a reachable `origin/main`, and permission to push to it. Check the project itself, not the OMG checkout:

   ```sh
   git -C /home/aleksei/plums/slyx status --short --branch
   git -C /home/aleksei/plums/slyx rev-parse --verify HEAD
   git -C /home/aleksei/plums/slyx remote get-url origin
   git -C /home/aleksei/plums/slyx ls-remote --exit-code --heads origin main
   ```

   `rev-parse` fails if there is no local commit. The last command prints a SHA only if remote `main` exists (exit status 2 means no matching branch; other failures may indicate a connection or access problem). Check that the local `main` is based on the intended remote history and that you can publish to `origin/main`; a configured URL alone does not establish either fact. If this is a new local repository **without commits**, first inspect its remote: if `origin/main` exists, fetch and base local work on that history (or clone the remote) rather than creating an unrelated initial history. If it does not exist, prepare and review the initial project contents, create the first commit on local `main`, and publish `main` to `origin` yourself. Verify `origin/main` after that. Do not start OMG requirements publication or development workflows until this mainline is ready.

5. **Import OMG at city scope and register the project as a rig.** The remote import is locked to a Git commit by Gas City; the pack is in the `packs/omg` subdirectory, not at the repository root. The import belongs to the city, while `rig add` points at the separate project directory:

   ```sh
   gc --city ~/omg-city import add https://github.com/atilla777/omg/tree/main/packs/omg --name omg
   gc --city ~/omg-city import check
   gc --city ~/omg-city rig add /home/aleksei/plums/slyx --name slyx --prefix slyx --default-branch main
   ```

   `--default-branch main` explicitly records the branch expected by OMG. Before creating OMG tasks, inspect the rig's Beads types, then add `omg-research`, `omg-development`, and `omg-bugfix` to `types.custom`, **preserving** Gas City's existing service types and any other custom types:

   ```sh
   bd -C /home/aleksei/plums/slyx config get types.custom
   bd -C /home/aleksei/plums/slyx config set types.custom '<existing-types>,omg-research,omg-development,omg-bugfix'
   ```

   Replace `<existing-types>` with the value returned by `config get`, without duplicating types already present. Alternatively, the orchestrator can check this setting and ask before adding missing types. Only `omg-development` has a production workflow today; research and bug-fix tasks cannot yet be launched.

6. **Check and start.** Verify the pack from the OMG checkout and the orchestrator skill in the city, then start the city and open its conversation:

   ```sh
   gc lint /home/aleksei/plums/omg/packs/omg
   gc --city ~/omg-city import check
   gc --city ~/omg-city skill list --agent omg.orchestrator
   gc start ~/omg-city
   gc --city ~/omg-city session attach omg.orchestrator
   ```

   You can also use the orchestrator terminal in Herdr. Ask it to select your rig and define a feature's requirements; approval publishes the specification to `origin/main`, while task decomposition and workflow launch require separate actions. For installation details and known limits, see [pack contracts](docs/pack-contracts.md).

## Short commands in the orchestrator's OpenCode session

These commands are supplied by the imported OMG pack for the **Gas City orchestrator's OpenCode session**, not for independently opened OpenCode in the OMG checkout or a project rig. Update the city's OMG import to the published version and restart the orchestrator/OpenCode session to pick up new commands and skills. You can still use ordinary conversation.

| Command | Example | Effect |
| --- | --- | --- |
| `/omg-req` | `/omg-req show slyx docs/requirements/search.md` | Discuss, find, show, approve or save requirements. Approval of the proposed summary publishes the approved specification to `origin/main`; saving does not create tasks. |
| `/omg-plan` | `/omg-plan slyx docs/requirements/search.md` | Propose an epic and typed subtasks from a **confirmed published** specification. Creating them requires separate approval of the breakdown; no development starts. |
| `/omg-dev` | `/omg-dev slyx-abc` | Check that exact source ID and start one ready `omg-development` workflow if it has no prior run needing attention. |
| `/omg` | `/omg slyx slyx-epic-id` | In the specified project and epic, select one next unblocked source by creation time, then ID. Start it only if it is ready and of type `omg-development`. |

**Before invoking `/omg` or `/omg-dev`:** either invocation is permission for **one complete development cycle**, including implementation, tests, bounded review/fixes, direct push to `origin/main` and closure of that source task after publication. There is no second confirmation before push, and the next task is never started automatically. If project, epic or source is ambiguous, the orchestrator asks one choice question instead of launching several tasks. A live workflow is reported rather than duplicated; an earlier failed run requires explicit reconciliation rather than a silent restart. Unsupported `omg-research`/`omg-bugfix` tasks are reported without substituting another formula. Asking for status (for example “show status of slyx-abc”) only inspects work; it never starts a workflow. The commands forward the user's text to the orchestrator as `$ARGUMENTS`. See [selection and retry rules](docs/pack-contracts.md#короткие-команды-opencode-plan-029).
