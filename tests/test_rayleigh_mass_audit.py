"""Mass-elevation reconciliation regression without ETABS or OpenSees."""
from copy import deepcopy
import unittest

from components.modal.rayleigh_mass_audit import audit_rayleigh_mass_elevations


def sample():
    g = 9.81
    model = {
        "base_z_m": 0.0,
        "diaphragms": [
            {"master_tag": 101, "master_xyz": [0, 0, 3]},
            {"master_tag": 102, "master_xyz": [0, 0, 6]},
        ],
        "nodes": {
            "1": [0, 0, 0],
            "2": [0, 0, 3],
            "3": [0, 0, 4.5],
            "4": [0, 0, 6],
        },
        "supports": {"1": [1, 1, 1, 1, 1, 1]},
        "nodal_mass": {"1": 25/g, "2": 100/g, "3": 20/g, "4": 80/g},
    }
    rows = [
        {"master_node_tag": 101, "dead_load_kN": 100.,
         "storage_live_load_kN": 0., "other_live_load_kN": 0.},
        {"master_node_tag": 102, "dead_load_kN": 100.,
         "storage_live_load_kN": 0., "other_live_load_kN": 0.},
    ]
    return model, rows


class RayleighMassElevationTests(unittest.TestCase):
    def test_reconciles_lower_half_between_diaphragms_to_lower_floor(self):
        model, rows = sample()
        model["nodes"]["3"][2] = 4.0
        rows[0]["dead_load_kN"], rows[1]["dead_load_kN"] = 120., 80.
        result = audit_rayleigh_mass_elevations(model, rows)
        self.assertEqual(result["floor_weights_from_nodal_mass_kN"], [120., 80.])
        self.assertEqual(result["vertical_first_moment_shift_kN_m"], -20.)
        self.assertEqual(result["maximum_downward_lump_m"], 1.)

    def test_reconciles_total_but_exposes_elevation_shift(self):
        model, rows = sample()
        result = audit_rayleigh_mass_elevations(model, rows)
        self.assertAlmostEqual(result["source_active_horizontal_weight_kN"], 200)
        self.assertAlmostEqual(result["intermediate_mass_weight_kN"], 20)
        self.assertAlmostEqual(result["vertical_first_moment_shift_kN_m"], 30)
        self.assertAlmostEqual(result["vertical_shift_weighted_mean_m"], 0.15)
        self.assertEqual(result["intermediate_mass_node_count"], 1)
        self.assertEqual(result["status"],
                         "SOURCE_MASS_TOTAL_RECONCILED_VERTICAL_LUMPING_NOT_EIGEN_EQUIVALENCE")

    def test_same_total_but_wrong_floor_allocation_fails(self):
        model, rows = sample()
        rows[0]["dead_load_kN"] = 110
        rows[1]["dead_load_kN"] = 90
        with self.assertRaisesRegex(ValueError, "floor weights"):
            audit_rayleigh_mass_elevations(model, rows)

    def test_missing_node_or_out_of_roof_rejected(self):
        model, rows = sample()
        del model["nodes"]["3"]
        with self.assertRaisesRegex(ValueError, "missing"):
            audit_rayleigh_mass_elevations(model, rows)
        model, rows = sample()
        model["nodes"]["3"][2] = 6.5
        with self.assertRaisesRegex(ValueError, "above uppermost"):
            audit_rayleigh_mass_elevations(model, rows)

    def test_invalid_mass_and_supports_rejected(self):
        model, rows = sample()
        model["nodal_mass"]["3"] = float("nan")
        with self.assertRaisesRegex(ValueError, "nodal mass"):
            audit_rayleigh_mass_elevations(model, rows)
        model, rows = sample()
        model["supports"]["3"] = [1, 0, 1, 1, 1, 1]
        result = audit_rayleigh_mass_elevations(model, rows)
        self.assertEqual(result["mixed_XY_support_node_count"], 1)

    def test_fixed_supports_do_not_enter_active_seismic_weight(self):
        model, rows = sample()
        model["nodal_mass"]["1"] = 1e6
        result = audit_rayleigh_mass_elevations(model, rows)
        self.assertAlmostEqual(result["source_active_horizontal_weight_kN"], 200)


if __name__ == "__main__":
    unittest.main()
