"""Beam clear-length weight correction does not double-count joints."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from components.model.beam_weight_convention import (
    GROSS,CLEAR,build_beam_weight_audit,export_beam_weight_audit
)


class BeamWeightTests(unittest.TestCase):
    def setUp(self):
        self.frames={
            "1183":[
                dict(object="1183",category="BEAM",length=3.,
                     start=0.,end=3.,properties=dict(A=.48,weight=24.992618)),
                dict(object="1183",category="BEAM",length=3.,
                     start=3.,end=6.,properties=dict(A=.48,weight=24.992618))],
            "1172":[dict(object="1172",category="COLUMN",length=3.8,
                start=0.,end=3.8,properties=dict(A=1.21,weight=24.992618))]}
        self.meta={"1183":{"GetEndLengthOffset":[True,.55,.55,1.,0]},
                   "1172":{"GetEndLengthOffset":[True,0.,.8,1.,0]}}
    def test_default_does_not_change_source_weight(self):
        audit,windows=build_beam_weight_audit(self.frames,self.meta)
        self.assertEqual(audit["policy"],GROSS)
        self.assertEqual(windows["1183"],(0.,6.))
        self.assertAlmostEqual(audit["gross_beam_weight_kN"],6*.48*24.992618)
        self.assertAlmostEqual(audit["selected_beam_weight_kN"],
                               audit["gross_beam_weight_kN"])
        self.assertEqual(audit["beam_count"],1)
    def test_approved_clear_span_applied_only_to_beams(self):
        audit,windows=build_beam_weight_audit(
            self.frames,self.meta,policy=CLEAR,etabs_clear_weight_confirmed=True)
        self.assertEqual(windows["1183"],(.55,5.45))
        self.assertAlmostEqual(audit["selected_beam_weight_kN"],4.9*.48*24.992618)
        self.assertAlmostEqual(audit["potential_offset_reduction_kN"],
                               1.1*.48*24.992618)
        self.assertEqual(len(audit["rows"]),1)
        with tempfile.TemporaryDirectory() as d:
            export_beam_weight_audit(d,audit)
            self.assertTrue((Path(d)/"ETABS_OpenSees_Beam_Weight_Reconciliation.csv").exists())
    def test_no_unverified_silent_load_correction(self):
        with self.assertRaisesRegex(ValueError,"explicit verification"):
            build_beam_weight_audit(self.frames,self.meta,policy=CLEAR)
    def test_missing_offset_blocks_verified_mode(self):
        with self.assertRaisesRegex(ValueError,"Missing/invalid"):
            build_beam_weight_audit(self.frames,{},policy=CLEAR,
                                    etabs_clear_weight_confirmed=True)
    def test_oversized_offset_blocks_verified_mode(self):
        self.meta["1183"]["GetEndLengthOffset"]=[True,3.5,3.5,1.,0]
        with self.assertRaisesRegex(ValueError,"Missing/invalid"):
            build_beam_weight_audit(self.frames,self.meta,policy=CLEAR,
                                    etabs_clear_weight_confirmed=True)
    def test_config_rejects_double_weight_subtraction(self):
        src=(Path(__file__).resolve().parents[1]/
             'components/model/assembly.py').read_text('utf8')
        self.assertIn("Do not combine beam clear-length weight with single-owner",src)
        self.assertIn("start=max(start,seg['start'])",src)
        self.assertIn("end=min(end,seg['end'])",src)

if __name__=="__main__":
    unittest.main()
