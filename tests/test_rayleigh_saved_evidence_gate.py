"""Fail-closed saved Rayleigh evidence tests; no ETABS/OpenSees dependency."""
import copy
import unittest
from components.modal.rayleigh_ledger_audit import (
    verify_saved_rayleigh_axis, verify_rayleigh_sum,
)


def valid_axis():
    rows = [
        dict(master_node=101, constrained_floor_node_count=3, weight_kN=100.,
             force_kN=10., displacement_m=.01),
        dict(master_node=102, constrained_floor_node_count=4, weight_kN=200.,
             force_kN=20., displacement_m=.02),
    ]
    reconstructed = verify_rayleigh_sum(rows)
    return {
        "rows": rows,
        "period_s": reconstructed["period_s"],
        "rayleigh_numerator_kN_m2": reconstructed["numerator_kN_m2"],
        "rayleigh_denominator_gFiDi_kN_m2_s2": reconstructed["denominator_kN_m2_s2"],
        "reference_force_total_kN": 30.,
        "kinematic_audit": {
            "status": "VERIFIED_FLOOR_TRANSLATIONS",
            "steps": 1,
            "pattern_factor": 1.,
            "incremental_base_reaction_kN": -30.,
            "relative_reaction_error": 0.,
            "max_floor_translation_spread_m": 0.,
        },
    }


class SavedRayleighEvidenceTests(unittest.TestCase):
    def test_all_terms_reconstruct_and_validate(self):
        axis = valid_axis()
        proof = verify_saved_rayleigh_axis(axis, expected_storeys=2)
        self.assertAlmostEqual(axis["period_s"], proof["period_s"])

    def test_missing_rows_and_masters_are_rejected(self):
        for mutate in (
            lambda x: x.update(rows=[]),
            lambda x: x["rows"][1].update(master_node=101),
            lambda x: x["rows"][1].update(constrained_floor_node_count=0),
        ):
            axis = valid_axis()
            mutate(axis)
            with self.assertRaises(ValueError):
                verify_saved_rayleigh_axis(axis)

    def test_modified_period_or_work_is_rejected(self):
        for key in ("period_s", "rayleigh_numerator_kN_m2",
                    "rayleigh_denominator_gFiDi_kN_m2_s2", "reference_force_total_kN"):
            axis = valid_axis()
            axis[key] *= 1.5
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_saved_rayleigh_axis(axis)

    def test_unsubstantiated_status_and_bad_kinematics_rejected(self):
        for field, value in (
            ("status", "VERIFIED_FLOOR_TRANSLATIONS_FAKE"),
            ("steps", 10),
            ("pattern_factor", .5),
            ("relative_reaction_error", .2),
            ("max_floor_translation_spread_m", .001),
            ("incremental_base_reaction_kN", -20.),
        ):
            axis = valid_axis()
            axis["kinematic_audit"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify_saved_rayleigh_axis(axis)

    def test_incomplete_storeys_and_boolean_metric_rejected(self):
        axis = valid_axis()
        with self.assertRaises(ValueError):
            verify_saved_rayleigh_axis(axis, expected_storeys=25)
        axis["kinematic_audit"]["pattern_factor"] = True
        with self.assertRaises(ValueError):
            verify_saved_rayleigh_axis(axis)


if __name__ == "__main__":
    unittest.main()
