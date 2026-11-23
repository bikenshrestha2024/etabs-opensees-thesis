"""Red/green regression for executed ESM runner identity.

Only synthetic temporary files. Never reads project native EDB or output.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.organized_exports import _latest_batch_status

CASE = "OpenSees_Direct_NBC105_ESM_Load_And_Static_Analysis_ULS_X+_E0_V111.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(root, *, recorded_hash=True, runner_path=None):
    script = root / CASE
    script.write_text("# synthetic runner A\n", encoding="utf-8")
    status_dir = root / "ESM_Runner_Status" / "20261123_100000"
    status_dir.mkdir(parents=True)
    row = {
        "case": CASE, "runner_path": str(runner_path or script),
        "status": "SUCCESS", "return_code": 0, "elapsed_s": 1.0,
    }
    if recorded_hash:
        row["runner_sha256"] = sha(script)
    (status_dir / "CASE_STATUS.json").write_text(
        json.dumps([row]), encoding="utf-8"
    )
    return script, status_dir / "CASE_STATUS.json"


class ExecutedRunnerIdentityTests(unittest.TestCase):
    def test_changed_runner_bytes_cannot_reuse_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script, manifest = fixture(root)
            self.assertEqual(_latest_batch_status(root)["status"], "COMPLETE_SOLVER_ONLY")
            script.write_text("# synthetic runner B\n", encoding="utf-8")
            result = _latest_batch_status(root)
            self.assertEqual(result["status"], "PARTIAL_OR_FAILED")
            self.assertEqual(result["completed"], 0)
            self.assertIn(CASE, result["missing_cases"])
            self.assertTrue(result["runner_identity_issues"])

    def test_historical_status_without_digest_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root, recorded_hash=False)
            result = _latest_batch_status(root)
            self.assertEqual(result["status"], "PARTIAL_OR_FAILED")
            self.assertEqual(result["completed"], 0)
            self.assertTrue(any("MISSING_RUNNER_SHA256" in x
                                for x in result["runner_identity_issues"]))

    def test_runner_path_must_belong_to_exact_selected_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outsider = root / "unrelated"
            outsider.mkdir()
            alien = outsider / CASE
            alien.write_text("# synthetic runner A\n", encoding="utf-8")
            fixture(root, runner_path=alien)
            result = _latest_batch_status(root)
            self.assertEqual(result["status"], "PARTIAL_OR_FAILED")
            self.assertEqual(result["completed"], 0)
            self.assertTrue(result["runner_identity_issues"])

    def test_identical_filename_different_canonical_bytes_requires_exact_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical = root / "canonical"
            canonical.mkdir()
            legacy, status = fixture(root)
            colliding = canonical / CASE
            colliding.write_text("# synthetic runner B\n", encoding="utf-8")
            self.assertEqual(
                _latest_batch_status(root, (canonical,))["status"], "COMPLETE_SOLVER_ONLY"
            )
            payload = json.loads(status.read_text(encoding="utf-8"))
            payload[0]["runner_path"] = str(colliding)
            status.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(
                _latest_batch_status(root, (canonical,))["status"], "PARTIAL_OR_FAILED"
            )


if __name__ == "__main__":
    unittest.main()
