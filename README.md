# OMG — Oh My Gas City

OMG is a [Gas City](https://github.com/gastownhall/gascity) pack for three core software development processes:

1. **Define requirements** — discuss a feature with an agent and approve its specification. OMG saves it in the selected project's (rig's) `docs/requirements/` and publishes the approved change directly to `origin/main` without a second approval. A separate breakdown into an epic and Beads tasks needs its own approval. If publication fails, the file remains local and development does not start from it. Saving and publishing requirements do not start implementation.
2. **Implement requirements (features)** — explicitly start an approved `omg-development` task. The [v2 formula](packs/omg/formulas/omg-development.toml) prepares a worktree, plans and implements the change, runs tests, updates documentation, reviews and fixes the result, and publishes directly to `origin/main` after approval. The formula describes the method; applying it creates a Beads workflow.
3. **Fix bugs** — a planned core process. OMG can record `omg-bugfix` tasks, but does not yet provide a bug-fix formula or support launching them.

The pack lives in [`packs/omg/`](packs/omg/pack.toml) and provides a city-scoped OpenCode orchestrator, Agent Skills, the development formula, and a separate diagnostic [`omg-probe` formula](packs/omg/formulas/omg-probe.toml). The orchestrator helps choose a rig, recover saved requirements, create approved tasks, and explicitly launch supported work without requiring users to memorize `gc` commands. Workflow artifacts stay local to the task worktree under `.omg/tasks/<source-id>/artifacts/`; Beads stores work state and links, while `docs/` holds durable project documentation. The shared [`omg-okf` skill](packs/omg/skills/omg-okf/SKILL.md) applies Google OKF v0.2 to new or edited durable documents in a rig's `docs/` directory.

See [pack contracts](docs/pack-contracts.md), [project vision](docs/project-vision.md), [workflow requirements](docs/workflow-requirements.md), and [skill architecture](docs/skill-architecture.md) for details. Development rules are in [AGENTS.md](AGENTS.md). Licensed under [MIT](LICENSE).

## Set up OMG on a developer machine

These instructions target the tested `gc 1.5.0` configuration with OpenCode and Herdr. Replace example city and project paths with paths on your machine.

1. **Install prerequisites.** Follow the official [Gas City installation guide](https://github.com/gastownhall/gascity/blob/main/docs/getting-started/installation.md) for `gc` and its dependencies (including Git, tmux, Beads `bd`, and Dolt). Install [OpenCode](https://opencode.ai/docs/) and [Herdr](https://github.com/gastownhall/gascity/blob/main/docs/reference/herdr-provider.md), and configure access to the models you intend to use. Check the installed tools:

   ```sh
   gc version
   bd version
   opencode --version
   herdr --version
   ```

2. **Configure OpenCode model tiers.** Clone this repository and open its root in an independent OpenCode session:

   ```sh
   git clone https://github.com/atilla777/omg.git ~/omg
   cd ~/omg
   opencode
   ```

   Ask OpenCode: **“Load the `omg-install` skill and set up OMG on this computer.”** The [installation skill](.opencode/skills/omg-install/SKILL.md) checks `gc` and model availability, then carefully adds global `standard` (`openai/gpt-6-luna`) and `advanced` (`openai/gpt-6-sol`) OpenCode agents without changing your default agent or unrelated settings. It is a local setup skill, not part of the imported GC pack. If you change the global agent configuration later, restart affected OpenCode/GC sessions.

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

4. **Import OMG at city scope and register your project as a rig.** The remote import is locked to a Git commit by Gas City; the pack is in the `packs/omg` subdirectory, not at the repository root. Use a Git project with an `origin/main` remote for the development workflow's direct publication:

   ```sh
   gc --city ~/omg-city import add https://github.com/atilla777/omg/tree/main/packs/omg --name omg
   gc --city ~/omg-city import check
   gc --city ~/omg-city rig add /absolute/path/to/project --name my-project --prefix mp
   ```

   Before creating OMG tasks, inspect the rig's Beads types, then add `omg-research`, `omg-development`, and `omg-bugfix` to `types.custom`, **preserving** Gas City's existing service types and any other custom types:

   ```sh
   bd -C /absolute/path/to/project config get types.custom
   bd -C /absolute/path/to/project config set types.custom '<existing-types>,omg-research,omg-development,omg-bugfix'
   ```

   Replace `<existing-types>` with the value returned by `config get`, without duplicating types already present. Alternatively, the orchestrator can check this setting and ask before adding missing types. Only `omg-development` has a production workflow today; research and bug-fix tasks cannot yet be launched.

5. **Check and start.** Verify the pack and the orchestrator skill, then start the city and open its conversation:

   ```sh
   gc lint ~/omg/packs/omg
   gc --city ~/omg-city import check
   gc --city ~/omg-city skill list --agent omg.orchestrator
   gc start ~/omg-city
   gc --city ~/omg-city session attach omg.orchestrator
   ```

   You can also use the orchestrator terminal in Herdr. Ask it to select your rig and define a feature's requirements; approval publishes the specification to `origin/main`, while task decomposition and workflow launch require separate approval. For installation details and known limits, see [pack contracts](docs/pack-contracts.md).
