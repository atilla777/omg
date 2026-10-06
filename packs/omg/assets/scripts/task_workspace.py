#!/usr/bin/env python3
"""Resolve task-local OMG operational artifacts inside a verified worktree."""

import argparse
from pathlib import Path
import re


def safe_component(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value) or value in (".", ".."):
        raise ValueError(f"unsafe task or artifact component: {value!r}")
    return value


class TaskWorkspace:
    def __init__(self, worktree, task_id):
        self.project = Path(worktree).resolve(strict=True)
        if not self.project.is_dir():
            raise ValueError("worktree must be a directory")
        self.task_id = safe_component(task_id)

    def _inside(self, path):
        resolved = path.resolve()
        if not resolved.is_relative_to(self.project):
            raise ValueError("artifact path escapes the worktree")
        return resolved

    def task_root(self):
        return self._inside(self.project / ".omg" / "tasks" / self.task_id)

    def artifacts_root(self):
        return self._inside(self.task_root() / "artifacts")

    def artifact_path(self, name):
        parts = Path(name).parts
        if not parts or Path(name).is_absolute():
            raise ValueError("artifact name must be relative")
        for part in parts:
            safe_component(part)
        return self._inside(self.artifacts_root().joinpath(*parts))

    def attempt_path(self, attempt, name):
        if not isinstance(attempt, int) or attempt < 1:
            raise ValueError("review attempt must be positive")
        return self.artifact_path(f"review/attempt-{attempt}/{safe_component(name)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--mkdir", action="store_true", help="create resolved directory or file parent")
    parser.add_argument("kind", choices=("task-root", "artifacts-root", "artifact", "attempt"))
    parser.add_argument("name", nargs="?")
    parser.add_argument("--attempt", type=int)
    args = parser.parse_args()
    try:
        workspace = TaskWorkspace(args.worktree, args.task)
        if args.kind == "task-root":
            path = workspace.task_root()
        elif args.kind == "artifacts-root":
            path = workspace.artifacts_root()
        elif args.kind == "artifact" and args.name:
            path = workspace.artifact_path(args.name)
        elif args.kind == "attempt" and args.name and args.attempt is not None:
            path = workspace.attempt_path(args.attempt, args.name)
        else:
            parser.error("artifact needs a name; attempt needs --attempt and a name")
        if args.mkdir:
            directory = path if args.kind.endswith("root") else path.parent
            directory.mkdir(parents=True, exist_ok=True)
        print(path)
    except (OSError, ValueError) as error:
        parser.exit(1, f"task workspace: {error}\n")


if __name__ == "__main__":
    main()
