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
    def test_static_run_stage_call_inventory_covers_all_modules_and_dynamic_stages(self):
        from tools.audit_output_stage_ownership import audit
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            snippets={
                "components/equivalent_static/output.py": """
create_case_run(root, 'ESM', 'same')
create_case_run(root, 'GRAVITY', 'other')
create_case_run(root, stage_variable, 'dynamic')
""",
                "components/gravity/beam.py": """
create_case_run(root, 'ETABS_EXPORT', 'BEAM_FORCES')
""",
                "components/modal/modal.py": """
create_case_run(root, 'MODAL', 'same')
""",
                "components/inputs/autofill.py": """
analysis_output_folder(root, 'ULS')
""",
                "components/linear_time_history/runner.py": """
owned_run_destination(root, 'LTHA', 'correct')
""",
                "components/ui/controller.py": """
create_case_run(root, 'MRSM', 'viewer')
""",
            }
            for name,content in snippets.items():
                path=root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content,encoding="utf-8")
            report=audit(root)
            self.assertIn("declared_run_stage_calls",report)
            self.assertIn("cross_owner_run_stage_review",report)
            self.assertIn("dynamic_run_stage_review",report)
            calls=report["declared_run_stage_calls"]
            self.assertEqual(len(calls),8)
            by_path={}
            for item in calls:
                by_path.setdefault(item["path"],[]).append(item)
                self.assertGreaterEqual(item["line"],1)
                self.assertIn(item["api"],(
                    "create_case_run","owned_run_destination",
                    "analysis_output_folder"))
            esm=by_path["components/equivalent_static/output.py"]
            self.assertEqual([i["status"] for i in esm],
                             ["OWNER_MATCHED","CROSS_OWNER_REVIEW","DYNAMIC_STAGE_REVIEW"])
            self.assertEqual([i["stage"] for i in esm],
                             ["ESM","GRAVITY",None])
            self.assertEqual(esm[1]["source_owner"],"ESM")
            cross=report["cross_owner_run_stage_review"]
            self.assertEqual({(i["path"],i["stage"]) for i in cross},{
                ("components/equivalent_static/output.py","GRAVITY"),
                ("components/gravity/beam.py","ETABS_EXPORT"),
            })
            self.assertEqual(len(report["dynamic_run_stage_review"]),1)
            self.assertEqual(by_path["components/inputs/autofill.py"][0]["status"],
                             "LEGACY_DEFAULT_REVIEW")
            self.assertEqual(by_path["components/ui/controller.py"][0]["status"],
                             "SHARED_OWNER_REVIEW")
            self.assertEqual(by_path["components/modal/modal.py"][0]["status"],
                             "OWNER_MATCHED")
            self.assertEqual(by_path["components/linear_time_history/runner.py"][0]["status"],
                             "OWNER_MATCHED")
            self.assertNotIn("CROSS_OWNER_REVIEW",
                 {v["reason"] for v in report["contract_violations"]})
            self.assertFalse((root/"audit").exists())

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

    def test_model_readiness_discovery_reads_canonical_modal_case(self):
        from components.model.readiness_gui import available_evidence
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            builder=root/"OpenSees_Complete_Nonlinear_Model.py"
            builder.write_text("# synthetic builder",encoding="utf-8")
            result=root/"04_MODAL"/"RUNS"/"ULS"/"case"/"run"/"02_RESULTS"/"NBC105_Modal_V111.json"
            result.parent.mkdir(parents=True)
            result.write_text('{"status":"NOT_ENGINEERING_ACCEPTANCE"}',encoding="utf-8")
            evidence=available_evidence(builder)
            key="modal_periods_modes_and_mass_participation_reviewed"
            self.assertIn(key,evidence)
            self.assertIn(str(result),evidence[key])

    def test_deformation_viewer_discovers_esm_mrsm_nltha_and_legacy(self):
        from components.ui.response_viewer import find_deformation_cases
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            paths=[
                root/"OpenSees_Analysis_Results"/"ULS_Floor_3_Model"/"Deformation_Old_V132.json",
                root/"03_ESM"/"RUNS"/"ULS"/"case"/"Deformation_ESM_V132.json",
                root/"05_MRSM"/"RUNS"/"ULS"/"case"/"run"/"02_RESULTS"/"Deformation_MRSM_V132.json",
                root/"07_NONLINEAR_TIME_HISTORY"/"RUNS"/"trial"/"Deformation_NLTHA_V132.json",
            ]
            for p in paths:
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('{"unverified":true}',encoding="utf-8")
            discovered=find_deformation_cases(root)
            self.assertEqual(set(discovered),set(paths))
            legacy=find_deformation_cases(root/"OpenSees_Analysis_Results")
            self.assertEqual(set(legacy),set(paths))

    def test_readiness_discovers_new_stage_outputs_and_historical_sources(self):
        from components.model.readiness_dashboard import _candidates
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            stage=(root/"09_SOFTWARE_DIAGNOSTICS"/"RUNS"/"READINESS_AUDIT")
            stage.mkdir(parents=True)
            current=stage/"Nonlinear_Readiness_Audit.json"
            current.write_text('{"status":"evidence"}',encoding="utf-8")
            historic=root/"OpenSees_Analysis_Results"
            historic.mkdir()
            old=historic/"Nonlinear_Readiness_Audit.json"
            old.write_text('{"status":"legacy"}',encoding="utf-8")
            results=_candidates(root,"Nonlinear_Readiness_Audit.json")
            self.assertIn(current,results)
            self.assertIn(old,results)
            self.assertEqual(len(results),2)

    def test_exploratory_and_material_paths_do_not_regress(self):
        repo=Path(__file__).resolve().parents[1]
        targets={
            "components/ui/building_exploratory_gui.py":"NLTHA",
            "components/model/readiness_gui.py":"SOFTWARE_DIAGNOSTICS",
            "components/validation/irregularity_review.py":"SOFTWARE_DIAGNOSTICS",
        }
        for filename,stage in targets.items():
            text=(repo/filename).read_text(encoding="utf-8-sig")
            tree=ast.parse(text)
            calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)
                   and isinstance(n.func,ast.Name)
                   and n.func.id=="owned_run_destination"]
            self.assertTrue(any(any(isinstance(a,ast.Constant)
                and a.value==stage for a in c.args) for c in calls), filename)

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
            "components/gravity/output_ownership.py":"GRAVITY",
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
        gui=ast.parse((repo/'components/gravity/gui_and_reports.py').read_text(encoding='utf-8-sig'))
        inputs=next(node for node in ast.walk(gui) if isinstance(node, ast.FunctionDef) and node.name=='_inputs')
        self.assertTrue(any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
                            and node.func.id=='model_workspace' for node in ast.walk(inputs)))


if __name__=="__main__":
    unittest.main()
