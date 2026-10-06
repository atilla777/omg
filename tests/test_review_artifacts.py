"""Recorded Beads workspace and attempt paths used by the review gate."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


CHECK = Path(__file__).resolve().parents[1] / "packs/omg/assets/checks/omg-review-approved.py"
spec = importlib.util.spec_from_file_location("omg_review_gate", CHECK)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def artifacts(worktree, source):
    return worktree / ".omg" / "tasks" / source / "artifacts"


class ReviewContractTests(unittest.TestCase):
    def test_git_worktrees_isolate_ignored_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            rig = Path(tmp) / "rig"
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
            paths = []
            for source in ("OMG-123", "OMG-124"):
                worktree = Path(tmp) / source
                git("worktree", "add", "-b", f"task/{source}", str(worktree), "main")
                report = artifacts(worktree, source) / "review/attempt-1/review.json"
                report.parent.mkdir(parents=True)
                report.write_text(source)
                self.assertEqual(subprocess.run(["git", "-C", str(worktree), "check-ignore", "-q", str(report)]).returncode, 0)
                self.assertEqual(subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"],
                                                check=True, capture_output=True, text=True).stdout, "")
                paths.append(report)
            self.assertNotEqual(paths[0], paths[1])
            self.assertNotEqual(paths[0].read_text(), paths[1].read_text())

    def test_two_attempts_and_exact_producer_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp)
            source = "OMG-123"
            root_id = "root-1"
            base = artifacts(worktree, source)
            root = {"id": root_id, "metadata": {"gc.var.source_id": source, "omg.workspace.path": tmp,
                    "omg.workspace.source_id": source, "omg.workspace.artifacts_root": str(base)}}
            control = {"metadata": {"gc.root_bead_id": root_id}}
            members = []
            for number, verdict in ((1, "changes_required"), (2, "approved")):
                attempt_dir = base / "review" / f"attempt-{number}"
                attempt_dir.mkdir(parents=True)
                beads = {}
                names = {"review": ("omg.review.report_path", "review.json"),
                         "synthesize-review": ("omg.review.synthesis_path", "synthesis.json"),
                         "apply-fixes": ("omg.review.fix_path", "fix.json")}
                for step, (key, filename) in names.items():
                    beads[step] = {"id": f"{step}-{number}", "status": "closed", "metadata": {
                        "gc.root_bead_id": root_id, "gc.attempt": str(number),
                        "gc.step_ref": f"review-loop.iteration.{number}.{step}", "gc.outcome": "pass",
                        key: str(attempt_dir / filename)}}
                    members.append(beads[step])
                identity = {"attempt": number, "source_id": source, "workflow_root_id": root_id}
                markdown = attempt_dir / "review.md"
                markdown.write_text(f"# Review {number}\n")
                beads["review"]["metadata"]["omg.review.markdown_path"] = str(markdown)
                (attempt_dir / "review.json").write_text(json.dumps({**identity, "schema": "omg.review.v1",
                    "review_step_id": beads["review"]["id"], "verdict": verdict,
                    "findings": [] if number == 2 else [{"id": "F1"}],
                    "markdown_report_path": str(markdown.relative_to(worktree)),
                    "reviewed_files": {"src/code.py": "a" * 64}}))
                (attempt_dir / "synthesis.json").write_text(json.dumps({**identity,
                    "schema": "omg.review-synthesis.v1", "verdict": verdict,
                    "review_step_id": beads["review"]["id"],
                    "synthesis_step_id": beads["synthesize-review"]["id"],
                    "review_report_path": str((attempt_dir / "review.json").relative_to(worktree)),
                    "required_fixes": [] if number == 2 else [{"finding_ids": ["F1"]}]}))
                (attempt_dir / "fix.json").write_text(json.dumps({**identity,
                    "schema": "omg.review-fix.v1", "synthesis_step_id": beads["synthesize-review"]["id"],
                    "fix_step_id": beads["apply-fixes"]["id"],
                    "status": "no_op" if number == 2 else "applied",
                    "addressed_finding_ids": [] if number == 2 else ["F1"],
                    "tests": [] if number == 2 else [{"outcome": "pass"}]}))

            def read_json(args):
                if "list" in args:
                    return members
                return [{"control-1": control, root_id: root}[args[4]]]

            with patch.object(gate, "read_json", side_effect=read_json), patch.dict(os.environ, {
                    "GC_STORE_PATH": tmp, "GC_BEAD_ID": "control-1", "GC_ITERATION": "1"}):
                self.assertEqual(gate.main(), 1)
                with patch.dict(os.environ, {"GC_ITERATION": "2"}):
                    self.assertEqual(gate.main(), 0)
                    members[3]["metadata"]["omg.review.report_path"] = str(base / "review/attempt-1/review.json")
                    with self.assertRaises(ValueError):
                        gate.main()
                    members[3]["metadata"]["omg.review.report_path"] = str(base / "review/attempt-2/review.json")
                    root["metadata"]["omg.workspace.source_id"] = "OMG-124"
                    with self.assertRaises(ValueError):
                        gate.main()
                    root["metadata"]["omg.workspace.source_id"] = source
                    root["metadata"]["omg.workspace.artifacts_root"] = str(artifacts(worktree, "OMG-124"))
                    with self.assertRaises(ValueError):
                        gate.main()
                    root["metadata"]["omg.workspace.artifacts_root"] = str(base)
                    members[3]["metadata"]["omg.review.markdown_path"] = str(base / "review/attempt-1/review.md")
                    with self.assertRaises(ValueError):
                        gate.main()
                    members[3]["metadata"]["omg.review.markdown_path"] = str(base / "review/attempt-2/review.md")
                    del root["metadata"]["omg.workspace.artifacts_root"]
                    # Missing metadata is supported only for a genuinely legacy workflow.
                    with self.assertRaises(ValueError):
                        gate.main()

    def test_symlink_and_parent_escape_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            worktree = Path(tmp)
            source = "OMG-123"
            root = {"metadata": {"gc.var.source_id": source, "omg.workspace.path": tmp,
                    "omg.workspace.source_id": source, "omg.workspace.artifacts_root": str(artifacts(worktree, source))}}
            control = {"metadata": {"gc.root_bead_id": "root"}}

            def read_json(args):
                return [{"control": control, "root": root}[args[4]]]

            with patch.object(gate, "read_json", side_effect=read_json), patch.dict(os.environ, {
                    "GC_STORE_PATH": tmp, "GC_BEAD_ID": "control", "GC_ITERATION": "1"}):
                root["metadata"]["omg.workspace.artifacts_root"] = str(worktree / ".." / "elsewhere")
                with self.assertRaises(ValueError):
                    gate.main()
                task_dir = worktree / ".omg/tasks" / source
                task_dir.mkdir(parents=True)
                (task_dir / "artifacts").symlink_to(outside, target_is_directory=True)
                root["metadata"]["omg.workspace.artifacts_root"] = str(artifacts(worktree, source))
                with self.assertRaises(ValueError):
                    gate.main()
                (task_dir / "artifacts").unlink()
                attempt_dir = artifacts(worktree, source) / "review/attempt-1"
                attempt_dir.mkdir(parents=True)
                (attempt_dir / "review.json").symlink_to(Path(outside) / "report.json")
                (Path(outside) / "report.json").write_text("{}")
                members = [{"id": step, "status": "closed", "metadata": {
                    "gc.root_bead_id": "root", "gc.attempt": "1",
                    "gc.step_ref": f"review-loop.iteration.1.{step}", "gc.outcome": "pass",
                    key: str(attempt_dir / name)}} for step, key, name in (
                        ("review", "omg.review.report_path", "review.json"),
                        ("synthesize-review", "omg.review.synthesis_path", "synthesis.json"),
                        ("apply-fixes", "omg.review.fix_path", "fix.json"))]

                def read_with_members(args):
                    if "list" in args:
                        return members
                    return read_json(args)

                with patch.object(gate, "read_json", side_effect=read_with_members), self.assertRaises(ValueError):
                    gate.main()

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
            identity = {"attempt": 1, "source_id": "OMG-123", "workflow_root_id": "root"}
            (attempt_dir / "review.json").write_text(json.dumps({**identity, "schema": "omg.review.v1",
                "review_step_id": "review", "verdict": "approved", "findings": []}))
            (attempt_dir / "synthesis.json").write_text(json.dumps({**identity,
                "schema": "omg.review-synthesis.v1", "review_step_id": "review", "synthesis_step_id": "synthesize-review",
                "review_report_path": "docs/tasks/OMG-123/review/attempt-1/review.json",
                "verdict": "approved", "required_fixes": []}))
            (attempt_dir / "fix.json").write_text(json.dumps({**identity, "schema": "omg.review-fix.v1",
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
