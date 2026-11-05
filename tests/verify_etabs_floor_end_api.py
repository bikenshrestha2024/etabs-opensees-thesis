"""Mocked CSI ETABS v23 signed source-case API contract; no ETABS installed."""
import tempfile
import unittest
from pathlib import Path

from components.validation.etabs_floor_end_api import extract_centered_from_sap


class Setup:
    def __init__(self):
        self.cases={"XCM":False,"OTHER":True}
        self.combos={"COMBO":True}
    def DeselectAllCasesAndCombosForOutput(self):
        self.cases={k:False for k in self.cases}
        self.combos={k:False for k in self.combos}
        return 0
    def GetCaseSelectedForOutput(self,name):return self.cases[name],0
    def GetComboSelectedForOutput(self,name):return self.combos[name],0
    def SetCaseSelectedForOutput(self,name):
        if name not in self.cases:return 1
        self.cases[name]=True
        return 0
    def SetComboSelectedForOutput(self,name):
        if name not in self.combos:return 1
        self.combos[name]=True
        return 0


class Names:
    def __init__(self, names):self.names=names
    def GetNameList(self):return len(self.names),self.names,0


class Results:
    def __init__(self):
        self.Setup=Setup()
    def JointDispl(self,node,obj_type):
        if obj_type!=0:raise ValueError("Only object node output expected")
        value={"A":.012,"B":.031}[node]
        # CSI: NumberResults, Obj, Elm, Case, StepType, StepNum,
        # U1,U2,U3,R1,R2,R3,ret (13 tuple entries).
        return (1,[node],[node],["XCM"],["Step"],[1.],
                [value],[.008],[0.],[0.],[0.],[0.],0)


class Sap:
    def __init__(self,path):
        self.path=path
        self.units=3
        self.LoadCases=Names(["XCM","OTHER"])
        self.RespCombo=Names(["COMBO"])
        self.Results=Results()
    def GetModelFilename(self):return str(self.path)
    def GetPresentUnits(self):return self.units
    def SetPresentUnits(self,units):self.units=units;return 0


class ETABSFloorApiTests(unittest.TestCase):
    def kw(self,edb):
        return dict(source_edb=edb,limit_state="ULS",case="XCM",
                    axis="X",step_type="Step",step_number=1.,
                    reviewed_centered_cm=True)
    def geometry(self):
        return [dict(node_id="A",storey="25",is_perimeter="true"),
                dict(node_id="B",storey="25",is_perimeter="true"),
                dict(node_id="INTERIOR",storey="25",is_perimeter="false")]
    def test_signed_values_and_selection_state_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ULTIMATE.EDB";path.write_bytes(b"fake")
            sap=Sap(path)
            out=extract_centered_from_sap(sap,self.geometry(),**self.kw(path))
            self.assertEqual([r["ux_m"] for r in out],[.012,.031])
            self.assertEqual(sap.units,3)
            self.assertEqual(sap.Results.Setup.cases,{"XCM":False,"OTHER":True})
            self.assertEqual(sap.Results.Setup.combos,{"COMBO":True})
            self.assertEqual(out[0]["response_basis"],"signed_centered_linear_increment")
    def test_rejects_wrong_edb(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ULTIMATE.EDB";path.write_bytes(b"fake")
            other=Path(folder)/"SERVICE.EDB";other.write_bytes(b"different")
            with self.assertRaisesRegex(ValueError,"Active ETABS EDB differs"):
                extract_centered_from_sap(Sap(path),self.geometry(),**self.kw(other))
    def test_does_not_assume_centered_and_rejects_envelopes(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ULTIMATE.EDB";path.write_bytes(b"fake")
            with self.assertRaisesRegex(ValueError,"centered-CM"):
                extract_centered_from_sap(Sap(path),self.geometry(),
                    **{**self.kw(path),"reviewed_centered_cm":False})
            with self.assertRaisesRegex(ValueError,"not a CQC/max envelope"):
                extract_centered_from_sap(Sap(path),self.geometry(),
                    **{**self.kw(path),"step_type":"Max"})
    def test_wrong_selected_step_restores_state_on_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ULTIMATE.EDB";path.write_bytes(b"fake")
            sap=Sap(path)
            with self.assertRaisesRegex(RuntimeError,"exactly one signed"):
                extract_centered_from_sap(sap,self.geometry(),
                    **{**self.kw(path),"step_number":3.})
            self.assertEqual(sap.units,3)
            self.assertEqual(sap.Results.Setup.cases["OTHER"],True)


if __name__=="__main__":
    unittest.main(verbosity=2)
