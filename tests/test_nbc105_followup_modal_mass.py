"""Owner ruling 6: cumulative modal mass to 100 percent, 90 percent region (printed 7.3, p.40)."""
import unittest
from components.nbc105.clause_07_modal_response_spectrum import (
    modal_mass_participation_profile as prof, modal_mass_participation_by_direction as by_dir,
    MODAL_MASS_THRESHOLD_PERCENT)


class ModalMass(unittest.TestCase):
    def test_threshold_stays_90(self):
        self.assertEqual(MODAL_MASS_THRESHOLD_PERCENT, 90.0)

    def test_reaches_90_then_100(self):
        r = prof([60.0, 20.0, 12.0, 5.0, 3.0], periods_s=[2.0, 1.0, 0.5, 0.3, 0.2])
        self.assertEqual(r["cumulative_percent"], [60.0, 80.0, 92.0, 97.0, 100.0])
        self.assertEqual(r["reached_90_at_mode"], 3)
        self.assertEqual(r["reached_100_at_mode"], 5)
        self.assertEqual(r["period_at_90_s"], 0.5)
        self.assertTrue(r["compliant_90"]); self.assertTrue(r["all_mass_covered_100"])
        self.assertEqual([x["region"] for x in r["regions"]],
                         ["REQUIRED_FOR_90"] * 3 + ["BEYOND_90_TO_100"] * 2)
        self.assertEqual([x["highlight_90_region"] for x in r["regions"]], [True, True, True, False, False])
        self.assertEqual([x["first_mode_at_90"] for x in r["regions"]], [False, False, True, False, False])

    def test_exactly_90_counts_and_89_9_does_not(self):
        self.assertEqual(prof([45.0, 45.0])["reached_90_at_mode"], 2)
        r = prof([45.0, 44.9])
        self.assertIsNone(r["reached_90_at_mode"]); self.assertFalse(r["compliant_90"])
        self.assertAlmostEqual(r["shortfall_to_90_percent"], 0.1)
        self.assertTrue(all(x["region"] == "REQUIRED_FOR_90" for x in r["regions"]))
        self.assertIsNone(r["period_at_90_s"])

    def test_not_reaching_100_is_reported(self):
        r = prof([70.0, 25.0])
        self.assertEqual(r["reached_90_at_mode"], 2); self.assertIsNone(r["reached_100_at_mode"])
        self.assertAlmostEqual(r["shortfall_to_100_percent"], 5.0)
        self.assertFalse(r["all_mass_covered_100"])

    def test_tail_after_100_and_rejections(self):
        r = prof([100.0, 0.0, 0.0])
        self.assertEqual((r["reached_90_at_mode"], r["reached_100_at_mode"]), (1, 1))
        self.assertEqual([x["region"] for x in r["regions"]], ["REQUIRED_FOR_90", "BEYOND_100", "BEYOND_100"])
        for bad in ([], [-1.0], [float("nan")], [60.0, 41.0]):
            with self.assertRaises(ValueError):
                prof(bad)
        with self.assertRaises(ValueError):
            prof([50.0, 50.0], periods_s=[1.0])

    def test_by_direction_each_has_own_mode_numbers(self):
        r = by_dir({"X": [70.0, 25.0, 5.0], "Y": [40.0, 40.0, 5.0, 4.0]})
        self.assertEqual(r["directions"]["X"]["reached_90_at_mode"], 2)
        self.assertIsNone(r["directions"]["Y"]["reached_90_at_mode"])
        self.assertFalse(r["compliant_90"])

    def test_modal_audit_result_exposes_fields(self):
        import pathlib
        src = (pathlib.Path(__file__).resolve().parents[1] / "components/modal/analysis.py").read_text(encoding="utf-8")
        for key in ("reached_90_at_mode", "reached_100_at_mode", "mass_coverage", "highlight_90_region_"):
            self.assertIn(key, src)


if __name__ == "__main__":
    unittest.main()
