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
            ("ETABS_OpenSees_Beam_Weight_Reconciliation.json",self.beam)]:
            (self.root/filename).write_text(json.dumps(value),encoding="utf8")
        self.fake=types.ModuleType("OpenSees_Complete_Export_V118")
        def apply(data,cfg,profile,types):
            self.assertEqual(profile,"GRAVITY_1.0D_1.0L")
            factors={"Self Weight":1.,"Live":1.}
            ledger={"Self Weight":120.,"Live":20.}
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
