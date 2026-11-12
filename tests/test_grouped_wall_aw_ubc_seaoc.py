"""1997 UBC/SEAOC grouped wall area diagnostic, synthetic source geometry."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from components.inputs.project_workbooks import _wall_aw_profile, _continuous_wall_pier_diagnostic
from components.inputs.grouped_wall_aw import (
    wall_aw_example, grouped_wall_aw, source_matched_grouping, INPUT_NAME,
    verify_thesis_two_12m_wall_geometry, selected_two_12m_wall_reference)


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


    def test_two_12m_wall_lines_verified_from_actual_style_shell_slices(self):
        patches=[]
        for plane in (6.,12.):
            patches.extend([
                ("X",plane,.6,6.,8.,0.,2.3),
                ("X",plane,.6,10.,14.,0.,2.3),
                ("X",plane,.6,16.,18.,0.,2.3),
                ("X",plane,.6,6.,18.,2.3,3.8)])
        for plane in (6.,12.,18.):
            patches.append(("Y",plane,.6,6.,12.,0.,3.8))
        profile=_wall_aw_profile(95.,0.,3.8,patches)
        result=verify_thesis_two_12m_wall_geometry(profile,95.)
        desired=selected_two_12m_wall_reference()
        self.assertEqual(result["status"],
                         "EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY")
        self.assertFalse(result["code_accepted"])
        self.assertEqual(len(result["wall_geometry_verification"]["x_wall_lines"]),2)
        self.assertEqual(len(result["wall_geometry_verification"]["y_wall_lines"]),3)
        self.assertAlmostEqual(result["aw_candidate_m2"]["X"],desired["X"],places=9)
        self.assertAlmostEqual(result["aw_candidate_m2"]["Y"],desired["Y"],places=9)
        old=_continuous_wall_pier_diagnostic(95.,profile)
        self.assertLess(old["aw_candidate_m2"]["X"],result["aw_candidate_m2"]["X"])
        self.assertAlmostEqual(old["aw_candidate_m2"]["X"],1.9306371191,places=8)
        # Physical first-storey connection above 2.3m is essential to 12m method.
        no_head=[p for p in patches if not (p[0]=="X" and p[5]==2.3)]
        with self.assertRaises(ValueError):
            verify_thesis_two_12m_wall_geometry(
                _wall_aw_profile(95.,0.,3.8,no_head),95.)
        with self.assertRaises(ValueError):
            verify_thesis_two_12m_wall_geometry(profile,94.)
        with self.assertRaises(ValueError):
            verify_thesis_two_12m_wall_geometry(
                _wall_aw_profile(95.,0.,3.8,patches[:-1]),95.)
        # Old method remains as sensitivity alternative, never selected by
        # splitting identical 12m wall shells at architectural grid points.
        self.assertAlmostEqual(wall_aw_example()["X"],1.9582936288,places=8)

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

    def test_length_height_ratio_capped_at_point_nine(self):
        # A 100 m connected wall in a 50 m building uses the explicit .9 cap.
        profile = _wall_aw_profile(
            50, 0, 3, [("X", 0., .6, 0., 100., 0., 3.)])
        groups = [dict(id="long", axis="X", plane_m=0,
                       thickness_m=.6, start_m=0, end_m=100)]
        result = grouped_wall_aw(profile, 50, groups)
        self.assertAlmostEqual(result["aw_candidate_m2"]["X"],
                               100 * .6 * (.2 + .9**2))

    def test_template_export_never_creates_approval_manifest(self):
        from unittest.mock import patch
        from components.inputs.opensees_nbc_sync import export_wall_grouping_review_template
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            edb = root / "active.EDB"
            edb.write_bytes(b"source bytes")
            snapshot = {
                "source_edb": str(edb),
                "assembled_model_sha256": "b"*64,
                "wall_aw_profile": self.profile,
                "wall_aw_height_m": 95.,
                "historical_ubc_seaoc_user_example": wall_aw_example(),
                "continuous_pier_diagnostic": _continuous_wall_pier_diagnostic(95, self.profile),
            }
            with patch("components.inputs.opensees_nbc_sync._source_snapshot", return_value=snapshot):
                template = export_wall_grouping_review_template(root, "ULS")
            payload = json.loads(template.read_text())
            self.assertEqual(payload["wall_groups"], [])
            self.assertEqual(payload["height_m"], 95)
            self.assertTrue(payload["source_slice_geometry_for_manual_mapping"])
            self.assertFalse((root / INPUT_NAME).exists())
            with patch("components.inputs.opensees_nbc_sync._source_snapshot", return_value=snapshot):
                with self.assertRaises(FileExistsError):
                    export_wall_grouping_review_template(root, "ULS")

    def test_common_aw_resolver_prefers_verified_12m_over_older_excel(self):
        from unittest.mock import patch
        from components.inputs.aw_sources import resolve_aw
        reference={"values":{"awx":1.958293628808864,
                             "awy":2.2030803324099724},
                   "method":"ORIGINAL_EXCEL","source_identity":"SAME_EDB_SHA256"}
        reported={"grouped_wall_aw_review":{
                      "status":"EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY",
                      "aw_candidate_m2":{"X":2.073174515235457,
                                         "Y":2.2030803324099724},
                      "source_edb_sha256":"a"*64},
                  "assembled_model_sha256":"b"*64,
                  "aw_evidence":{"X":{"code_accepted":False},
                                 "Y":{"code_accepted":False}}}
        with patch("components.inputs.aw_sources.latest_linked_reference",
                   return_value=(reference,"historical reference")), patch(
                   "components.inputs.opensees_nbc_sync._source_snapshot",
                   return_value=reported):
            chosen=resolve_aw("/nonexistent-export", "ULS")
        self.assertAlmostEqual(chosen["X"],2.073174515235457)
        self.assertEqual(chosen["method"],
                         "EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY")
        self.assertFalse(chosen["code_accepted"])
        self.assertAlmostEqual(chosen["historical_workbook_aw_m2"]["X"],
                               1.958293628808864)
        self.assertEqual(chosen["reference"],reference)

    def test_zero_or_full_opening_rejected(self):
        with self.assertRaises(ValueError):
            wall_aw_example(opening_width_m=6)
        with self.assertRaises(ValueError):
            grouped_wall_aw(self.profile, 0, self.groups)


if __name__ == "__main__":
    unittest.main()
