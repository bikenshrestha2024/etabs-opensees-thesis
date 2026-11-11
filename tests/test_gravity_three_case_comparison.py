"""Fast synthetic evidence tests: no ETABS or OpenSees installation required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.gravity.three_case_comparison import collect_cases


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
