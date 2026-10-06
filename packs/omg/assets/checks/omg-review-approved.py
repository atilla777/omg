#!/usr/bin/env python3
"""Runtime verdict gate for one OMG development review iteration."""

import json
import os
import re
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
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", source_id) or source_id in (".", ".."):
        raise ValueError("unsafe source ID")
    recorded_worktree = Path(root["metadata"]["omg.workspace.path"])
    if not recorded_worktree.is_absolute() or not recorded_worktree.is_dir() or recorded_worktree.resolve() != recorded_worktree:
        raise ValueError("invalid recorded worktree")
    worktree = recorded_worktree
    # Existing runs have no artifacts_root metadata and retain their recorded paths.
    legacy = "omg.workspace.artifacts_root" not in root["metadata"]
    if not attempt.isdecimal() or int(attempt) < 1:
        raise ValueError("invalid review attempt")
    if legacy:
        artifacts_root = worktree / "docs" / "tasks" / source_id
    else:
        if root["metadata"].get("omg.workspace.source_id") != source_id:
            raise ValueError("prepared source ID does not match workflow")
        artifacts_root = Path(root["metadata"]["omg.workspace.artifacts_root"])
        if (not artifacts_root.is_absolute() or artifacts_root != worktree / ".omg" / "tasks" / source_id / "artifacts"
                or artifacts_root.resolve() != artifacts_root):
            raise ValueError("task artifacts root does not match prepared worktree")
    attempt_dir = artifacts_root / "review" / f"attempt-{attempt}"
    if attempt_dir.resolve() != attempt_dir or not attempt_dir.is_relative_to(worktree):
        raise ValueError("review attempt escapes prepared worktree")
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
        path = Path(bead["metadata"][key])
        if path != attempt_dir / filename or path.resolve() != path or not path.is_file():
            raise ValueError(f"{schema} must be in this attempt's worktree directory")
        data = json.loads(path.read_text())
        if (data.get("schema"), str(data.get("attempt")), data.get("source_id"),
                data.get("workflow_root_id")) != (schema, attempt, source_id, root_id):
            raise ValueError(f"invalid {schema} identity")
        return data

    report = artifact(review, "omg.review.report_path", "omg.review.v1", "review.json")
    if not legacy:
        markdown_path = attempt_dir / "review.md"
        if (Path(review["metadata"].get("omg.review.markdown_path", "")) != markdown_path
                or markdown_path.resolve() != markdown_path
                or report.get("markdown_report_path") != str(markdown_path.relative_to(worktree))
                or not markdown_path.is_file() or not markdown_path.read_text().strip()):
            raise ValueError("missing or mismatched human-readable review report")
    decision = artifact(synthesis, "omg.review.synthesis_path", "omg.review-synthesis.v1", "synthesis.json")
    result = artifact(fix, "omg.review.fix_path", "omg.review-fix.v1", "fix.json")
    review_path = review["metadata"]["omg.review.report_path"]
    portable_review_path = (f"docs/tasks/{source_id}/review/attempt-{attempt}/review.json" if legacy else f".omg/tasks/{source_id}/artifacts/review/attempt-{attempt}/review.json")
    if (report.get("review_step_id") != review["id"]
            or decision.get("review_step_id") != review["id"]
            or decision.get("synthesis_step_id") != synthesis["id"]
            or decision.get("review_report_path") not in (review_path, portable_review_path)
            or decision.get("verdict") != report.get("verdict")):
        raise ValueError("synthesis does not match this attempt's review")
    if (result.get("synthesis_step_id") != synthesis["id"]
            or result.get("fix_step_id") != fix["id"]
            or result.get("status") not in ("applied", "no_op")):
        raise ValueError("fix does not reference this attempt's synthesis")
    if decision.get("verdict") == "approved" and result["status"] == "no_op":
        if report.get("findings") or decision.get("required_fixes"):
            raise ValueError("approval still contains required findings")
        if not legacy:
            files = report.get("reviewed_files")
            if (not isinstance(files, dict) or not files or any(
                not isinstance(name, str) or not name or Path(name).is_absolute()
                or any(part in (".", "..") for part in Path(name).parts)
                or name.startswith((".omg/", "docs/tasks/"))
                or (digest is not None and (not isinstance(digest, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", digest)))
                for name, digest in files.items()
            )):
                raise ValueError("approved review lacks a valid reviewed_files snapshot")
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
