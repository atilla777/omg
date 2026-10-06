#!/usr/bin/env python3
"""Snapshot one reviewed worktree, then publish it to origin/main without force."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


class PublishError(Exception):
    pass


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True
    )
    if result.returncode:
        raise PublishError(f"git {' '.join(args)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def common_dir(repo):
    return (repo / git(repo, "rev-parse", "--git-common-dir")).resolve()


def changed_files(worktree):
    result = subprocess.run(
        ["git", "-C", str(worktree), "ls-files", "-m", "-o", "-d", "--exclude-standard", "-z"],
        capture_output=True, check=True,
    )
    return sorted({os.fsdecode(name) for name in result.stdout.split(b"\0") if name})


def digest(worktree, relative):
    path = worktree / relative
    if path.is_symlink():
        raise PublishError(f"symlink needs manual review: {relative}")
    if not path.exists():
        return None
    if not path.is_file():
        raise PublishError(f"not a regular file: {relative}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remote_main(repo):
    output = git(repo, "ls-remote", "--exit-code", "origin", "refs/heads/main")
    rows = output.splitlines()
    if len(rows) != 1 or len(rows[0].split()) != 2:
        raise PublishError("origin/main is missing or ambiguous")
    return rows[0].split()[0]


def ancestor(repo, older, newer):
    result = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
        capture_output=True, text=True,
    )
    if result.returncode not in (0, 1):
        raise PublishError(result.stderr.strip() or "cannot check commit ancestry")
    return result.returncode == 0


def verified_paths(args):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.source):
        raise PublishError("unsafe source ID")
    rig, worktree = Path(args.rig).resolve(), Path(args.worktree).resolve()
    if git(rig, "rev-parse", "--show-toplevel") != str(rig):
        raise PublishError("rig is not the repository root")
    if git(worktree, "rev-parse", "--show-toplevel") != str(worktree):
        raise PublishError("path is not the worktree root")
    if common_dir(worktree) != common_dir(rig):
        raise PublishError("worktree belongs to another repository")
    if git(worktree, "branch", "--show-current") != f"task/{args.source}":
        raise PublishError("worktree is not on the source branch")
    artifact_dir = worktree / "docs" / "tasks" / args.source
    if not artifact_dir.resolve().is_relative_to(worktree):
        raise PublishError("artifact directory escapes worktree")
    if Path(args.manifest).resolve() != artifact_dir / "publish-manifest.json":
        raise PublishError("manifest must be in this source's worktree")
    return rig, worktree, artifact_dir


def snapshot(args):
    rig, worktree, artifact_dir = verified_paths(args)
    if git(worktree, "rev-parse", "HEAD") != args.base_sha:
        raise PublishError("snapshot requires an uncommitted branch at the prepared base")
    files = changed_files(worktree)
    excluded = {"docs/tasks/" + args.source + "/publish-manifest.json"}
    files = [path for path in files if path not in excluded]
    if not files:
        raise PublishError("nothing to publish")
    for relative in files:
        if relative.startswith(f"docs/tasks/{args.source}/"):
            path = worktree / relative
            if digest(worktree, relative) is not None and (str(worktree).encode() in path.read_bytes()
                                  or str(rig).encode() in path.read_bytes()):
                raise PublishError(f"local machine path in publishable artifact: {relative}")
    data = {
        "schema": "omg.publish-manifest.v1", "source_id": args.source,
        "workflow_root_id": args.root, "review_loop_id": args.review_loop,
        "base_sha": args.base_sha,
        "files": {path: digest(worktree, path) for path in files},
    }
    Path(args.manifest).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"ok": True, "manifest": args.manifest, "files": len(files)}))


def read_manifest(args, worktree):
    manifest = json.loads(Path(args.manifest).read_text())
    if (manifest.get("schema"), manifest.get("source_id"), manifest.get("workflow_root_id")) != (
        "omg.publish-manifest.v1", args.source, args.root
    ):
        raise PublishError("manifest belongs to another source or workflow")
    if not manifest.get("review_loop_id") or not manifest.get("base_sha"):
        raise PublishError("manifest lacks review or base identity")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise PublishError("manifest has no files")
    for path, expected in files.items():
        if (not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts
                or path in ("", ".") or (expected is not None and not isinstance(expected, str))):
            raise PublishError("invalid manifest path or hash")
        if digest(worktree, path) != expected:
            raise PublishError(f"reviewed file changed after finalization: {path}")
    return manifest


def publish(args):
    rig, worktree, artifact_dir = verified_paths(args)
    lock_path = common_dir(rig) / "omg-publish.lock"
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = read_manifest(args, worktree)
        base = manifest["base_sha"]
        head = git(worktree, "rev-parse", "HEAD")
        report = artifact_dir / "publication-report.json"
        allowed = set(manifest["files"]) | {
            "docs/tasks/" + args.source + "/publish-manifest.json",
            "docs/tasks/" + args.source + "/publication-report.json",
        }
        unexpected = set(changed_files(worktree)) - allowed
        if unexpected:
            raise PublishError(f"unreviewed worktree changes: {sorted(unexpected)}")

        remote = remote_main(rig)
        if head == base:
            if remote != base or git(rig, "rev-parse", "main") != base:
                raise PublishError(f"stale main: prepared {base}, local {git(rig, 'rev-parse', 'main')}, remote {remote}; reconcile and review again")
            if git(worktree, "diff", "--cached", "--name-only"):
                raise PublishError("worktree index is not clean before staging")
            git(worktree, "add", "-A", "--", *sorted(set(manifest["files"]) | {"docs/tasks/" + args.source + "/publish-manifest.json"}))
            if not git(worktree, "diff", "--cached", "--name-only"):
                raise PublishError("no staged result to publish")
            git(worktree, "diff", "--cached", "--check")
            git(worktree, "commit", "-m", f"Implement {args.source}")
            head = git(worktree, "rev-parse", "HEAD")
        elif git(worktree, "rev-parse", "HEAD^") != base:
            raise PublishError("branch contains an unrecognized commit after the prepared base")

        if set(changed_files(worktree)) - {"docs/tasks/" + args.source + "/publication-report.json"}:
            raise PublishError("worktree changed after commit")
        if remote == base:
            git(worktree, "push", "origin", "HEAD:refs/heads/main")
        elif remote != head:
            git(rig, "fetch", "origin", "refs/heads/main:refs/remotes/origin/main")
            if not ancestor(rig, head, "refs/remotes/origin/main"):
                raise PublishError(f"remote main advanced before push: {remote}; no force push")

        git(rig, "fetch", "origin", "refs/heads/main:refs/remotes/origin/main")
        if not ancestor(rig, head, "refs/remotes/origin/main"):
            raise PublishError("published commit is not in remote main")
        git(rig, "merge", "--ff-only", "refs/remotes/origin/main")
        verified_remote = remote_main(rig)
        if git(rig, "rev-parse", "main") != verified_remote:
            raise PublishError("local main does not match the verified remote main")
        data = {"schema": "omg.publication.v1", "source_id": args.source,
                "workflow_root_id": args.root, "commit": head, "remote": "origin/main",
                "remote_sha": verified_remote, "local_main_sha": git(rig, "rev-parse", "main"),
                "manifest": str(Path(args.manifest).resolve()), "status": "published"}
        report.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        print(json.dumps(data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("snapshot", "publish"))
    parser.add_argument("--rig", required=True)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base-sha", help="required for snapshot")
    parser.add_argument("--review-loop", help="required for snapshot")
    args = parser.parse_args()
    if args.action == "snapshot":
        if not args.base_sha or not args.review_loop:
            parser.error("snapshot requires --base-sha and --review-loop")
        snapshot(args)
    else:
        publish(args)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError, PublishError) as error:
        print(f"omg publication: {error}", file=sys.stderr)
        sys.exit(1)
