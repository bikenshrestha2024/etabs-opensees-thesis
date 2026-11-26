"""Owner ruling 1 (2026-11-26): 8 ground motions, printed 8.1.3 / 9.3.3 rule.

Source-to-code unit tests only; not engineering acceptance. Printed p.42, p.47.
"""
import unittest
from components.nbc105.clause_08_elastic_time_history import (
    PROJECT_DECLARED_GROUND_MOTION_COUNT, project_record_set_evaluation,
    record_response_aggregate)
from components.nonlinear_time_history.nbc105_2025_audit import project_response_aggregation


class GroundMotionRule(unittest.TestCase):
    def test_declared_count_is_eight(self):
        self.assertEqual(PROJECT_DECLARED_GROUND_MOTION_COUNT, 8)

    def test_eight_records_average(self):
        r = project_response_aggregation([1, 2, 3, 4, 5, 6, 7, 9])
        self.assertEqual((r["rule"], r["status"], r["declared_count_met"]), ("AVERAGE", "OK", True))
        self.assertAlmostEqual(r["value"], 37 / 8)

    def test_fewer_than_seven_uses_maximum(self):
        r = project_record_set_evaluation([1, 8, 3, 4, 5, 2])
        self.assertEqual((r["rule"], r["value"]), ("MAXIMUM", 8.0))
        self.assertFalse(r["declared_count_met"])
        self.assertEqual(r["status"], "OK_BUT_DECLARED_COUNT_NOT_MET")

    def test_exactly_seven_fail_closed_even_if_eight_declared(self):
        r = project_response_aggregation([1, 2, 3, 4, 5, 6, 7])
        self.assertEqual((r["status"], r["value"]), ("BLOCKED", None))
        with self.assertRaises(ValueError):
            record_response_aggregate([1, 2, 3, 4, 5, 6, 7])

    def test_empty_and_nonfinite(self):
        self.assertEqual(project_record_set_evaluation([])["status"], "BLOCKED")
        with self.assertRaises(ValueError):
            project_record_set_evaluation([1.0, float("nan")])


if __name__ == "__main__":
    unittest.main()
