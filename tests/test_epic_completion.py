"""Check the evidence gate for OMG epic completion."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "packs/omg/assets/checks/omg-close-epic.py"
spec = importlib.util.spec_from_file_location("omg_close_epic", SCRIPT)
epic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(epic)

SHA = "a" * 40


class PublicationTest(unittest.TestCase):
    def setUp(self):
        self.source = {"id": "rig-1.1", "metadata": {
            "omg.publish.commit": SHA, "omg.publish.report_path": "/rig/report.json",
            "omg.publish.status": "published", "gc.outcome": "pass"}}
        self.root = {"id": "rig-root", "metadata": {
            "gc.kind": "workflow", "gc.formula_name": "omg-development",
            "gc.var.source_id": "rig-1.1", "omg.publish.commit": SHA,
            "omg.publish.report_path": "/rig/report.json", "omg.publish.status": "published"}}
        self.step = {"id": "rig-step", "status": "closed", "metadata": {
            "gc.root_bead_id": "rig-root", "gc.step_id": "omg-development.publish",
            "gc.outcome": "pass", "omg.publish.commit": SHA,
            "omg.publish.report_path": "/rig/report.json", "omg.publish.status": "published"}}

    def check(self):
        with patch.object(epic, "issue", return_value=self.step), patch.object(
            epic.subprocess, "run", return_value=SimpleNamespace(returncode=0)
        ):
            return epic.publication("/rig", self.source, [self.root, self.step], SHA)

    def test_matching_closed_publish_and_remote_commit(self):
        self.assertEqual(self.check(), SHA)

    def test_closed_source_without_publish_step_is_insufficient(self):
        self.step["status"] = "open"
        with self.assertRaisesRegex(epic.Blocked, "publish step is not closed"):
            self.check()

    def test_mismatched_root_or_source_publication_is_insufficient(self):
        self.root["metadata"]["omg.publish.commit"] = "b" * 40
        with self.assertRaisesRegex(epic.Blocked, "no unique development workflow"):
            self.check()

    def test_missing_source_evidence_is_insufficient(self):
        del self.source["metadata"]["omg.publish.status"]
        with self.assertRaisesRegex(epic.Blocked, "missing confirmed publication"):
            self.check()

    def test_commit_must_be_ancestor_of_remote_main(self):
        with patch.object(epic, "issue", return_value=self.step), patch.object(
            epic.subprocess, "run", return_value=SimpleNamespace(returncode=1)
        ):
            with self.assertRaisesRegex(epic.Blocked, "not in origin/main"):
                epic.publication("/rig", self.source, [self.root, self.step], SHA)


if __name__ == "__main__":
    unittest.main()
