"""Tests for independent beam evidence and verified foundation-region aggregation."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from Gravity_Safe_Engineering_Review_V1 import (
    beam_checks,foundation_regions,review,stage_candidate,
    build_isolated_candidate)


class SafeGravityReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.export=self.root/"export";self.export.mkdir()
        (self.export/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps({"joint_volume_weight_policy":"AUDIT_ONLY",
                "etabs_beam_weight_policy":"GROSS_SECTION_LENGTH",
                "etabs_clear_beam_weight_confirmed":False}))
        self.audit=dict(beam_count=2,policy="GROSS_SECTION_LENGTH",
            gross_beam_weight_kN=72.+36.,rows=[
                dict(etabs_object="B1",full_length_m=6.0,frame_area_m2=.48,
                     unit_weight_kN_m3=25.,end_i_m=.55,end_j_m=.55,
                     gross_weight_kN=72.,potential_offset_weight_kN=13.2),
                dict(etabs_object="B2",full_length_m=3.0,frame_area_m2=.48,
                     unit_weight_kN_m3=25.,end_i_m=0.,end_j_m=0.,
                     gross_weight_kN=36.,potential_offset_weight_kN=0.)])
        self._save_audit()
        self.weight=self.root/"etabs_material_list.csv"
        self.weight.write_text("object_type,weight_kN\nBeam,94.8\n",encoding="utf8")
    def _save_audit(self):
        (self.export/"ETABS_OpenSees_Beam_Weight_Reconciliation.json").write_text(
            json.dumps(self.audit),encoding="utf8")

    def test_independent_beam_audit_and_readonly_candidate(self):
        result=beam_checks(self.export,source_beam_csv=self.weight)
        self.assertTrue(result["candidate_eligible"])
        self.assertAlmostEqual(result["reconstructed_clear_kN"],94.8)
        report_dir,report=review(self.export,etabs_beam_csv=self.weight)
        self.assertTrue((report_dir/"GRAVITY_SAFE_REVIEW.txt").exists())
        old=(self.export/"OpenSees_Complete_Model_Config_V118.json").read_bytes()
        with self.assertRaisesRegex(ValueError,"acknowledgement"):
            stage_candidate(self.export,report_dir/"GRAVITY_SAFE_REVIEW.json",
                approval_text="yes")
        candidate=stage_candidate(
            self.export,report_dir/"GRAVITY_SAFE_REVIEW.json",
            approval_text="I REVIEWED ETABS BEAM SELF WEIGHT AND SOURCE GEOMETRY")
        self.assertTrue((candidate/"CANDIDATE_PROVENANCE.json").exists())
        staged=json.loads((candidate/"OpenSees_Complete_Model_Config_V118.json").read_text())
        self.assertEqual(staged["etabs_beam_weight_policy"],"ETABS_BEAM_CLEAR_LENGTH")
        self.assertEqual((self.export/"OpenSees_Complete_Model_Config_V118.json").read_bytes(),
                         old)

    def test_isolated_approved_candidate_never_overwrites_original(self):
        required=[
            "OpenSees_Element_Connectivity.json",
            "OpenSees_Section_Assignment_Audit.json",
            "OpenSees_Load_Conversion_Audit.json",
            "OpenSees_Source_Model_Metadata_V118.json"]
        for name in required:
            (self.export/name).write_text(json.dumps({"source":name}),encoding="utf8")
        folder,review_data=review(self.export,etabs_beam_csv=self.weight)
        candidate=stage_candidate(self.export,folder/"GRAVITY_SAFE_REVIEW.json",
                    approval_text="I REVIEWED ETABS BEAM SELF WEIGHT AND SOURCE GEOMETRY")
        original=(self.export/"OpenSees_Complete_Model_Config_V118.json").read_bytes()
        def builder(target):
            (target/"OpenSees_Complete_Model_Data_V118.json").write_text(
                '{"gravity":{"Self Weight":{}}}',encoding="utf8")
            (target/"OpenSees_Complete_Gravity_Model.py").write_text(
                "print('requires native validation')\n",encoding="utf8")
            return {"gravity_model_script":"OpenSees_Complete_Gravity_Model.py"},{
                "analysis_ready":True,"assembly_errors":[]}
        rebuilt=build_isolated_candidate(self.export,candidate,build_callback=builder)
        self.assertTrue((rebuilt/"ISOLATED_CANDIDATE_PROVENANCE.json").is_file())
        info=json.loads((rebuilt/"ISOLATED_CANDIDATE_PROVENANCE.json").read_text())
        self.assertEqual(info["state"],"CANDIDATE_ASSEMBLED_NEEDS_NATIVE_GRAVITY_VALIDATION")
        self.assertFalse(info["native_gravity_solver_executed"])
        self.assertFalse(info["etabs_equivalence_established"])
        self.assertEqual(original,
            (self.export/"OpenSees_Complete_Model_Config_V118.json").read_bytes())
        self.assertEqual(
            json.loads((rebuilt/"OpenSees_Complete_Model_Config_V118.json").read_text())[
                "etabs_beam_weight_policy"],"ETABS_BEAM_CLEAR_LENGTH")
        with self.assertRaises(FileExistsError):
            build_isolated_candidate(self.export,candidate,build_callback=builder)

    def test_missing_and_invalid_offset_blocks_candidate(self):
        self.audit["rows"][0]["end_j_m"]=None
        self._save_audit()
        r=beam_checks(self.export,source_beam_csv=self.weight)
        self.assertFalse(r["candidate_eligible"])
        self.assertTrue(any("missing ETABS end offsets" in x for x in r["issues"]))
        self.audit["rows"][0]["end_j_m"]=7.0
        self._save_audit()
        r=beam_checks(self.export,source_beam_csv=self.weight)
        self.assertFalse(r["candidate_eligible"])
        self.assertTrue(any("invalid end offsets" in x for x in r["issues"]))

    def test_user_entered_beam_number_does_not_qualify(self):
        r=beam_checks(self.export,source_beam_weight=94.8)
        self.assertTrue(r["within_screening_tolerance"])
        self.assertFalse(r["candidate_eligible"])

    def test_wrong_independent_weight_does_not_pass(self):
        self.weight.write_text("object_type,weight_kN\nBeam,100.0\n",encoding="utf8")
        r=beam_checks(self.export,source_beam_csv=self.weight)
        self.assertFalse(r["candidate_eligible"])

    def test_source_double_subtraction_blocks(self):
        cfg=self.export/"OpenSees_Complete_Model_Config_V118.json"
        cfg.write_text(json.dumps({"joint_volume_weight_policy":"VERIFIED_SINGLE_OWNER"}))
        self.assertFalse(beam_checks(self.export,source_beam_csv=self.weight)[
            "candidate_eligible"])

    def test_support_region_still_exposes_individual_mismatch(self):
        nodes={"rows":[
            dict(status="MATCHED_GLOBAL_Z",etabs_point="264",
                 opensees_node="41",etabs_global_rz_kN=100.0,
                 opensees_rz_kN=30.0),
            dict(status="MATCHED_GLOBAL_Z",etabs_point="725",
                 opensees_node="9",etabs_global_rz_kN=0.0,
                 opensees_rz_kN=70.0)]}
        mapping=self.root/"source_regions.csv"
        with mapping.open("w",newline="",encoding="utf8") as f:
            w=csv.writer(f);w.writerow(
                ["etabs_point","region_id","region_type","verified","source_basis"])
            w.writerow(["264","CORE_A","CORE","YES","Original EDB wall polygon review"])
            w.writerow(["725","CORE_A","CORE","YES","Original EDB wall polygon review"])
        result=foundation_regions(nodes,mapping,etabs_base_reaction_kN=100.)
        self.assertAlmostEqual(result["rows"][0]["difference_kN"],0.)
        self.assertAlmostEqual(result["rows"][0]["max_individual_difference_kN"],70.)
        self.assertEqual(result["status"],"DIAGNOSTIC_NOT_STRUCTURAL_ACCEPTANCE")
        self.assertEqual(len(result["original_individual_rows"]),2)
    def test_unverified_or_incomplete_region_map_fails_closed(self):
        nodes={"rows":[dict(status="MATCHED_GLOBAL_Z",etabs_point="264",
                 etabs_global_rz_kN=10,opensees_rz_kN=10),
              dict(status="UNMATCHED_ETABS",etabs_point="725")]}
        mapping=self.root/"m.csv"
        mapping.write_text("etabs_point,region_id,region_type,verified,source_basis\n"
            "264,WALL_A,WALL_PIER,YES,ETABS actual polygon\n")
        with self.assertRaisesRegex(ValueError,"Unmatched"):
            foundation_regions(nodes,mapping)


if __name__=="__main__":
    unittest.main()
