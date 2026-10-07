#!/usr/bin/env python3
"""Close an OMG epic only after all direct source children are complete."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


class Blocked(Exception):
    pass


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode:
        raise Blocked(f"{' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def issue(rig, issue_id):
    rows = json.loads(run("bd", "-C", rig, "show", issue_id, "--json"))
    if len(rows) != 1 or rows[0].get("id") != issue_id:
        raise Blocked(f"cannot uniquely read issue {issue_id}")
    return rows[0]


def metadata(row, key):
    return (row.get("metadata") or {}).get(key)


def publication(rig, child, rows, remote_sha):
    child_id = child["id"]
    commit = metadata(child, "omg.publish.commit")
    report = metadata(child, "omg.publish.report_path")
    if not commit or not report or metadata(child, "omg.publish.status") != "published":
        raise Blocked(f"{child_id}: missing confirmed publication on source")
    if metadata(child, "gc.outcome") != "pass":
        raise Blocked(f"{child_id}: source outcome is not pass")

    roots = [row for row in rows if metadata(row, "gc.kind") == "workflow"
             and metadata(row, "gc.var.source_id") == child_id
             and metadata(row, "omg.publish.commit") == commit
             and metadata(row, "omg.publish.report_path") == report
             and metadata(row, "omg.publish.status") == "published"]
    if len(roots) != 1 or metadata(roots[0], "gc.formula_name") != "omg-development":
        raise Blocked(f"{child_id}: no unique development workflow with matching publication")
    root_id = roots[0]["id"]
    steps = [row for row in rows if metadata(row, "gc.root_bead_id") == root_id
             and metadata(row, "gc.step_id") == "omg-development.publish"]
    if len(steps) != 1:
        raise Blocked(f"{child_id}: no unique publish step for {root_id}")
    step = issue(rig, steps[0]["id"])
    if (step.get("status") != "closed" or metadata(step, "gc.outcome") != "pass"
            or metadata(step, "omg.publish.status") != "published"
            or metadata(step, "omg.publish.commit") != commit
            or metadata(step, "omg.publish.report_path") != report):
        raise Blocked(f"{child_id}: publish step is not closed with matching confirmation")
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise Blocked(f"{child_id}: invalid publication SHA")
    if subprocess.run(("git", "-C", rig, "merge-base", "--is-ancestor", commit,
                       remote_sha), capture_output=True).returncode:
        raise Blocked(f"{child_id}: published commit {commit} is not in origin/main")
    return commit


def close_epic(rig, source_id):
    source = issue(rig, source_id)
    parent_id = source.get("parent")
    if not parent_id:
        return {"state": "no_parent", "source_id": source_id}
    epic = issue(rig, parent_id)
    if epic.get("issue_type") != "epic":
        raise Blocked(f"{parent_id}: parent is not an epic")
    children = json.loads(run("bd", "-C", rig, "list", "--parent", parent_id,
                              "--all", "--flat", "--limit", "0", "--json"))
    children = [row for row in children if row.get("parent") == parent_id]
    if not children or source_id not in {row["id"] for row in children}:
        raise Blocked(f"{parent_id}: missing direct children or source {source_id}")
    if epic.get("status") == "closed":
        # Another actor may have added children after closure: do not claim they were checked.
        if any(row.get("updated_at", "") > epic.get("closed_at", "") for row in children):
            raise Blocked(f"{parent_id}: children changed after epic was closed; manual review required")
        return {"state": "already_closed", "epic_id": parent_id}

    # Read every child afresh; the list alone can omit metadata and is not evidence of publication.
    children = [issue(rig, row["id"]) for row in children]
    if any(child.get("parent") != parent_id for child in children):
        raise Blocked(f"{parent_id}: child parent changed during inspection")
    for child in children:
        if child.get("issue_type") not in ("omg-development", "omg-research", "omg-bugfix"):
            raise Blocked(f"{child['id']}: unsupported child type")
        if child.get("status") != "closed":
            raise Blocked(f"{child['id']}: child is {child.get('status')}, not closed")

    commits = {}
    if any(child["issue_type"] == "omg-development" for child in children):
        remote = run("git", "-C", rig, "ls-remote", "origin", "refs/heads/main").split()
        if len(remote) != 2 or remote[1] != "refs/heads/main":
            raise Blocked("cannot verify origin/main")
        run("git", "-C", rig, "fetch", "origin", "main")
        if run("git", "-C", rig, "rev-parse", "FETCH_HEAD") != remote[0]:
            raise Blocked("origin/main moved during verification")
        rows = json.loads(run("bd", "-C", rig, "list", "--all", "--include-infra",
                              "--limit", "0", "--flat", "--json"))
        for child in children:
            if child["issue_type"] == "omg-development":
                commits[child["id"]] = publication(rig, child, rows, remote[0])

    # Recheck graph and publication metadata before the final write. bd close without --force
    # also refuses open children and live blockers; it is not an atomic Git/Beads transaction.
    current = json.loads(run("bd", "-C", rig, "list", "--parent", parent_id,
                             "--all", "--flat", "--limit", "0", "--json"))
    if {row["id"] for row in current if row.get("parent") == parent_id} != {c["id"] for c in children}:
        raise Blocked(f"{parent_id}: children changed during verification")
    for child in children:
        fresh = issue(rig, child["id"])
        if fresh.get("parent") != parent_id or fresh.get("status") != "closed":
            raise Blocked(f"{child['id']}: state changed during verification")
        if child["id"] in commits and any(metadata(fresh, key) != metadata(child, key)
                                           for key in ("omg.publish.commit", "omg.publish.report_path",
                                                       "omg.publish.status", "gc.outcome")):
            raise Blocked(f"{child['id']}: publication changed during verification")
    if issue(rig, parent_id).get("status") == "closed":
        return {"state": "already_closed", "epic_id": parent_id}
    run("bd", "-C", rig, "close", parent_id, "--reason",
        "OMG: all direct source children closed; development commits verified in origin/main")
    if issue(rig, parent_id).get("status") != "closed":
        raise Blocked(f"{parent_id}: closure not confirmed")
    return {"state": "closed", "epic_id": parent_id,
            "children": [child["id"] for child in children], "commits": commits}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rig", required=True, help="absolute path to selected rig")
    parser.add_argument("--source", required=True, help="closed source bead ID")
    args = parser.parse_args()
    try:
        if not Path(args.rig).is_absolute() or not Path(args.rig).is_dir():
            raise Blocked("rig must be an existing absolute directory")
        result = close_epic(args.rig, args.source)
    except (Blocked, ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"state": "blocked", "source_id": args.source, "reason": str(error)}))
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
