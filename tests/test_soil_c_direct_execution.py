"""Headless execution-path tests; no native ETABS/OpenSees model is claimed."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.nonlinear_time_history import soil_c_case_execution as exe

EXPORTS = (
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
    "OpenSees_Complete_Export_Report_V118.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Source_Model_Metadata_V118.json",
)

class DirectCaseExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.model = self.root / "model"
        self.model.mkdir()
        for name in EXPORTS:
            (self.model / name).write_text("{}", encoding="utf-8")
        self.a = self.root / "A.txt"
        self.b = self.root / "B.txt"
        self.a.write_text("0\n1\n", encoding="utf-8")
        self.b.write_text("0\n2\n", encoding="utf-8")
        self.config_path = self.root / "case.json"
        self.cfg = {
            "model_folder": str(self.model), "output_dir": str(self.root/"results"),
            "x_path": str(self.a), "y_path": str(self.b),
            "variant_id": "M0", "pair_id": "Kobe", "earthquake_event": "Kobe",
            "analysis_intent": "RESEARCH_DIAGNOSTIC", "soil_type": "C",
            "soil_c_primary_nltha": True, "source_records_already_scaled": True,
            "scale": 1.0, "orientations": ["XY", "YX"],
            "diagnostic_excitation": "XY", "limit_state": "ULS",
            "duration_s": None,
        }
        self.config_path.write_text(json.dumps(self.cfg), encoding="utf-8")
        self.check_pair = patch.object(exe, "verify_runner_pair", return_value={
            "event": "Kobe", "source_sha256_A": "a"*64, "source_sha256_B": "b"*64})
        self.check_pair.start()
        self.addCleanup(self.check_pair.stop)

    def test_rejects_unreviewed_diagnostic_without_explicit_opt_in(self):
        with self.assertRaisesRegex(ValueError, "allow-research-diagnostic"):
            exe.preflight_case(self.config_path)
        self.assertFalse((self.root/"results").exists())

    def test_source_fingerprint_gate_is_required(self):
        with patch.object(exe, "verify_runner_pair", side_effect=ValueError("SHA mismatch")):
            with self.assertRaisesRegex(ValueError, "SHA mismatch"):
                exe.preflight_case(self.config_path, allow_research_diagnostic=True)

    def test_rejects_missing_export_and_never_launches(self):
        (self.model / EXPORTS[0]).unlink()
        with self.assertRaisesRegex(FileNotFoundError, "OpenSees_Complete_Model_Data"):
            exe.preflight_case(self.config_path, allow_research_diagnostic=True)

    def test_rejects_existing_output_to_preserve_evidence(self):
        (self.root/"results").mkdir()
        with self.assertRaises(FileExistsError):
            exe.preflight_case(self.config_path, allow_research_diagnostic=True)

    def test_never_accepts_one_orientation_as_complete_pair(self):
        def fake_launch(command, cwd, log_path):
            case = self.root / "results" / "XY"
            case.mkdir()
            (case / "Case_Summary.json").write_text(json.dumps({
                "status": "COMPLETED_EXPLORATORY_RECORD",
                "completion_gate": {"status": "FULL_DURATION_NUMERIC_SCREEN", "full_record_completed": True},
                "orientation": "XY",
            }), encoding="utf-8")
            return 0
        result = exe.execute_case(self.config_path, allow_research_diagnostic=True, launcher=fake_launch)
        self.assertEqual(result["status"], "INCOMPLETE_OR_UNVERIFIED")
        self.assertFalse(result["engineering_accepted"])
        self.assertEqual(result["orientations_verified"], ["XY"])

    def test_two_accepted_history_screens_are_not_thesis_approval(self):
        def fake_launch(command, cwd, log_path):
            self.assertIn("building_exploratory", " ".join(command))
            for orientation in ("XY", "YX"):
                case = self.root/"results"/orientation
                case.mkdir()
                (case/"Case_Summary.json").write_text(json.dumps({
                    "status": "COMPLETED_EXPLORATORY_RECORD",
                    "orientation": orientation,
                    "completion_gate": {"status": "FULL_DURATION_NUMERIC_SCREEN", "full_record_completed": True},
                }), encoding="utf-8")
            return 0
        result = exe.execute_case(self.config_path, allow_research_diagnostic=True, launcher=fake_launch)
        self.assertEqual(result["status"], "FULL_DURATION_SOFTWARE_SCREEN_ONLY")
        self.assertFalse(result["engineering_accepted"])
        self.assertTrue((self.root/"results"/"Execution_Status.json").is_file())
        with self.assertRaises(FileExistsError):
            exe.execute_case(self.config_path, allow_research_diagnostic=True, launcher=fake_launch)

    def test_failed_child_return_keeps_failure_evidence(self):
        result = exe.execute_case(self.config_path, allow_research_diagnostic=True,
                                  launcher=lambda command, cwd, log_path: 7)
        self.assertEqual(result["status"], "RUNNER_FAILED")
        self.assertEqual(result["runner_exit_code"], 7)
        self.assertFalse(result["engineering_accepted"])
        self.assertTrue((self.root/"results"/"Execution_Status.json").exists())

if __name__ == "__main__":
    unittest.main()
