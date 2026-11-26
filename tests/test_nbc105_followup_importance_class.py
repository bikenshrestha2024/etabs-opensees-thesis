"""Owner ruling 9d: Table 4-4 occupancy classification (printed p. 26). Unit tests only."""
import unittest

from components.nbc105 import clause_04_seismic_hazard as c4
from components.equivalent_static import code_basis as cb


class Classification(unittest.TestCase):
    def test_every_category_maps_to_printed_class(self):
        self.assertEqual({c4.OCCUPANCY_CLASS[k] for k in ("apartments", "offices", "banks")}, {1})
        self.assertEqual(c4.OCCUPANCY_CLASS["schools"], 2)
        self.assertEqual(c4.OCCUPANCY_CLASS["hospitals"], 3)
        self.assertEqual({v for v in c4.OCCUPANCY_CLASS.values()}, {1, 2, 3})

    def test_factors_follow_importance_factor(self):
        for cat, f in (("offices", 1.0), ("schools", 1.25), ("fire_stations", 1.5)):
            n = 100 if cat == "offices" else None
            self.assertEqual(c4.classify_importance([cat], occupant_count=n)["importance_factor"], f)

    def test_highest_class_governs(self):
        self.assertEqual(c4.classify_importance(["offices", "hospitals"])["importance_class"], 3)

    def test_over_500_persons_is_class_ii(self):
        r = c4.classify_importance(["apartments"], occupant_count=501)
        self.assertEqual((r["importance_class"], r["importance_factor"]), (2, 1.25))
        self.assertIn("OCCUPANCY_ABOVE_500_CLASS_II", r["flags"])

    def test_below_500_stays_class_i(self):
        self.assertEqual(c4.classify_importance(["apartments"], occupant_count=499)["importance_class"], 1)

    def test_exactly_500_not_printed_conservative_flagged(self):
        r = c4.classify_importance(["offices"], occupant_count=500)
        self.assertEqual(r["importance_class"], 2)
        self.assertIn("OCCUPANCY_EXACTLY_500_NOT_PRINTED_TREATED_AS_CLASS_II", r["flags"])

    def test_missing_occupancy_is_unverified_not_silent(self):
        r = c4.classify_importance(["apartments"])
        self.assertIn("CLASS_I_OCCUPANCY_UNVERIFIED", r["flags"])
        self.assertEqual(r["status"], "CLASSIFIED_OCCUPANCY_UNVERIFIED")

    def test_declared_class_cross_check(self):
        r = c4.classify_importance(["apartments"], occupant_count=900, declared_class=1)
        self.assertEqual(r["status"], "DECLARED_BELOW_TABLE_4_4")
        self.assertFalse(r["conforming"])
        self.assertEqual(c4.classify_importance(["offices"], occupant_count=10, declared_class=2)["status"],
                         "DECLARED_ABOVE_TABLE_4_4")
        self.assertEqual(c4.classify_importance(["schools"], declared_class=2)["status"],
                         "DECLARED_MATCHES_TABLE_4_4")

    def test_disaster_shelter_footnote(self):
        self.assertEqual(c4.classify_importance(["schools"], disaster_shelter=True)["importance_factor"], 1.5)
        with self.assertRaises(ValueError):
            c4.classify_importance(["offices"], occupant_count=10, disaster_shelter=True)

    def test_bad_inputs(self):
        for bad in ([], "offices", ["spaceport"]):
            with self.assertRaises(ValueError):
                c4.classify_importance(bad)
        with self.assertRaises(ValueError):
            c4.classify_importance(["offices"], declared_class=4)


class EsmSoftKey(unittest.TestCase):
    STORIES = [dict(height_m=3.0 * k, dead_load_kN=1000.0, storage_live_load_kN=0.0, other_live_load_kN=200.0)
               for k in (1, 2, 3)]

    def _run(self, i, basis):
        return cb.calculate_esm(self.STORIES, period_s=1.0, soil_type="C", zoning_factor_z=0.35,
                                importance_factor_i=i, occupancy_basis=basis)

    def test_absent_basis_changes_nothing(self):
        self.assertNotIn("importance_classification", self._run(1.0, None))

    def test_basis_reports_without_changing_i(self):
        r = self._run(1.0, {"categories": ["apartments"], "occupant_count": 900, "declared_class": 1})
        self.assertEqual(r["importance_factor_I"], 1.0)
        self.assertFalse(r["importance_factor_matches_table_4_4"])
        self.assertEqual(r["importance_classification"]["status"], "DECLARED_BELOW_TABLE_4_4")


if __name__ == "__main__":
    unittest.main()
