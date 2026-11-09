"""Synthetic tests of source-derived gravity and beam-offset diagnostic.

No ETABS fitting; no OpenSees solver required.
"""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from components.gravity.source_load_reconciliation import source_load_audit


class SourceLoadAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.out=self.root/"outputs"
        self.data={
            "load_provenance":[
                dict(pattern="Self Weight",component="self_weight_beam",
                     source="FRAME:101",node=1,downward_kN=80.),
                dict(pattern="Self Weight",component="self_weight_shear wall",
                     source="AREA:55",node=2,downward_kN=40.),
                dict(pattern="Live",component="area_load",
                     source="AREA:56",node=3,downward_kN=20.)],
            "unfactored_patterns":{"Self Weight":{"1":[0,0,-80],
                "2":[0,0,-40]},"Live":{"3":[0,0,-20]}},
            "total_downward_load_kN":140.,
            "gravity_by_pattern_kN":{"Self Weight":120.,"Live":20.}}
        self.cfg={"gravity_factors":{"Self Weight":1.,"Live":.3},
                  "mass_factors":{"Self Weight":1.,"Live":.3},
                  "etabs_beam_weight_policy":"GROSS_SECTION_LENGTH"}
        self.meta={"pattern_types":{"Self Weight":1,"Live":3}}
        self.beam={"potential_offset_reduction_kN":8.,
                   "gross_beam_weight_kN":80.,
                   "etabs_clear_weight_confirmed":False,
                   "unresolved_offset_count":0}
        for filename,value in [
            ("OpenSees_Complete_Model_Data_V118.json",self.data),
            ("OpenSees_Complete_Model_Config_V118.json",self.cfg),
            ("OpenSees_Source_Model_Metadata_V118.json",self.meta),
            ("OpenSees_Load_Conversion_Audit.json",{}),
            ("ETABS_OpenSees_Beam_Weight_Reconciliation.json",self.beam),
            ("Gravity_Single_Count_Self_Weight_Audit.json",
             {"status":"SELF_WEIGHT_PATTERN_ACCOUNTING_PASS_NOT_JOINT_SOLID_VALIDATED",
              "full_DL_LL_physical_self_weight_coefficient":1.0,
              "etabs_pattern_rows":[
                  {"pattern":"Self Weight","etabs_self_weight_multiplier":1.0}]}),
            ("Gravity_Slab_Self_Weight_Audit.json",
             {"gross_slab_self_weight_kN":0.0}),
            ("Gravity_Physical_Weight_Modifier_Audit.json",
             {"status":"NATIVE_WEIGHT_MODIFIERS_VERIFIED",
              "source_weight_modifier_verified":True,
              "source_weight_conflict":False})]:
            (self.root/filename).write_text(json.dumps(value),encoding="utf8")
        self.fake=types.ModuleType("OpenSees_Complete_Export_V118")
        def apply(data,cfg,profile,types):
            self.assertEqual(profile,"GRAVITY_1.0D_1.0L")
            factors={"Self Weight":1.,"Live":1.}
            # Independent assembled un-factored force vectors are the
            # expected ledger; never derive both sides of a test from
            # the same load_provenance records.
            ledger={pat:-sum(float(vec[2]) for vec in nodes.values())
                    for pat,nodes in data["unfactored_patterns"].items()}
            data["gravity_by_pattern_kN"]=ledger
            data["total_downward_load_kN"]=sum(ledger.values())
            return {"profile":profile,"factors":factors}
        self.fake.apply_gravity_profile=apply

    def run_audit(self,**kwargs):
        with patch.dict(sys.modules,{"OpenSees_Complete_Export_V118":self.fake}):
            return source_load_audit(self.root,"GRAVITY_1.0D_1.0L",self.out,**kwargs)

    def test_all_components_auto_sum_and_full_live(self):
        info=self.run_audit(etabs_total_kN=132.)
        self.assertEqual(info["applied_total_kN"],140.)
        self.assertEqual(info["gravity_by_component_kN"]["self_weight_beam"],80.)
        self.assertEqual(info["gravity_by_component_kN"]["self_weight_shear wall"],40.)
        self.assertEqual(info["gravity_by_component_kN"]["area_load"],20.)
        self.assertEqual(info["source_to_etabs_difference_kN"],8.)
        self.assertEqual(info["post_offset_total_hypothesis_kN"],132.)
        self.assertFalse(info["beam_offset_verified"])
        self.assertEqual(info["status"],"SOURCE_LEDGER_RECONCILED_NOT_ETABS_VALIDATED")
        self.assertTrue((self.out/"Gravity_Source_Components_Audit.xlsx").is_file())
        self.assertTrue((self.out/"Gravity_Source_Components_Detail.csv").is_file())

    def test_mismatch_in_source_provenance_blocks_audit(self):
        self.data["load_provenance"][0]["downward_kN"]=81.
        (self.root/"OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps(self.data),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"does not reconcile"):
            self.run_audit()

    def test_legacy_export_does_not_claim_single_count_validation(self):
        (self.root/"Gravity_Single_Count_Self_Weight_Audit.json").unlink()
        # Legacy runs cannot have a new independent physical slab audit
        # without the self-weight pattern source evidence.
        (self.root/"Gravity_Slab_Self_Weight_Audit.json").unlink()
        info=self.run_audit()
        self.assertEqual(info["status"],"LEGACY_EXPORT_SINGLE_COUNT_NOT_VERIFIED")

    def test_physical_slab_15kn_matches_applied_source_nodes(self):
        self.data["load_provenance"].append(
            dict(pattern="Self Weight",component="self_weight_floor",
                 source="AREA:57",node=4,downward_kN=15.))
        self.data["unfactored_patterns"]["Self Weight"]["4"]=[0,0,-15]
        (self.root/"OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps(self.data),encoding="utf8")
        (self.root/"Gravity_Slab_Self_Weight_Audit.json").write_text(
            json.dumps({"gross_slab_self_weight_kN":15.}),encoding="utf8")
        info=self.run_audit()
        self.assertEqual(info["actual_applied_slab_self_weight_kN"],15.)
        self.assertEqual(info["expected_full_gravity_slab_self_weight_kN"],15.)
        self.assertTrue(info["slab_source_conservation_verified"])

    def test_zero_self_weight_roof_live_eqx_does_not_need_gravity_factor(self):
        path=self.root/"Gravity_Single_Count_Self_Weight_Audit.json"
        audit=json.loads(path.read_text(encoding="utf8"))
        for name in ("Roof Live","EQX","EQY","~RSX P DeltaECC"):
            audit["etabs_pattern_rows"].append({
                "pattern":name,"etabs_self_weight_multiplier":0.0})
        path.write_text(json.dumps(audit),encoding="utf8")
        result=self.run_audit()
        self.assertEqual(result["expected_full_gravity_slab_self_weight_kN"],0.)
        self.assertTrue(result["slab_source_conservation_verified"])

    def test_nonzero_unclassified_slab_weight_still_blocks(self):
        path=self.root/"Gravity_Single_Count_Self_Weight_Audit.json"
        audit=json.loads(path.read_text(encoding="utf8"))
        audit["etabs_pattern_rows"].append({
            "pattern":"Roof Live","etabs_self_weight_multiplier":0.25})
        path.write_text(json.dumps(audit),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"NONZERO Roof Live"):
            self.run_audit()


    def test_slab_double_weight_or_omission_is_rejected(self):
        (self.root/"Gravity_Slab_Self_Weight_Audit.json").write_text(
            json.dumps({"gross_slab_self_weight_kN":15.}),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"SLAB SELF-WEIGHT DOUBLE/OMISSION"):
            self.run_audit()

    def test_legacy_slab_export_does_not_claim_validated_source(self):
        (self.root/"Gravity_Slab_Self_Weight_Audit.json").unlink()
        info=self.run_audit()
        self.assertEqual(info["status"],"LEGACY_EXPORT_SLAB_PHYSICAL_WEIGHT_NOT_VERIFIED")

    def test_legacy_native_weight_modifier_evidence_is_not_validated(self):
        (self.root/"Gravity_Physical_Weight_Modifier_Audit.json").unlink()
        info=self.run_audit()
        self.assertEqual(info["status"],"NATIVE_ETABS_WEIGHT_MODIFIERS_NOT_VERIFIED")
    def test_source_nonunity_weight_modifier_blocks_equivalence(self):
        (self.root/"Gravity_Physical_Weight_Modifier_Audit.json").write_text(
            json.dumps({"status":"SOURCE_NATIVE_WEIGHT_MODIFIER_CONFLICT",
                        "source_weight_modifier_verified":False,
                        "source_weight_conflict":True}),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"not unity"):
            self.run_audit()

    def test_no_source_ledger_fails_closed(self):
        self.data.pop("load_provenance")
        (self.root/"OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps(self.data),encoding="utf8")
        with self.assertRaisesRegex(ValueError,"no complete load_provenance"):
            self.run_audit()

    def test_missing_beam_audit_blocks_conditional_claim(self):
        (self.root/"ETABS_OpenSees_Beam_Weight_Reconciliation.json").unlink()
        with self.assertRaises(FileNotFoundError):
            self.run_audit()

if __name__=="__main__":
    unittest.main()
