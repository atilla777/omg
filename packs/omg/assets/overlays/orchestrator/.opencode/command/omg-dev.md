---
description: Start one ready OMG development source by ID, including publication and closure.
---

User request: $ARGUMENTS

Load `omg-orchestrator` and `omg-gc`. If the arguments ask only to inspect status, observe without launching. Otherwise resolve exactly one source ID and project from the arguments; if missing or ambiguous ask one choice question. This launch invocation authorizes one complete `omg-development` cycle, including direct push to origin/main and source closure after review. Follow the manual launch and prior-workflow checks in `omg-gc`; show any live run, reconcile failed runs explicitly, and never ask for another launch or publication confirmation. No next task is authorized.
