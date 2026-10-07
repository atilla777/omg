#!/usr/bin/env python3
"""Return the current review/fix attempt's verdict to the Gas City check controller."""

import json
import os
import subprocess
import sys


def bead(store, bead_id):
    rows = json.loads(subprocess.check_output(["bd", "-C", store, "show", bead_id, "--json"], text=True))
    if len(rows) != 1 or rows[0]["id"] != bead_id:
        raise ValueError(f"expected one bead {bead_id}")
    return rows[0]


def main():
    store = os.environ["GC_STORE_PATH"]
    control = bead(store, os.environ["GC_BEAD_ID"])
    attempt = os.environ["GC_ITERATION"]
    if not attempt.isdecimal() or int(attempt) < 1:
        raise ValueError("invalid review attempt")
    root_id = control["metadata"]["gc.root_bead_id"]
    rows = json.loads(subprocess.check_output([
        "bd", "-C", store, "list", "--all", "--include-infra",
        "--metadata-field", f"gc.root_bead_id={root_id}", "--limit", "0", "--json",
    ], text=True))

    def result(step, key):
        matches = [row for row in rows if row.get("metadata", {}).get("gc.root_bead_id") == root_id
                   and row["metadata"].get("gc.attempt") == attempt
                   and row["metadata"].get("gc.step_ref", "").endswith(
                       f"review-loop.iteration.{attempt}.{step}")]
        if len(matches) != 1 or matches[0]["status"] != "closed" or matches[0]["metadata"].get("gc.outcome") != "pass":
            raise ValueError(f"expected one passing closed {step} bead for attempt {attempt}")
        return matches[0]["metadata"].get(key)

    if result("review", "omg.review.schema") != "omg.review.v2":
        raise ValueError("review gate requires direct v2 review")
    verdict = result("review", "omg.review.verdict")
    status = result("apply-fixes", "omg.review.fix_status")
    if verdict == "approved" and status == "no_op":
        print(f"review attempt {attempt} approved")
        return 0
    if verdict == "changes_required" and status == "applied":
        print(f"review attempt {attempt} fixed; new review required")
        return 1
    raise ValueError("missing or inconsistent review/fix outcome")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, ValueError, TypeError) as error:
        print(f"omg review gate: {error}", file=sys.stderr)
        sys.exit(1)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"omg review gate: infrastructure unavailable: {error}", file=sys.stderr)
        sys.exit(75)
