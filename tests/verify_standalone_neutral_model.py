"""Solver-free boundary tests; no ETABS or OpenSeesPy dependency."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest
from src.thesis_core.neutral_model import cantilever_example,model_sha256,validate_model
from src.opensees_engine.standalone import run_standalone,axial_cantilever_check

ROOT=Path(__file__).resolve().parents[1]
class FakeOps:
    def __init__(self):self.calls=[]
    def __getattr__(self,name):
        def method(*args):
            self.calls.append((name,args))
            if name=="analyze":return 0
            if name=="nodeDisp":return -4e-5 if args==(2,3) else 0.
            if name=="nodeReaction":return 100. if args==(1,3) else 0.
            return None
        return method

class StandaloneBoundaryTests(unittest.TestCase):
    def test_contract_and_mocked_solver_call_path(self):
        data=cantilever_example();sha=model_sha256(data)
        result=run_standalone(data,ops=FakeOps())
        self.assertEqual(result["model_sha256"],sha)
        self.assertEqual(result["status"],"NUMERICALLY_CONVERGED_ONLY")
        self.assertTrue(axial_cantilever_check(data,result)["pass"])
    def test_reject_unsupported_wall_without_fallback(self):
        data=cantilever_example();data["elements"][0]["type"]="SFI-MVLEM-3D"
        with self.assertRaisesRegex(ValueError,"Unsupported element"):
            validate_model(data)
    def test_reject_unregistered_units_and_version(self):
        for key,value in (("units","N-mm-s"),("schema_version","2.0")):
            data=cantilever_example();data[key]=value
            with self.assertRaises(ValueError):validate_model(data)
    def test_no_etabs_import_in_core(self):
        for base in ("src/thesis_core","src/opensees_engine"):
            for file in (ROOT/base).rglob("*.py"):
                tree=ast.parse(file.read_text(encoding="utf-8"))
                names=[x.module or "" for x in ast.walk(tree) if isinstance(x,ast.ImportFrom)]
                names += [n.name for x in ast.walk(tree) if isinstance(x,ast.Import) for n in x.names]
                forbidden=("comtypes","win32com","etabs","src.etabs_adapter","OpenSees_Project_Inputs_V123")
                self.assertFalse([n for n in names if n.lower().startswith(forbidden)],
                                 str(file))
    def test_nonparallel_vecxz_required(self):
        data=cantilever_example();data["elements"][0]["vecxz"]=[0,0,1]
        with self.assertRaisesRegex(ValueError,"parallel"):validate_model(data)

if __name__=="__main__":unittest.main()
