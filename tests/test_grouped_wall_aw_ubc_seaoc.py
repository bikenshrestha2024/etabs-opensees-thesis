"""1997 UBC/SEAOC grouped wall area diagnostic, synthetic source geometry."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from components.inputs.project_workbooks import _wall_aw_profile, _continuous_wall_pier_diagnostic
from components.inputs.grouped_wall_aw import (
    wall_aw_example, grouped_wall_aw, source_matched_grouping, INPUT_NAME)


class TestGroupedWallArea(unittest.TestCase):
    def setUp(self):
        self.groups = []
        self.patches = []
        for i in range(4):
            plane = i * 8.
            self.groups.append(dict(id=f"X{i+1}", axis="X", plane_m=plane,
                                    thickness_m=.6, start_m=0, end_m=6))
            # Door begins at base and is 2.3 m high; upper wall spans full 6 m.
            self.patches.extend([
                ("X", plane, .6, 0, 2, 0, 2.3),
                ("X", plane, .6, 4, 6, 0, 2.3),
                ("X", plane, .6, 0, 6, 2.3, 3.8)])
        for i in range(3):
            plane = 100 + i * 8.
            self.groups.append(dict(id=f"Y{i+1}", axis="Y", plane_m=plane,
                                    thickness_m=.6, start_m=0, end_m=6))
            self.patches.append(("Y", plane, .6, 0, 6, 0, 3.8))
        self.profile = _wall_aw_profile(95, 0, 3.8, self.patches)

    def test_user_original_excel_method_is_reproduced(self):
        result = grouped_wall_aw(self.profile, 95, self.groups)
        formula = .2 + (6 / 95)**2
        self.assertAlmostEqual(result["aw_candidate_m2"]["X"], 4 * 2.4 * formula, places=9)
        self.assertAlmostEqual(result["aw_candidate_m2"]["Y"], 3 * 3.6 * formula, places=9)
        self.assertAlmostEqual(result["aw_candidate_m2"]["X"], 1.958293628808864, places=9)
        self.assertAlmostEqual(result["aw_candidate_m2"]["Y"], 2.2030803324099724, places=9)
        self.assertFalse(result["code_accepted"])
        self.assertEqual(wall_aw_example()["status"], "ILLUSTRATIVE_GEOMETRY_NOT_EDB_VERIFIED")

    def test_old_independent_pier_diagnostic_stays_separate(self):
        old = _continuous_wall_pier_diagnostic(95, self.profile)
        new = grouped_wall_aw(self.profile, 95, self.groups)
        self.assertLess(old["aw_candidate_m2"]["X"], new["aw_candidate_m2"]["X"])
        self.assertAlmostEqual(old["aw_candidate_m2"]["Y"], new["aw_candidate_m2"]["Y"])

    def test_all_source_wall_material_must_be_mapped(self):
        with self.assertRaisesRegex(ValueError, "Unmapped"):
            grouped_wall_aw(self.profile, 95, self.groups[:-1])

    def test_overlapping_groups_refused(self):
        duplicate = dict(self.groups[0], id="duplicate", start_m=1, end_m=5)
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            grouped_wall_aw(self.profile, 95, self.groups + [duplicate])

    def test_source_hash_required_no_silent_override(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            edb = root / "original.EDB"
            edb.write_bytes(b"test only -- original EDB contents")
            sha = hashlib.sha256(edb.read_bytes()).hexdigest()
            model_hash = "b" * 64
            (root / INPUT_NAME).write_text(json.dumps(dict(
                source_edb_sha256=sha, assembled_model_sha256=model_hash,
                limit_state="ULS", height_m=95, wall_groups=self.groups)))
            selected = source_matched_grouping(
                root, "ULS", self.profile, 95, edb, model_hash)
            self.assertAlmostEqual(selected["aw_candidate_m2"]["X"], wall_aw_example()["X"])
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                source_matched_grouping(root, "SLS", self.profile, 95, edb, model_hash)
            with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
                source_matched_grouping(root, "ULS", self.profile, 95, edb, "c"*64)

    def test_zero_or_full_opening_rejected(self):
        with self.assertRaises(ValueError):
            wall_aw_example(opening_width_m=6)
        with self.assertRaises(ValueError):
            grouped_wall_aw(self.profile, 0, self.groups)


if __name__ == "__main__":
    unittest.main()
