"""Pure deterministic tests; no OpenSeesPy or experimental files required."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from components.nonlinear_time_history.thesis_quality import (
    audit_ground_motion_pair, classify_case_result,
    generate_isolation_configs, review_isolation_runs,
)


class ThesisNLTHAQualityTests(unittest.TestCase):
    def test_reject_nonfinite_acceleration(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"record.txt"
            p.write_text("sample data")
            with self.assertRaisesRegex(ValueError, "non-finite"):
                audit_ground_motion_pair(
                    [([0, float("nan")], .01, "g"), ([0, 1], .01, "g")], [p, p])

    def test_pair_hashes_and_sampling(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"record.txt"
            p.write_text("data")
            report = audit_ground_motion_pair(
                [([0, 1, 0], .01, "g"), ([0, -1, 0], .01, "m/s2")], [p, p])
            self.assertEqual(report["status"], "PRECHECK_PASSED")
            self.assertEqual(report["records"][0]["samples"], 3)
            self.assertEqual(len(report["records"][0]["sha256"]), 64)

    def test_truncated_never_ranks_as_complete(self):
        case = {"orientation": "XY", "status": "COMPLETED_TRUNCATED_TRIAL",
                "physical_time_s": .005, "full_record_duration_s": 25}
        result = classify_case_result(case)
        self.assertFalse(result["full_record_completed"])
        self.assertFalse(result["eligible_for_further_engineering_review"])

    def test_probes_are_separate_and_keep_original_config(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"export"
            model.mkdir()
            (model/"OpenSees_Complete_Model_Data_V118.json").write_text('{"nodes":{}}')
            a_path=Path(d)/"x.txt";b_path=Path(d)/"y.txt"
            a_path.write_text("0.0\\n0.1");b_path.write_text("0.0\\n-0.1")
            original = {"model_folder": str(model),
                        "x_path": str(a_path), "y_path": str(b_path),
                        "limit_state":"ULS", "dt_s":0.005,
                        "analysis_intent":"RESEARCH_DIAGNOSTIC",
                        "nonlinear_walls": True}
            before = original.copy()
            paths = generate_isolation_configs(original, Path(d)/"probes")
            self.assertEqual(original, before)
            self.assertEqual(len(paths), 4)
            manifest=json.loads((Path(d)/"probes"/"00_Probe_Evidence_Manifest.json").read_text())
            self.assertEqual(len(manifest["input_fingerprints"]["model_sha256"]),64)
            for file in paths:
                data = json.loads(Path(file).read_text())
                self.assertEqual(data["limit_state"], "ULS")
                self.assertTrue(data["diagnostic_zero_damping"])
                self.assertEqual(data["orientations"], ["XY"])
                self.assertEqual(data["duration_s"], .005)
            with self.assertRaises(FileExistsError):
                generate_isolation_configs(original, Path(d)/"probes")

    def test_missing_probes_are_not_passed(self):
        with tempfile.TemporaryDirectory() as d:
            result = review_isolation_runs(d)
            self.assertEqual(len(result["probe_results"]), 4)
            self.assertTrue(all(x["status"] == "NOT_RUN" for x in result["probe_results"]))

    def test_x_failure_is_classified_not_solved(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for label in ("ZERO", "Y", "XY"):
                p = root/label/"XY"/"Case_Summary.json"
                p.parent.mkdir(parents=True)
                p.write_text(json.dumps({
                    "status": "COMPLETED_TRUNCATED_TRIAL", "physical_time_s": .005,
                    "full_record_duration_s": 20.0}))
            p = root/"X"/"XY"/"FAILED.json"
            p.parent.mkdir(parents=True)
            p.write_text(json.dumps({"error": "tangent failure", "stage": "transient_analysis"}))
            result = review_isolation_runs(root)
            self.assertIn("X-specific", result["interpretation"])
            self.assertEqual(result["thesis_validation"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
