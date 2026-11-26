"""Owner ruling 7: one source of the 5.5.3 drift limits; every path shares it."""
import re
import unittest
from pathlib import Path
from unittest import mock

from components.nbc105 import clause_05_dynamic_characteristics as c5
from components.nonlinear_time_history import nbc105_2025_audit as audit
from components.validation import response_checks

ROOT = Path(__file__).resolve().parents[1]
LITERAL = re.compile(r"(0?\.025\s+if\s)|(else\s+0?\.006\b)|(0?\.006\s+if\s)|(['\"]SLS['\"]\s*:\s*0?\.006)")


class DriftSingleSource(unittest.TestCase):
    def test_dead_constant_removed(self):
        self.assertFalse(hasattr(audit, "DRIFT_LIMITS"))
        self.assertEqual(c5.DRIFT_LIMITS, {"ULS": 0.025, "SLS": 0.006})

    def test_no_duplicate_literals_in_production_code(self):
        offenders = []
        for path in list((ROOT / "components").rglob("*.py")) + [ROOT / "tools" / "plot_results.py"]:
            if path.name == "clause_05_dynamic_characteristics.py":
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
                if LITERAL.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{n}")
        self.assertEqual(offenders, [])

    def test_all_paths_follow_clause_5_limits(self):
        patched = {"ULS": 0.5, "SLS": 0.4}
        with mock.patch.dict(c5.DRIFT_LIMITS, patched):
            self.assertEqual(c5.drift_limit_ratio("ULS"), 0.5)
            self.assertEqual(c5.drift_ratio_status(0.45, "ULS"), "PASS")
            self.assertEqual(c5.drift_ratio_status(0.55, "ULS"), "REVIEW")
            h = audit.history_drift_check(0.45, "ULS", clause="9.3.3.1")
            self.assertTrue(h["pass"]); self.assertEqual(h["limit"], 0.5)
            h = audit.history_drift_check(0.45, "SLS", clause="8.1.3.1")
            self.assertFalse(h["pass"]); self.assertEqual(h["clause"], "8.1.3.1")
            rows = response_checks.drift_check([{"design_drift_ratio": 0.45}], "SLS")
            self.assertEqual(rows[0]["status"], "EXCEEDS")
            self.assertEqual(rows[0]["limit_ratio"], 0.4)
            from tools import plot_results
            self.assertEqual(plot_results.DRIFT_LIMIT["ULS"], 0.5)

    def test_default_numbers_and_strictness(self):
        self.assertTrue(audit.history_drift_check(0.025, "ULS")["pass"])
        self.assertFalse(audit.history_drift_check(0.0251, "ULS")["pass"])
        self.assertTrue(audit.history_drift_check(0.006, "SLS", clause="8.1.3.1")["pass"])
        with self.assertRaises(ValueError):
            audit.history_drift_check(0.01, "ULS", clause="5.6")
        with self.assertRaises(ValueError):
            c5.drift_limit_ratio("XLS")


if __name__ == "__main__":
    unittest.main()
