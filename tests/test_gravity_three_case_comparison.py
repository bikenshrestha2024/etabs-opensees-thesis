"""Fast synthetic evidence tests: no ETABS or OpenSees installation required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.gravity.three_case_comparison import collect_cases, export_case_comparison


class TestThreeCaseGravity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.model = self.root / "OpenSees_Complete_Gravity_Model.py"
        self.model.write_text("pass\n", encoding="utf-8")

    def test_no_solved_case_never_substitutes_defaults(self):
        with patch("components.gravity.three_case_comparison.current_case", return_value=None):
            with self.assertRaisesRegex(ValueError, "No current separately solved"):
                collect_cases(self.root, self.model)

    def test_separate_real_cases_and_missing_status(self):
        def current(_root, _model, *, scenario, profile):
            if scenario == "CONTINUOUS_WALL_BASE_FIXED":
                return None
            n = 32 if scenario == "ETABS_NONZERO_REACTION_DIAGNOSTIC" else 76
            result = self.root / ("case_" + str(n) + ".json")
            result.write_text(json.dumps({"ok": True, "reactions": [{"node_tag": i} for i in range(n)]}))
            return {"result_path": str(result), "applied_load_kN": 100.0}
        with patch("components.gravity.three_case_comparison.current_case", side_effect=current):
            available, missing = collect_cases(self.root, self.model)
        self.assertEqual(set(available), {"32", "76"})
        self.assertEqual(len(missing), 1)
        self.assertIn("97", missing[0])

    def test_partial_cases_export_missing_as_blank_not_keyerror(self):
        def current(_root, _model, *, scenario, profile):
            if scenario == "CONTINUOUS_WALL_BASE_FIXED":
                return None
            n = 32 if scenario == "ETABS_NONZERO_REACTION_DIAGNOSTIC" else 76
            result = self.root / ("case_" + str(n) + ".json")
            result.write_text(json.dumps({
                "ok": True,
                "reactions": [{"node_tag": i, "rz_kN": 100.0 / n}
                              for i in range(n)],
                "nodes": [{"tag": i, "ux_m": 0.0, "uy_m": 0.0,
                           "uz_m": -0.001, "z_m": 0.0}
                          for i in range(n)]
            }))
            return {"result_path": str(result), "applied_load_kN": 100.0,
                    "summed_reaction_kN": 100.0,
                    "equilibrium_error_percent": 0.0}
        with patch("components.gravity.three_case_comparison.current_case", side_effect=current):
            report, directory, _figure = export_case_comparison(self.root, self.model)
        self.assertEqual(set(report["available_cases"]), {"32", "76"})
        import csv
        with (directory / "Support_Reactions_32_76_97.csv").open(encoding="utf-8-sig") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 76)
        self.assertIn("rz_32_kN", rows[0])
        self.assertIn("rz_76_kN", rows[0])
        self.assertIn("rz_97_kN", rows[0])
        self.assertEqual(rows[0]["rz_97_kN"], "")
        self.assertEqual(rows[50]["rz_32_kN"], "")
        # The original exporter reversed (strategy, label) and silently
        # wrote every displacement value as a blank. Verify actual numbers,
        # including a legitimate missing-case blank for the 97-node case.
        with (directory / "Common_Node_Displacements_32_76_97.csv").open(
                encoding="utf-8-sig") as fp:
            displacements = list(csv.DictReader(fp))
        self.assertEqual(len(displacements), 32)
        first = displacements[0]
        self.assertAlmostEqual(
            float(first["uz_m_ETABS_NONZERO_REACTION_DIAGNOSTIC"]), -0.001)
        self.assertAlmostEqual(
            float(first["uz_m_ETABS_SOURCE_SUPPORTS"]), -0.001)
        self.assertEqual(first["uz_m_CONTINUOUS_WALL_BASE_FIXED"], "")

    def test_load_discrepancy_is_blocker(self):
        def current(_root, _model, *, scenario, profile):
            n = {"ETABS_NONZERO_REACTION_DIAGNOSTIC": 32,
                 "ETABS_SOURCE_SUPPORTS": 76,
                 "CONTINUOUS_WALL_BASE_FIXED": 97}[scenario]
            result = self.root / ("case_" + str(n) + ".json")
            result.write_text(json.dumps({"ok": True, "reactions": [{"node_tag": i} for i in range(n)]}))
            return {"result_path": str(result),
                    "applied_load_kN": 101.0 if n == 76 else 100.0}
        with patch("components.gravity.three_case_comparison.current_case", side_effect=current):
            with self.assertRaisesRegex(ValueError, "different applied gravity"):
                collect_cases(self.root, self.model)


if __name__ == "__main__":
    unittest.main()
