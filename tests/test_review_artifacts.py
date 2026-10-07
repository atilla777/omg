"""The review gate decides only from the current attempt's Beads outcome."""

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


def step(name, attempt, value, *, root="root", outcome="pass", status="closed"):
    key = "omg.review.verdict" if name == "review" else "omg.review.fix_status"
    return {"id": f"{name}-{attempt}", "status": status, "metadata": {
        "gc.root_bead_id": root, "gc.attempt": str(attempt),
        "gc.step_ref": f"omg-development.review-loop.iteration.{attempt}.{name}",
        "gc.outcome": outcome, key: value,
        **({"omg.review.schema": "omg.review.v2"} if name == "review" else {})}}


class ReviewGateTests(unittest.TestCase):
    def run_gate(self, rows, attempt="1"):
        def output(command, text):
            if "show" in command:
                return json.dumps([{"id": "control", "metadata": {"gc.root_bead_id": "root"}}])
            self.assertEqual(command[command.index("--metadata-field") + 1], "gc.root_bead_id=root")
            return json.dumps(rows)

        with patch.object(gate.subprocess, "check_output", side_effect=output), patch.dict(os.environ, {
                "GC_STORE_PATH": "/unused", "GC_BEAD_ID": "control", "GC_ITERATION": attempt}):
            return gate.main()

    def test_fixed_attempt_retries_then_latest_approved_attempt_passes(self):
        rows = [step("review", 1, "changes_required"), step("apply-fixes", 1, "applied"),
                step("review", 2, "approved"), step("apply-fixes", 2, "no_op")]
        self.assertEqual(self.run_gate(rows), 1)
        self.assertEqual(self.run_gate(rows, "2"), 0)

    def test_wrong_attempt_root_or_step_cannot_approve(self):
        rows = [step("review", 1, "approved"), step("apply-fixes", 2, "no_op")]
        with self.assertRaises(ValueError):
            self.run_gate(rows)
        rows[1] = step("apply-fixes", 1, "no_op", root="other")
        with self.assertRaises(ValueError):
            self.run_gate(rows)
        rows[1] = step("apply-fixes", 1, "no_op")
        rows.append(step("review", 1, "approved"))
        with self.assertRaises(ValueError):
            self.run_gate(rows)

    def test_incomplete_or_inconsistent_outcome_does_not_approve(self):
        for rows in ([step("review", 1, "approved"), step("apply-fixes", 1, "applied")],
                     [step("review", 1, "approved"), step("apply-fixes", 1, "no_op", status="open")],
                     [step("review", 1, "approved", outcome="fail"), step("apply-fixes", 1, "no_op")],
                     [step("review", 1, "approved"), step("apply-fixes", 1, None)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.run_gate(rows)

    def test_v1_review_is_not_approved(self):
        rows = [step("review", 1, "approved"), step("apply-fixes", 1, "no_op")]
        rows[0]["metadata"]["omg.review.schema"] = "omg.review.v1"
        with self.assertRaises(ValueError):
            self.run_gate(rows)

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
                report = worktree / ".omg/tasks" / source / "artifacts/review/attempt-1/review.json"
                report.parent.mkdir(parents=True)
                report.write_text(source)
                self.assertEqual(subprocess.run(["git", "-C", str(worktree), "check-ignore", "-q", str(report)]).returncode, 0)
                self.assertEqual(subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"],
                                                check=True, capture_output=True, text=True).stdout, "")
                paths.append(report)
            self.assertNotEqual(paths[0], paths[1])
            self.assertNotEqual(paths[0].read_text(), paths[1].read_text())


if __name__ == "__main__":
    unittest.main()
