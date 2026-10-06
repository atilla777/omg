"""Workspace isolation and the review gate's recorded producer/consumer contract."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "packs" / "omg" / "assets"


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


workspace_module = module(SCRIPTS / "scripts" / "task_workspace.py", "task_workspace")
gate = module(SCRIPTS / "checks" / "omg-review-approved.py", "omg_review_gate")


class WorkspaceTests(unittest.TestCase):
    def test_isolation_and_safe_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = workspace_module.TaskWorkspace(tmp, "OMG-123")
            second = workspace_module.TaskWorkspace(tmp, "OMG-124")
            first.artifacts_root().mkdir(parents=True)
            second.artifacts_root().mkdir(parents=True)
            self.assertEqual(first.artifact_path("plan.md"), Path(tmp) / ".omg/tasks/OMG-123/artifacts/plan.md")
            self.assertNotEqual(first.artifacts_root(), second.artifacts_root())
            self.assertNotEqual(first.attempt_path(1, "review.json"), first.attempt_path(2, "review.json"))
            for invalid in ("../foo", "other/../../review.json", "/tmp/review.json"):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    first.artifact_path(invalid)
            with self.assertRaises(ValueError):
                workspace_module.TaskWorkspace(tmp, "../outside")
            with self.assertRaises(ValueError):
                first.attempt_path(0, "review.json")
            with tempfile.TemporaryDirectory() as outside:
                (first.artifacts_root() / "external").symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    first.artifact_path("external/report.md")

    def test_git_worktrees_ignore_task_artifacts_and_isolate_them(self):
        with tempfile.TemporaryDirectory() as tmp:
            rig = Path(tmp) / "project"
            rig.mkdir()

            def git(*args):
                return subprocess.run(["git", "-C", str(rig), *args], check=True, text=True,
                                      capture_output=True).stdout.strip()

            git("init", "-b", "main")
            (rig / "README.md").write_text("example\n")
            git("add", "README.md")
            git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "base")
            exclude = Path(git("rev-parse", "--git-path", "info/exclude"))
            if not exclude.is_absolute():
                exclude = rig / exclude
            with exclude.open("a") as output:
                output.write("\n/.omg/\n")
            worktrees = [Path(tmp) / "OMG-123", Path(tmp) / "OMG-124"]
            for path in worktrees:
                git("worktree", "add", "-b", "task/" + path.name, str(path), "main")
                artifact = workspace_module.TaskWorkspace(path, path.name).artifact_path("review/attempt-1/review.json")
                artifact.parent.mkdir(parents=True)
                artifact.write_text(path.name)
                check = subprocess.run(["git", "-C", str(path), "check-ignore", "-q", str(artifact)])
                self.assertEqual(check.returncode, 0)
                status = subprocess.run(["git", "-C", str(path), "status", "--porcelain"],
                                        check=True, capture_output=True, text=True)
                self.assertEqual(status.stdout, "")
            self.assertNotEqual(workspace_module.TaskWorkspace(worktrees[0], "OMG-123").artifacts_root(),
                                workspace_module.TaskWorkspace(worktrees[1], "OMG-124").artifacts_root())


class ReviewContractTests(unittest.TestCase):
    def test_review_attempts_follow_bead_references_and_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            ws = workspace_module.TaskWorkspace(tmp, "OMG-123")
            root_id = "root-1"
            root = {"id": root_id, "metadata": {"gc.var.source_id": "OMG-123",
                    "omg.workspace.path": tmp, "omg.workspace.artifacts_root": str(ws.artifacts_root())}}
            control = {"metadata": {"gc.root_bead_id": root_id}}
            members = []
            for number, verdict in ((1, "changes_required"), (2, "approved")):
                attempt = str(number)
                beads = {}
                for step, key in (("review", "omg.review.report_path"),
                                  ("synthesize-review", "omg.review.synthesis_path"),
                                  ("apply-fixes", "omg.review.fix_path")):
                    beads[step] = {"id": f"{step}-{number}", "status": "closed", "metadata": {
                        "gc.root_bead_id": root_id, "gc.attempt": attempt,
                        "gc.step_ref": f"review-loop.iteration.{attempt}.{step}", "gc.outcome": "pass",
                        key: str(ws.attempt_path(number, {"review": "review.json", "synthesize-review": "synthesis.json", "apply-fixes": "fix.json"}[step]))}}
                    members.append(beads[step])
                base = {"attempt": number, "source_id": "OMG-123", "workflow_root_id": root_id}
                review = {**base, "schema": "omg.review.v1", "review_step_id": beads["review"]["id"],
                          "verdict": verdict, "findings": [] if number == 2 else [{"id": "F1"}],
                          "markdown_report_path": str(ws.attempt_path(number, "review.md").relative_to(tmp)),
                          "reviewed_files": {"src/code.py": "a" * 64}}
                beads["review"]["metadata"]["omg.review.markdown_path"] = str(ws.attempt_path(number, "review.md"))
                synthesis = {**base, "schema": "omg.review-synthesis.v1", "verdict": verdict,
                             "review_step_id": beads["review"]["id"],
                             "synthesis_step_id": beads["synthesize-review"]["id"],
                             "review_report_path": str(ws.attempt_path(number, "review.json").relative_to(tmp)),
                             "required_fixes": [] if number == 2 else [{"finding_ids": ["F1"]}]}
                fix = {**base, "schema": "omg.review-fix.v1", "synthesis_step_id": beads["synthesize-review"]["id"],
                       "fix_step_id": beads["apply-fixes"]["id"], "status": "no_op" if number == 2 else "applied",
                       "addressed_finding_ids": [] if number == 2 else ["F1"],
                       "tests": [] if number == 2 else [{"outcome": "pass"}]}
                for step, contents in (("review", review), ("synthesize-review", synthesis), ("apply-fixes", fix)):
                    name = {"review": "review.json", "synthesize-review": "synthesis.json", "apply-fixes": "fix.json"}[step]
                    path = ws.attempt_path(number, name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(contents))
                ws.attempt_path(number, "review.md").write_text(f"# Review attempt {number}\n\n{verdict}\n")

            def read_json(args):
                if "list" in args:
                    return members
                return [{"control-1": control, root_id: root}[args[4]]]

            with patch.object(gate, "read_json", side_effect=read_json), patch.dict(os.environ, {
                    "GC_STORE_PATH": tmp, "GC_BEAD_ID": "control-1"}):
                with patch.dict(os.environ, {"GC_ITERATION": "1"}):
                    self.assertEqual(gate.main(), 1)
                with patch.dict(os.environ, {"GC_ITERATION": "2"}):
                    self.assertEqual(gate.main(), 0)
                with patch.dict(os.environ, {"GC_ITERATION": "2"}):
                    members[3]["metadata"]["omg.review.markdown_path"] = str(ws.attempt_path(1, "review.md"))
                    with self.assertRaises(ValueError):
                        gate.main()
                    members[3]["metadata"]["omg.review.markdown_path"] = str(ws.attempt_path(2, "review.md"))
                # Producer metadata is authoritative: a path from another attempt is rejected.
                members[3]["metadata"]["omg.review.report_path"] = str(ws.attempt_path(1, "review.json"))
                with patch.dict(os.environ, {"GC_ITERATION": "2"}), self.assertRaises(ValueError):
                    gate.main()
            self.assertEqual(json.loads(ws.attempt_path(1, "review.json").read_text())["verdict"], "changes_required")

    def test_legacy_review_directory_remains_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            attempt_dir = Path(tmp) / "docs/tasks/OMG-123/review/attempt-1"
            attempt_dir.mkdir(parents=True)
            root = {"id": "root", "metadata": {"gc.var.source_id": "OMG-123", "omg.workspace.path": tmp}}
            keys = (("review", "omg.review.report_path", "review.json"),
                    ("synthesize-review", "omg.review.synthesis_path", "synthesis.json"),
                    ("apply-fixes", "omg.review.fix_path", "fix.json"))
            members = [{"id": name, "status": "closed", "metadata": {
                "gc.root_bead_id": "root", "gc.attempt": "1", "gc.step_ref": f"review-loop.iteration.1.{name}",
                "gc.outcome": "pass", key: str(attempt_dir / filename)}} for name, key, filename in keys]
            base = {"attempt": 1, "source_id": "OMG-123", "workflow_root_id": "root"}
            (attempt_dir / "review.json").write_text(json.dumps({**base, "schema": "omg.review.v1",
                "review_step_id": "review", "verdict": "approved", "findings": []}))
            (attempt_dir / "synthesis.json").write_text(json.dumps({**base,
                "schema": "omg.review-synthesis.v1", "review_step_id": "review", "synthesis_step_id": "synthesize-review",
                "review_report_path": "docs/tasks/OMG-123/review/attempt-1/review.json",
                "verdict": "approved", "required_fixes": []}))
            (attempt_dir / "fix.json").write_text(json.dumps({**base, "schema": "omg.review-fix.v1",
                "synthesis_step_id": "synthesize-review", "fix_step_id": "apply-fixes", "status": "no_op"}))

            def read_json(args):
                if "list" in args:
                    return members
                return [{"ctrl": {"metadata": {"gc.root_bead_id": "root"}}, "root": root}[args[4]]]

            with patch.object(gate, "read_json", side_effect=read_json), patch.dict(os.environ, {
                    "GC_STORE_PATH": tmp, "GC_BEAD_ID": "ctrl", "GC_ITERATION": "1"}):
                self.assertEqual(gate.main(), 0)


if __name__ == "__main__":
    unittest.main()
