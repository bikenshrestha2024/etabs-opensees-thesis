"""Physical self weight must not inherit ULS stiffness reduction factors.

[REF docs/source/components/model/physical_weight_modifiers.py.md]
"""
import tempfile
import unittest
from pathlib import Path
from components.model.physical_weight_modifiers import (
    FRAME_LABELS,AREA_LABELS,decode_api_modifiers,
    review_physical_weight_modifiers,extract_native_weight_modifiers)


def vector(labels,stiff=None,weight=1.,mass=1.):
    values={k:1. for k in labels}
    values.update(stiff or {})
    values.update(mass=mass,weight=weight)
    return values


class FakeAPI:
    def __init__(self, mapping):
        self.mapping=mapping
    def GetModifiers(self,name):
        value=self.mapping[name]
        return [list(value.values()),0]


class NativeWeightTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.record={
            "schema":"etabs-native-independent-modifiers-v1",
            "complete":True,"errors":[],
            "records":[
                dict(kind="frame",object="B101",section="RC_Beam",
                     object_modifiers=vector(FRAME_LABELS,{"I22":.35,"I33":.35}),
                     section_modifiers=vector(FRAME_LABELS)),
                dict(kind="area",object="W01",section="Wall300",
                     object_modifiers=vector(AREA_LABELS,{"f11":.5,"f22":.5,"m11":.1,"m22":.1}),
                     section_modifiers=vector(AREA_LABELS)),
            ]}
        self.patterns=[dict(pattern="Self Weight",multiplier=1.),
                       dict(pattern="Floor Live",multiplier=0.)]

    def test_stiffness_modifiers_do_not_reduce_physical_weight(self):
        result=review_physical_weight_modifiers(
            self.record,self.patterns,self.root)
        self.assertEqual(result["full_gravity_dead_weight_coefficient"],1.)
        self.assertTrue(result["source_weight_modifier_verified"])
        self.assertFalse(result["source_weight_conflict"])
        self.assertEqual(result["status"],"NATIVE_WEIGHT_MODIFIERS_VERIFIED")
        self.assertTrue((self.root/"Gravity_Physical_Weight_Modifier_Audit.xlsx").is_file())

    def test_nonunit_native_weight_rejected_and_preserved_in_evidence(self):
        self.record["records"][0]["object_modifiers"]["weight"]=.5
        result=review_physical_weight_modifiers(self.record,self.patterns,self.root)
        self.assertTrue(result["source_weight_conflict"])
        self.assertFalse(result["source_weight_modifier_verified"])
        self.assertIn("modifier=0.5"," ".join(result["evidence_issues"]))

    def test_legacy_evidence_cannot_certify_etabs_weight(self):
        result=review_physical_weight_modifiers(None,self.patterns,self.root)
        self.assertFalse(result["source_weight_modifier_verified"])
        self.assertEqual(result["status"],"NATIVE_WEIGHT_OR_MASS_EVIDENCE_INCOMPLETE")

    def test_single_full_physical_weight_must_be_allocated(self):
        result=review_physical_weight_modifiers(self.record,
                 [dict(pattern="Dead",multiplier=.7)],self.root)
        self.assertFalse(result["source_weight_modifier_verified"] is False and
                         result["full_gravity_dead_weight_coefficient"]==1)
        self.assertTrue(any("expected 1.0" in issue for issue in result["evidence_issues"]))

    def test_decode_frame_and_area_api_vectors(self):
        values=decode_api_modifiers([list(vector(FRAME_LABELS,{"I22":.7}).values()),0],8,"F1")
        self.assertAlmostEqual(values["I22"],.7)
        area=decode_api_modifiers([list(vector(AREA_LABELS,{"m11":.25}).values()),0],10,"S1")
        self.assertAlmostEqual(area["m11"],.25)
        with self.assertRaisesRegex(ValueError,"did not succeed"):
            decode_api_modifiers([[1.]*8,1],8,"X")

    def test_native_extraction_object_and_section(self):
        class Sap:
            FrameObj=FakeAPI({"B101":vector(FRAME_LABELS,{"I22":.35})})
            PropFrame=FakeAPI({"RC_Beam":vector(FRAME_LABELS)})
            class AreaObj(FakeAPI):
                def GetNameList(self):return [1,["W01"],0]
                def GetProperty(self,name):return ["Wall300",0]
            AreaObj=AreaObj({"W01":vector(AREA_LABELS,{"m11":.1})})
            PropArea=FakeAPI({"Wall300":vector(AREA_LABELS)})
        result=extract_native_weight_modifiers(
            Sap(),[{"etabs_object":"B101","assigned_section":"RC_Beam"}])
        self.assertTrue(result["complete"],result["errors"])
        self.assertEqual(len(result["records"]),2)


if __name__=="__main__":
    unittest.main()
