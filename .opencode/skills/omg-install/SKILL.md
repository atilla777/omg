---
name: omg-install
description: Use when setting up OMG on a computer: configure global OpenCode model-tier agents and check Gas City readiness before importing the OMG pack.
---

# Set up OMG model tiers

This skill is run in an independently opened OpenCode session at the root of the OMG repository, before starting OMG sessions in Gas City. It configures the **user's global OpenCode**, not the rig or this repository. The pack already assigns OpenCode agent names to its GC roles; do not rewrite formula model IDs or add `option_defaults.model` to the city.

1. Confirm `gc version`, `opencode --version` and that `opencode models openai` lists `openai/gpt-6-luna` and `openai/gpt-6-sol`. If either model is unavailable, stop and ask the user for an available replacement rather than silently choosing a different model.
2. Read the current `~/.config/opencode/opencode.json` or `.jsonc` and any global `~/.config/opencode/agent/` or `agents/` definitions named `standard` or `advanced`. If both config files exist, inspect both; avoid duplicate agent definitions or conflicting project-level overrides. Preserve all existing keys, formatting where possible, and unrelated agent definitions. If an existing definition conflicts with the intended tier, show the difference and ask before overwriting it. Do not change `default_agent` or global `model`.
3. In the existing global OpenCode config (or create `~/.config/opencode/opencode.json` if none exists), merge just the following `agent` entries. Declare `"$schema": "https://opencode.ai/config.json"` in a new JSON file. The agents are `primary`, so `opencode --agent <name>` can use them as the active conversation agent. Do not add custom prompts or blanket permissions that would replace the GC role's instructions or the user's existing permission policy.

   ```json
   {
     "agent": {
       "standard": {
         "description": "OMG standard model tier",
         "mode": "primary",
         "model": "openai/gpt-6-luna"
       },
       "advanced": {
         "description": "OMG advanced model tier",
         "mode": "primary",
         "model": "openai/gpt-6-sol"
       }
     }
   }
   ```

4. Validate the merged config against the current OpenCode schema, then run `opencode agent list` to confirm both names and `opencode debug agent standard` / `opencode debug agent advanced` to inspect the effective model of each. Run the latter from an actual GC agent's working directory too, to detect project-level overrides; the command need not print the entire global configuration. Avoid printing credential values in the user-facing summary.
5. Tell the user to restart existing OpenCode/GC sessions after changing global config: sessions load configuration at startup. Before starting the city, verify the imported pack with `gc lint packs/omg` and `gc --city <city> import check`; its GC roles use `session = "tmux"` and either `args = ["--agent", "standard"]` or `args = ["--agent", "advanced"]`. Do not claim ACP uses these args: it has separate `acp_args`. If a city provider overrides `opencode` with a `--model` pin or a workflow supplies `opt_model`, reconcile that override before claiming the global agent's model will be used.

Leave the exact provider model IDs in the user's global OpenCode configuration. After setup, changing a tier's model there (and restarting its session) updates every OMG role using that tier without changing the pack.
