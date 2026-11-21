"""Canonical output stage routing and cross-workflow writer ownership.

All fixtures operate in temporary local directories. No source model edited,
no OpenSees solver executed, no physical equivalence asserted.
"""
import ast
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_layout import owned_run_destination


class StageOwnershipTests(unittest.TestCase):
    def test_all_canonical_stages(self):
        stages={"GRAVITY":"02_GRAVITY", "ESM":"03_ESM", "MODAL":"04_MODAL",
                "MRSM":"05_MRSM", "LTHA":"06_LINEAR_TIME_HISTORY",
                "NLTHA":"07_NONLINEAR_TIME_HISTORY",
                "ETABS_COMPARISONS":"08_ETABS_COMPARISONS",
                "SOFTWARE_DIAGNOSTICS":"09_SOFTWARE_DIAGNOSTICS"}
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for stage,name in stages.items():
                with self.subTest(stage=stage):
                    result=owned_run_destination(root,stage,"Source_1")
                    self.assertEqual(result,root/name/"RUNS"/"Source_1")
                    self.assertFalse(result.exists())
                    self.assertEqual(
                        owned_run_destination(root,stage,"Source_1",selected=root),result)
                    self.assertEqual(
                        owned_run_destination(root,stage,"Source_1",
                          selected=root/"OpenSees_Analysis_Results"/"old-case"),result)
                    self.assertEqual(
                        owned_run_destination(root,stage,"Source_1",
                          selected=root/"03_ESM"/"RUNS"/"ULS"/"old"),(
                            root/"03_ESM"/"RUNS"/"ULS"/"old")
                            if stage=="ESM" else result)

    def test_custom_outside_kept_existing_right_stage_kept(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            root=base/"export";root.mkdir()
            other=base/"custom"
            self.assertEqual(owned_run_destination(root,"GRAVITY","Case",selected=other),other)
            stage=root/"02_GRAVITY"/"RUNS"/"Existing"
            self.assertEqual(owned_run_destination(root,"GRAVITY","Case",selected=stage),stage)
            wrong=root/"05_MRSM"/"RUNS"/"Wrong"
            self.assertEqual(owned_run_destination(root,"GRAVITY","Case",selected=wrong),
                             root/"02_GRAVITY"/"RUNS"/"Case")
            self.assertFalse((root/"02_GRAVITY").exists())

    def test_diagnostic_writers_have_canonical_run_owner(self):
        repo=Path(__file__).resolve().parents[1]
        p=repo/"components/model/readiness_dashboard_gui.py"
        source=p.read_text(encoding="utf-8-sig")
        self.assertNotIn('"OpenSees_Analysis_Results"',source)
        tree=ast.parse(source)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)
               and isinstance(n.func,ast.Name)
               and n.func.id=="owned_run_destination"]
        self.assertGreaterEqual(len(calls),4)
        for call in calls:
            self.assertTrue(any(isinstance(arg,ast.Constant)
                and arg.value=="SOFTWARE_DIAGNOSTICS" for arg in call.args))
        response=ast.parse((repo/"components/validation/response_checks.py")
                           .read_text(encoding="utf-8-sig"))
        self.assertTrue(any(isinstance(n,ast.Call)
            and isinstance(n.func,ast.Name) and n.func.id=="create_case_run"
            and any(isinstance(arg,ast.Constant)
                    and arg.value=="SOFTWARE_DIAGNOSTICS" for arg in n.args)
            for n in ast.walk(response)))

    def test_reject_traversal_and_links(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaises(ValueError):
                owned_run_destination(root,"GRAVITY","../other")
            with self.assertRaises(ValueError):
                owned_run_destination(root,"UNDEFINED","case")
            actual=root/"real";actual.mkdir()
            try:
                (root/"link").symlink_to(actual,target_is_directory=True)
            except (OSError,NotImplementedError):
                return
            with self.assertRaisesRegex(ValueError,"linked"):
                owned_run_destination(root,"GRAVITY","case",selected=root/"link"/"res")

    def test_run_gui_source_contract_contains_guard(self):
        repo=Path(__file__).resolve().parents[1]
        sources={
            "components/gravity/gui_and_reports.py":"GRAVITY",
            "components/linear_time_history/runner_and_gui.py":"LTHA",
            "components/nonlinear_time_history/runner_and_gui.py":"NLTHA",
        }
        for name,stage in sources.items():
            tree=ast.parse((repo/name).read_text(encoding="utf-8-sig"))
            calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)
                   and isinstance(n.func,ast.Name)
                   and n.func.id=="owned_run_destination"]
            self.assertTrue(calls,name+" must guard user-selected in-project paths")
            self.assertTrue(any(
                isinstance(arg,ast.Constant) and arg.value==stage
                for c in calls for arg in c.args),name+" wrong stage")


if __name__=="__main__":
    unittest.main()
