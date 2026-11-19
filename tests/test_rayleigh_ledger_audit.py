"""Regression tests for all-storey NBC Rayleigh ledger audit (no OpenSees required)."""
import math
import unittest
from components.modal.rayleigh_ledger_audit import verify_storey_coverage, verify_rayleigh_sum, verify_storey_elevations


class TestRayleighLedgerAudit(unittest.TestCase):
    def setUp(self):
        self.model = [{"storey_number": 1, "master_tag": 101},
                      {"storey_number": 2, "master_tag": 102}]
        self.rows = [{"story_number": 1, "master_node_tag": 101},
                     {"story_number": 2, "master_node_tag": 102}]

    def test_full_coverage_order_independent(self):
        self.assertEqual(verify_storey_coverage(self.model, list(reversed(self.rows))), 2)

    def test_matching_ids_but_wrong_heights_are_rejected(self):
        model = [
            {"storey_number": 1, "master_tag": 101, "master_xyz": [0, 0, 3.8]},
            {"storey_number": 2, "master_tag": 102, "master_xyz": [0, 0, 7.6]},
        ]
        ledger = [
            {"story_number": 1, "master_node_tag": 101, "height_m": 3.8},
            {"story_number": 2, "master_node_tag": 102, "height_m": 7.6},
        ]
        self.assertEqual(verify_storey_elevations(model, ledger, 0), 2)
        stale = [dict(row) for row in ledger]
        stale[1]["height_m"] = 8.1
        with self.assertRaisesRegex(ValueError, "differs"):
            verify_storey_elevations(model, stale, 0)
        shifted = [dict(row) for row in ledger]
        shifted[0]["height_m"] = 2.8
        with self.assertRaisesRegex(ValueError, "differs"):
            verify_storey_elevations(model, shifted, 0)

    def test_missing_or_stale_level_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_storey_coverage(self.model, self.rows[:1])
        with self.assertRaises(ValueError):
            verify_storey_coverage(self.model, self.rows + [{"story_number": 3, "master_node_tag": 103}])

    def test_duplicate_master_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_storey_coverage(self.model, [self.rows[0], {"story_number": 2, "master_node_tag": 101}])

    def test_reproduces_uniform_deflection_period(self):
        records = [{"weight_kN": 100., "force_kN": 10., "displacement_m": 0.01},
                   {"weight_kN": 200., "force_kN": 20., "displacement_m": 0.01}]
        answer = verify_rayleigh_sum(records)
        self.assertEqual(answer["storey_count"], 2)
        self.assertAlmostEqual(answer["period_s"], 2 * math.pi * math.sqrt(0.03 / (9.81 * 0.3)))
        self.assertEqual(answer["status"], "NUMERICAL_RECONSTRUCTION_ONLY")

    def test_missing_or_invalid_values_rejected(self):
        for record in ([], [{"weight_kN": 10., "force_kN": 0., "displacement_m": 1.}],
                       [{"weight_kN": 10., "force_kN": 1., "displacement_m": -1.}]):
            with self.assertRaises(ValueError):
                verify_rayleigh_sum(record)


if __name__ == "__main__":
    unittest.main()
