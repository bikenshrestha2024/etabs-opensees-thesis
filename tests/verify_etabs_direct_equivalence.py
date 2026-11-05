"""ETABS direct COM API adapter contract without ETABS (Python 3.12 CI).

The mock faithfully supplies the official CSI out-array ordering; a native
Windows ETABS v23 integration still requires independent verification.
"""
import tempfile
import unittest
from pathlib import Path
from components.validation.etabs_direct_api import (
    extract_from_sap, validate_mapping, _arrays,
)
from components.validation.etabs_equivalence_report import evaluate,export_excel
from components.validation.etabs_comparison import FIELDS


class Setup:
    def __init__(self):
        self.cases={"RSX":False,"MODAL":True}
        self.combos={"ENVELOPE":True}
    def DeselectAllCasesAndCombosForOutput(self):
        self.cases={k:False for k in self.cases}
        self.combos={k:False for k in self.combos}
        return 0
    def SetCaseSelectedForOutput(self,k):
        if k not in self.cases:return 1
        self.cases[k]=True;return 0
    def SetComboSelectedForOutput(self,k):
        if k not in self.combos:return 1
        self.combos[k]=True;return 0
    def GetCaseSelectedForOutput(self,k):return (self.cases[k],0)
    def GetComboSelectedForOutput(self,k):return (self.combos[k],0)


class Names:
    def __init__(self,names):self.names=list(names)
    def GetNameList(self):return (len(self.names),self.names,0)


class Results:
    def __init__(self,setup):self.Setup=setup
    def BaseReact(self):
        return (1,["RSX"],["Max"],[0.],[100.],[0.],[0.],
                [0.],[0.],[0.],0.,0.,0.,0)
    def StoryDrifts(self):
        return (2,["Story25","Story24"],["RSX","RSX"],
                ["Max","Max"],[0.,0.],["X","X"],
                [0.002,0.001],[ "J1","J2"],
                [0.,0.],[0.,0.],[95.,91.2],0)
    def ModalPeriod(self):
        return (1,["MODAL"],["Mode"],[1.],[3.5],
                [1/3.5],[2*3.14159265/3.5],[.5],0)
    def ModalParticipatingMassRatios(self):
        return (1,["MODAL"],["Mode"],[1.],[3.5],
                [0.65],[0.15],[0.],[0.65],[0.15],[0.],
                [0.],[0.],[0.1],[0.],[0.],[0.1],0)
    def JointDispl(self,name,typ):
        if name!="JOINT25" or typ!=0:raise RuntimeError("Unexpected point")
        return (1,[name],[name],["RSX"],["Max"],[0.],
                [.045],[.001],[0.],[0.],[0.],[0.],0)


class FakeSap:
    def __init__(self,edb):
        self.edb=edb
        self.units=3
        self.LoadCases=Names(["RSX","MODAL"])
        self.RespCombo=Names(["ENVELOPE"])
        self.Results=Results(Setup())
    def GetModelFilename(self):return str(self.edb)
    def GetPresentUnits(self):return self.units
    def SetPresentUnits(self,v):self.units=v;return 0


def mapping(path,approval=True):
    return {"source_edb":str(path),"assumptions_verified":approval,
            "percent_limits":{"base_shear":5,"drift_ratio":5,"displacement":5,"period":2},
            "cases":[
             {"etabs_case":"MODAL","method":"MODAL","limit_state":"ULS","case":"MODAL",
              "axis":"X","modal_mode_pairing_verified":True},
             {"etabs_case":"RSX","method":"MRSM","limit_state":"ULS","case":"X_E0","axis":"X",
              "story_map":{"Story25":25,"Story24":24},
              "points":[{"etabs_point":"JOINT25","story_number":25}],
              "force_basis_verified":True,"force_scale_note":"Same spectrum CQC & NBC force scale",
              "displacement_basis_verified":True,
              "displacement_scale_note":"Same design CQC and point definition"}]}


class Tests(unittest.TestCase):
    def test_model_source_units_and_selection_are_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"source.edb";path.write_bytes(b"read only source")
            sap=FakeSap(path)
            rows=extract_from_sap(sap,mapping(path))
            self.assertEqual(sap.units,3)
            self.assertEqual(sap.Results.Setup.cases,{"RSX":False,"MODAL":True})
            self.assertEqual(sap.Results.Setup.combos,{"ENVELOPE":True})
            index={(r["metric"],r["location"]):r for r in rows}
            self.assertAlmostEqual(index[("period","1")]["value"],3.5)
            self.assertAlmostEqual(index[("base_shear","BASE")]["value"],100)
            self.assertAlmostEqual(index[("drift_ratio","25")]["value"],.002)
            self.assertAlmostEqual(index[("displacement","25")]["value"],.045)
            self.assertEqual(index[("displacement","25")]["unit"],"m")
            self.assertEqual(index[("period","1")]["axis"],"")
            self.assertEqual(index[("drift_ratio","25")]["unit"],"ratio")

    def test_wrong_source_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"source.edb";path.write_bytes(b"x")
            other=Path(tmp)/"other.edb";other.write_bytes(b"y")
            sap=FakeSap(path)
            with self.assertRaisesRegex(ValueError,"NOT selected source"):
                extract_from_sap(sap,mapping(other))
            self.assertEqual(sap.units,3)

    def test_missing_real_case_mapping_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"story-name"):
            validate_mapping({"cases":[dict(etabs_case="RSX",method="MRSM",
                limit_state="ULS",case="X_E0",axis="X")]})

    def test_incorrect_api_tuple_never_silently_shifts(self):
        with self.assertRaisesRegex(RuntimeError,"expected"):
            _arrays((1,[2],0),11,"StoryDrifts")

    def test_evidence_gate_and_screening(self):
        base=dict(method="MRSM",limit_state="ULS",case="X_E0",axis="X",
                  location="BASE",metric="base_shear",unit="kN",basis="CQC_force_scaled")
        ref=[dict(base,value=100.)]
        ours=[dict(base,value=102.)]
        self.assertEqual(evaluate(ours,ref,FIELDS)[0]["status"],"NOT_COMPARABLE")
        self.assertEqual(evaluate(ours,ref,FIELDS,{"assumptions_verified":True})[0]["status"],"PASS")
        self.assertEqual(evaluate([dict(base,value=110.)],ref,FIELDS,{"assumptions_verified":True})[0]["status"],"FAIL")
        wrong=[dict(base,value=100.,basis="ETABS_unverified")]
        self.assertEqual(evaluate(ours,wrong,FIELDS,{"assumptions_verified":True})[0]["status"],"NOT_COMPARABLE")
        self.assertEqual(evaluate(ours,[],FIELDS,{"assumptions_verified":True})[0]["status"],"MISSING_ETABS")

    def test_zero_reference_absolute_tolerance_and_missing_opensees(self):
        base=dict(method="MRSM",limit_state="ULS",case="X_E0",axis="X",
                  location="25",metric="drift_ratio",unit="ratio",
                  basis="CQC_design_unscaled_by_7_5")
        res=evaluate([dict(base,value=.0000001)],[dict(base,value=0.)],
                     FIELDS,{"assumptions_verified":True})
        self.assertEqual(res[0]["status"],"PASS")
        self.assertIsNone(res[0]["percent_difference"])
        self.assertEqual(evaluate([],[dict(base,value=.001)],FIELDS)[0]["status"],"MISSING_OPENSEES")

    def test_excel_report_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=dict(method="MRSM",limit_state="ULS",case="X_E0",axis="X",
                      metric="drift_ratio",unit="ratio",
                      basis="CQC_design_unscaled_by_7_5")
            ours=[dict(base,location=str(i),value=.001*i) for i in (24,25)]
            refs=[dict(r,value=r["value"]*1.02) for r in ours]
            compared=evaluate(ours,refs,FIELDS,{"assumptions_verified":True})
            out=export_excel(tmp,ours,refs,compared,{"assumptions_verified":True})
            self.assertTrue(out.is_file())
            from openpyxl import load_workbook
            wb=load_workbook(out,read_only=True)
            self.assertIn("Profiles and Charts",wb.sheetnames)
            self.assertIn("Comparison",wb.sheetnames)
            wb.close()


if __name__=="__main__":unittest.main(verbosity=2)
