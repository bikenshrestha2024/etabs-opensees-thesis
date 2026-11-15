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
    def test_axial_analytic_comparison_uses_endpoint_tags_not_list_order(self):
        data=cantilever_example()
        data["nodes"].reverse()
        result=run_standalone(data,ops=FakeOps())
        check=axial_cantilever_check(data,result)
        self.assertTrue(check["pass"])
        self.assertAlmostEqual(check["expected_uz_m"],-4e-5)
        self.assertAlmostEqual(check["actual_uz_m"],-4e-5)

    def test_reject_disconnected_extra_node_before_solver_setup(self):
        data=cantilever_example()
        data["nodes"].append({"tag":3,"xyz":[1,0,1],"fixity":[0]*6})
        with self.assertRaisesRegex(ValueError,"Exactly two connected"):
            validate_model(data)
        fake=FakeOps()
        with self.assertRaisesRegex(ValueError,"Exactly two connected"):
            run_standalone(data,ops=fake)
        self.assertEqual(fake.calls,[])

    def test_boolean_fixity_and_element_tag_are_invalid(self):
        data=cantilever_example()
        data["nodes"][0]["fixity"][0]=True
        with self.assertRaisesRegex(ValueError,"integer binary fixity"):
            validate_model(data)
        data=cantilever_example()
        data["elements"][0]["tag"]=True
        with self.assertRaisesRegex(ValueError,"Invalid element tag"):
            validate_model(data)

    def test_nondict_element_is_explicitly_rejected(self):
        data=cantilever_example()
        data["elements"]=[None]
        with self.assertRaisesRegex(ValueError,"Element must be a mapping"):
            validate_model(data)

    def test_unhashable_or_boolean_connectivity_does_not_crash_validator(self):
        for bad in ([1], True, "1"):
            data=cantilever_example()
            data["elements"][0]["nodes"][0]=bad
            with self.subTest(endpoint=repr(bad)):
                with self.assertRaisesRegex(ValueError,"integer node tags"):
                    validate_model(data)
        for bad in ([2],True,{}):
            data=cantilever_example()
            data["loads"][0]["node"]=bad
            with self.subTest(load_node=repr(bad)):
                with self.assertRaisesRegex(ValueError,"unknown integer node tag"):
                    validate_model(data)

    def test_malformed_load_and_source_are_actionable_errors(self):
        data=cantilever_example()
        data["loads"]=[None]
        with self.assertRaisesRegex(ValueError,"Nodal load must be a mapping"):
            validate_model(data)
        for description in (123,[], "  "):
            data=cantilever_example()
            data["source"]["description"]=description
            with self.assertRaisesRegex(ValueError,"text model source"):
                validate_model(data)

    def test_force_balance_does_not_mask_unbalanced_global_moment(self):
        data=cantilever_example()
        data["loads"][0]["force"][0]=10.0
        class MissingSupportMoment(FakeOps):
            def __getattr__(self,name):
                base=super().__getattr__(name)
                if name!="nodeReaction":
                    return base
                def response(*args):
                    if args==(1,1):return -10.0
                    return base(*args)
                return response
        fake=MissingSupportMoment()
        with self.assertRaisesRegex(RuntimeError,"moment equilibrium FAILED"):
            run_standalone(data,ops=fake)

    def test_moment_residual_reported_in_separate_3d_equilibrium_gate(self):
        data=cantilever_example()
        result=run_standalone(data,ops=FakeOps())
        self.assertEqual(result["moment_residual_kNm"],[0.0,0.0,0.0])
        self.assertEqual(result["force_residual_kN"],[0.0,0.0,0.0])

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
