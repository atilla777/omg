#!/usr/bin/env python3
"""Runtime verdict gate for one OMG development review iteration."""

import json
import os
import subprocess
import sys
from pathlib import Path


def read_json(command):
    return json.loads(subprocess.check_output(command, text=True))


def one(rows):
    if isinstance(rows, list) and len(rows) == 1:
        return rows[0]
    raise ValueError("expected exactly one bead")


def main():
    store = os.environ["GC_STORE_PATH"]
    control_id = os.environ["GC_BEAD_ID"]
    attempt = os.environ["GC_ITERATION"]
    control = one(read_json(["bd", "-C", store, "show", control_id, "--json"]))
    root_id = control["metadata"]["gc.root_bead_id"]
    root = one(read_json(["bd", "-C", store, "show", root_id, "--json"]))
    source_id = root["metadata"]["gc.var.source_id"]
    worktree = Path(root["metadata"]["omg.workspace.path"]).resolve()
    attempt_dir = worktree / "docs" / "tasks" / source_id / "review" / f"attempt-{attempt}"
    members = read_json([
        "bd", "-C", store, "list", "--all", "--include-infra",
        "--metadata-field", f"gc.root_bead_id={root_id}", "--limit", "0", "--json",
    ])

    def member(step):
        matched = [
            item for item in members
            if item.get("metadata", {}).get("gc.root_bead_id") == root_id
            and item["metadata"].get("gc.attempt") == attempt
            and item["metadata"].get("gc.step_ref", "").endswith(f"review-loop.iteration.{attempt}.{step}")
        ]
        if (len(matched) != 1 or matched[0]["status"] != "closed"
                or matched[0]["metadata"].get("gc.outcome") != "pass"):
            raise ValueError(f"expected one passing closed {step} bead for attempt {attempt}")
        return matched[0]

    review = member("review")
    synthesis = member("synthesize-review")
    fix = member("apply-fixes")

    def artifact(bead, key, schema, filename):
        path = Path(bead["metadata"][key]).resolve()
        if path != attempt_dir / filename:
            raise ValueError(f"{schema} must be in this attempt's worktree directory")
        data = json.loads(path.read_text())
        if (data.get("schema"), str(data.get("attempt")), data.get("source_id"),
                data.get("workflow_root_id")) != (schema, attempt, source_id, root_id):
            raise ValueError(f"invalid {schema} identity")
        return data

    report = artifact(review, "omg.review.report_path", "omg.review.v1", "review.json")
    decision = artifact(synthesis, "omg.review.synthesis_path", "omg.review-synthesis.v1", "synthesis.json")
    result = artifact(fix, "omg.review.fix_path", "omg.review-fix.v1", "fix.json")
    if (report.get("review_step_id") != review["id"]
            or decision.get("review_step_id") != review["id"]
            or decision.get("synthesis_step_id") != synthesis["id"]
            or decision.get("review_report_path") != review["metadata"]["omg.review.report_path"]
            or decision.get("verdict") != report.get("verdict")):
        raise ValueError("synthesis does not match this attempt's review")
    if (result.get("synthesis_step_id") != synthesis["id"]
            or result.get("fix_step_id") != fix["id"]
            or result.get("status") not in ("applied", "no_op")):
        raise ValueError("fix does not reference this attempt's synthesis")
    if decision.get("verdict") == "approved" and result["status"] == "no_op":
        if report.get("findings") or decision.get("required_fixes"):
            raise ValueError("approval still contains required findings")
        print(f"review attempt {attempt} approved")
        return 0
    if decision.get("verdict") == "changes_required" and result["status"] == "applied":
        required = decision.get("required_fixes")
        if not isinstance(required, list) or not required:
            raise ValueError("changes_required has no mandatory fixes")
        ids = {finding_id for item in required for finding_id in item["finding_ids"]}
        tests = result.get("tests")
        if not ids.issubset(set(result.get("addressed_finding_ids", []))):
            raise ValueError("mandatory findings were not addressed")
        if not isinstance(tests, list) or not tests or any(test.get("outcome") != "pass" for test in tests):
            raise ValueError("fix has no passing test evidence")
        print(f"review attempt {attempt} fixed; new review required")
        return 1
    raise ValueError("blocked or inconsistent review/fix outcome")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyError, ValueError) as error:
        print(f"omg review gate: {error}", file=sys.stderr)
        sys.exit(1)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"omg review gate: infrastructure unavailable: {error}", file=sys.stderr)
        sys.exit(75)
