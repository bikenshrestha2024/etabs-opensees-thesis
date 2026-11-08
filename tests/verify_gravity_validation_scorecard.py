"""Tests for conservative gravity validation and original evidence provenance."""
import json
import tempfile
import unittest
from pathlib import Path
from components.gravity.validation_scorecard import (
    create_gravity_scorecard,save_gravity_scorecard)


class GravityScorecardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.export=self.base/"export";self.export.mkdir()
        self.gravity=self.base/"gravity";self.gravity.mkdir()
        self.direct=self.gravity/"Gravity_ETABS_OpenSees_Direct";self.direct.mkdir()
        (self.export/"OpenSees_Complete_Model_Config_V118.json").write_text(
            json.dumps({"etabs_beam_weight_policy":"GROSS_SECTION_LENGTH",
              "etabs_clear_beam_weight_confirmed":False}))
        (self.export/"ETABS_OpenSees_Beam_Weight_Reconciliation.json").write_text(
            json.dumps({"policy":"GROSS_SECTION_LENGTH",
              "gross_beam_weight_kN":53984.055,
              "selected_beam_weight_kN":53984.055,
              "potential_offset_reduction_kN":8652.444,
              "unresolved_offset_count":0}))
        (self.export/"OpenSees_Joint_Volume_Ownership_Audit.json").write_text(
            json.dumps({"policy":"AUDIT_ONLY","geometry_verified":False,
                         "potentially_duplicated_RCC_weight_kN":19358.527}))
        (self.gravity/"Gravity_Result_V110.json").write_text(json.dumps(
            {"ok":True,"report":{"applied_vertical_load_kN":320047.788933,
                  "support_vertical_reaction_kN":320047.788933}}))
        self.diff={"etabs_base_FZ_kN":311367.313879,
              "opensees_support_FZ_kN":320047.788933,
              "node_comparison":{"valid_one_to_one_global_z_count":76,
                  "ambiguous_count":0,"axis_unverified_count":0,
                  "etabs_unmatched_count":0,"opensees_unmatched_count":0},
              "top_node_discrepancies":[{"etabs_point":"264",
                  "opensees_node":41,"abs_delta_kN":10861.4,
                  "etabs_global_rz_kN":14748.52},
                  {"etabs_point":"725","opensees_node":9,
                   "abs_delta_kN":4627.4,"etabs_global_rz_kN":0.0}]}
        (self.direct/"Direct_Gravity_Comparison.json").write_text(
            json.dumps(self.diff))
    def test_actual_failed_global_and_support_gates_and_optional_files(self):
        missing=[{"file":"source/missing_"+str(n),"required":False}
                 for n in range(7)]
        score=create_gravity_scorecard(
            self.export,self.gravity,self.gravity,missing,[])
        by_key={x["key"]:x for x in score["rows"]}
        self.assertEqual(score["conclusion"],"NOT_STRUCTURALLY_VALIDATED")
        self.assertEqual(by_key["global"]["status"],"NOT_VALIDATED")
        self.assertAlmostEqual(by_key["global"]["value"]["opensees_minus_etabs_kN"],
                               8680.475054,places=4)
        self.assertEqual(by_key["foundation"]["status"],"NOT_VALIDATED")
        self.assertEqual(by_key["foundation"]["value"]["verified_matches"],76)
        self.assertEqual(len(by_key["foundation"]["value"]["large_difference_examples"]),2)
        self.assertEqual(by_key["evidence"]["value"]["optional_missing_count"],7)
        self.assertEqual(by_key["evidence"]["status"],"INCOMPLETE")
        self.assertEqual(by_key["beam_weight"]["status"],"GROSS_BEAM_WEIGHT_ACTIVE")
        self.assertEqual(by_key["joint_volume"]["status"],"GEOMETRY_NOT_VERIFIED")
        save_gravity_scorecard(self.base/"output",score)
        self.assertIn("Global gravity load agreement",
            (self.base/"output"/"GRAVITY_VALIDATION_SCORECARD.txt").read_text())
        self.assertIn("Individual foundation reactions",
            (self.base/"output"/"GRAVITY_VALIDATION_SCORECARD.csv").read_text(
                encoding="utf-8-sig"))
    def test_numerically_matched_global_cannot_be_engineering_accepted(self):
        self.diff["opensees_support_FZ_kN"]=311367.313879
        self.diff["top_node_discrepancies"]=[{
            "etabs_point":"1","opensees_node":1,
            "abs_delta_kN":0.1,"etabs_global_rz_kN":1000.}]
        (self.direct/"Direct_Gravity_Comparison.json").write_text(
            json.dumps(self.diff))
        score=create_gravity_scorecard(
            self.export,self.gravity,self.gravity,[],[])
        d={x["key"]:x for x in score["rows"]}
        self.assertEqual(d["global"]["status"],
                         "WITHIN_SCREENING_TOLERANCE_NOT_ACCEPTED")
        self.assertEqual(d["foundation"]["status"],
                         "WITHIN_SCREENING_TOLERANCE_NOT_ACCEPTED")
        self.assertFalse(score["corrected_gravity_model_certified"])
    def test_missing_native_evidence_is_not_accepted(self):
        (self.direct/"Direct_Gravity_Comparison.json").unlink()
        score=create_gravity_scorecard(
            self.export,self.gravity,self.gravity,[],[])
        d={x["key"]:x for x in score["rows"]}
        self.assertEqual(d["global"]["status"],"MISSING_ETABS_DIRECT_EVIDENCE")
        self.assertEqual(d["foundation"]["status"],"MISSING_OR_AMBIGUOUS_EVIDENCE")


if __name__=="__main__":
    unittest.main()
