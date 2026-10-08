---
description: Start exactly one next ready OMG development source in the selected plan.
---

User request: $ARGUMENTS

Load `omg-orchestrator` and `omg-gc`. If the arguments ask only to inspect status, observe without launching. Otherwise resolve the project and epic plan from the arguments or context; ask one choice question if ambiguous. Use `omg-gc`'s documented next-task order, readiness, type, dependencies and complete prior-workflow checks. This launch invocation authorizes one complete `omg-development` cycle for that single source, including direct push to origin/main and source closure after review, without repeated confirmation. Show a live process rather than relaunching; never silently restart a failed one, use a different formula for unsupported types or launch the next task automatically.
