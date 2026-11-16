"""Offline integrity checks for private Studio evidence import.

No solver, ETABS or confidential source model required.
"""
import json
import pathlib
import tempfile
import unittest

from import_verified_runs import EXPECTED, validate_directory


def fixture(folder):
    for case, count in EXPECTED.items():
        analytical = case == "B12"
        r = {
            "case_id": case,
            "status": "ANALYTICAL_PASS" if analytical else "PASS",
            "solver": "NONE_ANALYTICAL_ONLY" if analytical else "OpenSeesPy",
            "solver_version": "NOT_APPLICABLE" if analytical else "3.8.0",
            "etabs_native_equivalence": "NOT_VERIFIED",
            "metrics": [{"metric": "synthetic", "actual": 1.0, "expected": 1.0,
                         "passed": True} for _ in range(count)],
            "source_sha256": {
                "ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py": "a" * 64
            },
            "software_version": "2.1.0-single-file",
            "tolerance_relative": .01,
        }
        (pathlib.Path(folder) / (case + ".json")).write_text(json.dumps(r))


class TestEvidenceImport(unittest.TestCase):
    def test_valid_complete_12_case_archive(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            out = validate_directory(d)
            self.assertEqual(out["status"], "EVIDENCE_CONSISTENT")
            self.assertEqual(out["native_component_cases_passed"], 11)
            self.assertEqual(out["analytical_only_cases_passed"], 1)
            self.assertEqual(out["metrics_passed"], 58)
            self.assertEqual(out["thesis_model_equivalence"], "NOT_VERIFIED")
            self.assertNotIn(d, json.dumps(out))

    def test_missing_case_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            (pathlib.Path(d) / "B06.json").unlink()
            self.assertEqual(validate_directory(d)["status"], "EVIDENCE_REJECTED")

    def test_mislabeled_analytical_case_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            path = pathlib.Path(d) / "B12.json"
            x = json.loads(path.read_text())
            x["status"] = "PASS"
            path.write_text(json.dumps(x))
            self.assertEqual(validate_directory(d)["status"], "EVIDENCE_REJECTED")

    def test_claim_of_etabs_equivalence_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            path = pathlib.Path(d) / "B01.json"
            x = json.loads(path.read_text())
            x["etabs_native_equivalence"] = "VERIFIED"
            path.write_text(json.dumps(x))
            self.assertEqual(validate_directory(d)["status"], "EVIDENCE_REJECTED")

    def test_mixed_source_hashes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            path = pathlib.Path(d) / "B09.json"
            x = json.loads(path.read_text())
            x["source_sha256"]["ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py"] = "b" * 64
            path.write_text(json.dumps(x))
            self.assertIn("MIXED_OR_MISSING_STUDIO_SOURCE_HASHES",
                          validate_directory(d)["issues"])

    def test_false_pass_metric_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            path = pathlib.Path(d) / "B04.json"
            x = json.loads(path.read_text())
            x["metrics"][0]["actual"] = 1.5
            path.write_text(json.dumps(x))
            self.assertEqual(validate_directory(d)["status"], "EVIDENCE_REJECTED")

    def test_nonfinite_metric_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            path = pathlib.Path(d) / "B05.json"
            x = json.loads(path.read_text())
            x["metrics"][0]["actual"] = float("nan")
            path.write_text(json.dumps(x))
            self.assertEqual(validate_directory(d)["status"], "EVIDENCE_REJECTED")


if __name__ == "__main__":
    unittest.main()
