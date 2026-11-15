"""Solver-free regression gates for saved gravity force evidence integrity."""
import copy
import math
import unittest

from components.gravity.load_path_formulas import (
    recovered_vertical_transfers, vertical_joint_balance,
)


def valid_payload():
    return {
        "nodes": [{"tag": 1, "z_m": 0.0}, {"tag": 2, "z_m": 3.0}],
        "elements": [{"tag": 101, "nodes": [1, 2]}],
        "global_end_forces": [{
            "tag": 101, "nodes": [1, 2],
            "forces": [0, 0, 10, 0, 0, 0, 0, 0, -10, 0, 0, 0],
        }],
        "reactions": [{"node_tag": 1, "rz_kN": 10.0}],
    }


class GravityLoadPathIntegrityTests(unittest.TestCase):
    def test_valid_floor_cut_and_signed_joint_balance_are_unchanged(self):
        payload = valid_payload()
        cuts = recovered_vertical_transfers(payload, [0, 3])
        self.assertEqual(cuts[0]["lower_face_resisting_Fz_kN"], 10)
        self.assertEqual(cuts[1]["crossing_elements"], 0)
        rows = vertical_joint_balance(payload, {2: -10})
        self.assertTrue(all(r["residual_Fz_kN"] == 0 for r in rows))

    def test_duplicate_nodes_cannot_silently_replace_geometry(self):
        p = valid_payload()
        p["nodes"].append({"tag": "1", "z_m": 100.0})
        with self.assertRaisesRegex(ValueError, "Duplicate node tag"):
            recovered_vertical_transfers(p, [0])

    def test_duplicate_element_and_force_tags_cannot_be_overwritten(self):
        p = valid_payload()
        p["elements"].append(copy.deepcopy(p["elements"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate element tag"):
            recovered_vertical_transfers(p, [0])
        p = valid_payload()
        p["global_end_forces"].append(copy.deepcopy(p["global_end_forces"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate global force tag"):
            recovered_vertical_transfers(p, [0])

    def test_off_cut_nonfinite_vector_rejected_even_without_levels(self):
        p = valid_payload()
        p["global_end_forces"][0]["forces"][2] = math.nan
        with self.assertRaisesRegex(ValueError, "Nonfinite global end-force"):
            recovered_vertical_transfers(p, [])
        with self.assertRaisesRegex(ValueError, "Nonfinite global end-force"):
            vertical_joint_balance(p, {2: -10})

    def test_bad_endpoint_and_nonfinite_floor_elevation_rejected(self):
        p = valid_payload()
        p["elements"][0]["nodes"] = [1, 99]
        p["global_end_forces"][0]["nodes"] = [1, 99]
        with self.assertRaisesRegex(ValueError, "absent node"):
            recovered_vertical_transfers(p, [0])
        p = valid_payload()
        with self.assertRaisesRegex(ValueError, "Nonfinite requested floor"):
            recovered_vertical_transfers(p, [float("nan")])
        p = valid_payload()
        p["nodes"][0]["z_m"] = float("inf")
        with self.assertRaisesRegex(ValueError, "Nonfinite node elevation"):
            recovered_vertical_transfers(p, [0])

    def test_duplicate_or_nonfinite_reactions_are_not_silently_accepted(self):
        p = valid_payload()
        p["reactions"].append({"node_tag": "1", "rz_kN": 0})
        with self.assertRaisesRegex(ValueError, "Duplicate support reaction"):
            vertical_joint_balance(p, {2: -10})
        p = valid_payload()
        p["reactions"][0]["rz_kN"] = math.inf
        with self.assertRaisesRegex(ValueError, "Invalid support reaction"):
            vertical_joint_balance(p, {2: -10})

    def test_nonfinite_unknown_or_colliding_applied_load_is_rejected(self):
        p = valid_payload()
        with self.assertRaisesRegex(ValueError, "Invalid applied-load"):
            vertical_joint_balance(p, {2: math.nan})
        with self.assertRaisesRegex(ValueError, "Invalid applied-load"):
            vertical_joint_balance(p, {999: -10})
        with self.assertRaisesRegex(ValueError, "Duplicate applied-load"):
            vertical_joint_balance(p, {2: -5, "2": -5})


if __name__ == "__main__":
    unittest.main()
