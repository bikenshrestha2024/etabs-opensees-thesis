"""Fail-closed V135 drift: source identity + completed solver run are required."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.validation.design_checks import (
    run,saved_drift_solver_status,
)


class V135DriftSourceAndCompletionTests(unittest.TestCase):
    def test_current_sha_with_no_run_status_is_not_a_drift_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text('{"frames":[],"shells":[]}',encoding="utf-8")
            digest=hashlib.sha256(model.read_bytes()).hexdigest()
            results=root/"05_MRSM"/"RUNS"/"ULS"/"case"/"run1"/"02_RESULTS"
            results.mkdir(parents=True)
            response=results/"MRSM_Results_V132.json"
            def save_response(sha):
                response.write_text(json.dumps({"X_E0":{
                    "model_sha256":sha,"limit_state":"ULS","axis":"X",
                    "stories":[{"story_number":1,"design_drift_ratio":0.005}]
                }}))
            def assess():
                with patch("components.validation.settings_audit.audit",
                           return_value={"rows":[]}):
                    return run(root)[0]
            save_response(digest)
            report=assess()
            self.assertEqual(report["drift_source_mismatch_excluded_count"],0)
            self.assertEqual(report["drift_source_unverified_row_count"],0)
            self.assertEqual(report["drift_run_completion_unverified_row_count"],1)
            row=report["tables"]["Seismic drift"][0]
            self.assertEqual(row["raw_limit_status"],"PASS")
            self.assertEqual(row["status"],"NOT EVALUATED")
            self.assertEqual(row["run_completion_status"],"NO_RUN_COMPLETION_MANIFEST")
            manifest=results.parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            manifest.parent.mkdir()
            # Previously this incomplete, schema-less manifest was accepted
            # as proof that the native MRSM run completed. It is not.
            manifest.write_text(json.dumps({
                "solver_status":"COMPLETED_SOLVER_ONLY",
                "model_sha256":digest
            }))
            report=assess()
            self.assertEqual(report["drift_run_completion_unverified_row_count"],1)
            self.assertEqual(report["tables"]["Seismic drift"][0]["status"],
                             "NOT EVALUATED")
            self.assertEqual(report["tables"]["Seismic drift"][0]["run_completion_status"],
                             "INVALID_RUN_MANIFEST")
            from components.inputs.output_contract import RUN_SUBFOLDERS,SCHEMA
            for folder in RUN_SUBFOLDERS:
                (results.parent/folder).mkdir(exist_ok=True)
            valid_manifest={
                "schema":SCHEMA,"stage":"05_MRSM","state":"ULS",
                "case_id":"case","run_id":"run1","units":"kN-m-s",
                "solver_status":"COMPLETED_SOLVER_ONLY",
                "structural_acceptance":"NOT_VERIFIED",
                "model_sha256":digest,"source_edb_sha256":None,
            }
            manifest.write_text(json.dumps(valid_manifest))
            report=assess()
            self.assertEqual(report["drift_run_completion_unverified_row_count"],0)
            self.assertEqual(report["tables"]["Seismic drift"][0]["status"],"PASS")
            incomplete=dict(valid_manifest,solver_status="INCOMPLETE")
            manifest.write_text(json.dumps(incomplete))
            report=assess()
            self.assertEqual(report["tables"]["Seismic drift"][0]["status"],
                             "NOT EVALUATED")
            save_response("b"*64)
            manifest.write_text(json.dumps(valid_manifest))
            report=assess()
            self.assertEqual(report["tables"]["Seismic drift"],[])
            self.assertGreater(report["drift_source_mismatch_excluded_count"],0)
            self.assertTrue(any(r.get("status") in (
                "SOURCE_MANIFEST_RESULT_SHA_CONFLICT_EXCLUDED",
                "SOURCE_MODEL_SHA_MISMATCH_EXCLUDED")
                for r in report["tables"]["Open items"]))

    def test_finite_source_values_cannot_publish_overflowed_utilization(self):
        from components.validation.design_checks import evaluate_checks,combine_actions,COMPONENTS
        with tempfile.TemporaryDirectory() as td:
            evidence=Path(td)/"source.json"
            evidence.write_text("{}")
            checks=evaluate_checks([{
                "model_sha256":"a"*64,"reviewed":"true","source":"unit-test",
                "clause":"reviewed criterion","result_file":str(evidence),
                "limit_state":"ULS","unit":"kN","demand":1e308,
                "limit":1e-308
            }],"a"*64,"deflection")
            self.assertEqual(checks[0]["status"],"NOT EVALUATED")
            self.assertIsNone(checks[0]["utilization"])
            self.assertIn("overflow",checks[0]["reason"])
            case={"case":"ULS_EXTREME","limit_state":"ULS",
                  "factors":{"A":2.0}}
            row={"model_sha256":"a"*64,"response_kind":
                 "signed_first_order_linear_increment","limit_state":"ULS",
                 "member":"C1","station":"end","axes":"local",
                 "basis_case":"A",**{field:1e308 for field in COMPONENTS}}
            combined,issues=combine_actions([row],[case],"a"*64)
            self.assertEqual(combined,[])
            self.assertEqual(len(issues),1)
            self.assertEqual(issues[0]["status"],"NOT EVALUATED")
            self.assertIn("Nonfinite combined action",issues[0]["reason"])

    def test_v135_output_index_marks_no_current_rows_explicitly(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text(
                '{"frames":[],"shells":[]}',encoding="utf-8")
            diagnostics=root/"09_SOFTWARE_DIAGNOSTICS"/"DESIGN_CHECKS_V135"
            diagnostics.mkdir(parents=True)
            prior=diagnostics/"Seismic_drift.csv"
            prior.write_text("historical csv must not appear current\n")
            with patch("components.validation.settings_audit.audit",
                       return_value={"rows":[]}):
                report,out=run(root)
            idx=json.loads((out/"Design_Check_Output_Index_V135.json").read_text())
            self.assertEqual(idx["schema"],"V135_DERIVED_REPORT_INDEX_V1")
            self.assertEqual(idx["tables"]["Seismic drift"]["current_row_count"],0)
            self.assertEqual(idx["tables"]["Seismic drift"]["status"],
                             "NO_CURRENT_ROWS_PRIOR_CSV_NOT_REPLACED")
            self.assertEqual(prior.read_text(),"historical csv must not appear current\n")
            self.assertTrue((out/"Design_Check_V135.log").is_file())
            self.assertEqual(list(out.glob(".design_check_log_*.partial")),[])
            self.assertEqual(list(out.glob(".design_checks_*.xlsx")),[])

    def test_v135_refuses_linked_templates_or_model_source(self):
        from components.validation.design_checks import templates
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outside=root/"outside"
            outside.mkdir()
            output=root/"09_SOFTWARE_DIAGNOSTICS"
            try:
                output.symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Symbolic links unsupported")
            with self.assertRaisesRegex(ValueError,"linked derived-output"):
                templates(output/"DESIGN_CHECKS_V135")
            self.assertEqual(list(outside.iterdir()),[])
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            linked=root/"actual_model.json"
            linked.write_text('{"frames":[],"shells":[]}')
            model.symlink_to(linked)
            with self.assertRaisesRegex(ValueError,"linked authoritative"):
                run(root)
            self.assertEqual(list(outside.iterdir()),[])

    def test_v135_workbook_publishes_without_temp_residue(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text('{"frames":[],"shells":[]}',encoding="utf-8")
            with patch("components.validation.settings_audit.audit",
                       return_value={"rows":[]}):
                report,out=run(root)
            self.assertEqual(report["overall"],"INCOMPLETE")
            self.assertTrue((out/"Design_Check_Report_V135.xlsx").is_file())
            self.assertEqual(list(out.glob(".design_checks_*.xlsx")),[])
            self.assertEqual(list(out.glob(".writing_*.partial")),[])

    def test_derived_design_csv_publication_is_atomic(self):
        from components.validation.design_checks import write_rows
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            output=root/"Design_Checks_V135"/"Seismic_drift.csv"
            output.parent.mkdir()
            output.write_text("existing evidence stays\\n")
            with self.assertRaisesRegex(ValueError,"Nonfinite numeric CSV"):
                write_rows(output,[{"case":"X_E0","drift":0.003},
                                   {"case":"Y_E0","drift":float("nan")}])
            self.assertEqual(output.read_text(),"existing evidence stays\\n")
            self.assertEqual(list(output.parent.glob(".writing_*.partial")),[])
            write_rows(output,[{"case":"X_E0","drift":0.003}])
            self.assertIn("X_E0,0.003",output.read_text())
            # Empty rows retain legacy no-write behavior; they do not fabricate evidence.
            before=output.read_bytes()
            write_rows(output,[])
            self.assertEqual(before,output.read_bytes())

    def test_mixed_valid_invalid_rows_do_not_leak_drift_passes(self):
        from components.validation.design_checks import scan_drift
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            csvpath=root/"Drift_Check_ULS_X.csv"
            csvpath.write_text(
                "limit_state,design_drift_ratio,story_number,axis\n"
                "ULS,0.003,1,X\nULS,NaN,2,X\n",encoding="utf-8")
            mrsm=root/"MRSM_Results_V132.json"
            mrsm.write_text(json.dumps({
                "X_E0":{"limit_state":"ULS","axis":"X",
                        "stories":[{"story_number":1,"design_drift_ratio":0.003}]},
                "Y_E0":{"limit_state":"ULS","axis":"Y",
                        "stories":[{"story_number":2,"design_drift_ratio":"Infinity"}]}
            }),encoding="utf-8")
            rows,issues=scan_drift(root)
            self.assertEqual(rows,[])
            self.assertEqual(len(issues),2)
            self.assertTrue(all(row["status"]=="NOT EVALUATED" for row in issues))
            csvpath.write_text(
                "limit_state,design_drift_ratio,story_number,axis\n"
                "ULS,0.003,1,X\n",encoding="utf-8")
            mrsm.unlink()
            rows,issues=scan_drift(root)
            self.assertEqual(len(rows),1)
            self.assertEqual(issues,[])

    def test_manifest_misfiled_identity_blocks_completed_drift_status(self):
        from components.inputs.output_contract import create_case_run,record_case_status
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            folder=create_case_run(root,"MRSM","X_E0",state="ULS",
                                   model_sha256="a"*64)
            result=folder/"02_RESULTS"/"MRSM_Results_V132.json"
            result.write_text('{"X_E0":{}}')
            record_case_status(folder,"COMPLETED_SOLVER_ONLY")
            self.assertEqual(saved_drift_solver_status(result),"COMPLETED_SOLVER_ONLY")
            manifest=folder/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            data=json.loads(manifest.read_text())
            for field,bad in (("case_id","another_case"),
                              ("stage","03_ESM"),("run_id","another_run")):
                corrupt=dict(data)
                corrupt[field]=bad
                manifest.write_text(json.dumps(corrupt))
                with self.subTest(field=field):
                    self.assertEqual(saved_drift_solver_status(result),
                                     "INVALID_RUN_MANIFEST")
            self.assertEqual(json.loads(manifest.read_text())["run_id"],"another_run")

    def test_legacy_drift_csv_without_hash_cannot_be_marked_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text(
                '{"frames":[],"shells":[]}',encoding="utf-8")
            legacy=root/"OpenSees_Analysis_Results"
            legacy.mkdir()
            csvfile=legacy/"Drift_Check_ULS_X.csv"
            csvfile.write_text(
                "limit_state,design_drift_ratio,story_number,axis\n"
                "ULS,0.003,1,X\n",encoding="utf-8")
            self.assertEqual(saved_drift_solver_status(csvfile),
                             "NO_RUN_COMPLETION_MANIFEST")
            with patch("components.validation.settings_audit.audit",
                       return_value={"rows":[]}):
                report,_=run(root)
            row=report["tables"]["Seismic drift"][0]
            self.assertEqual(row["source_identity_status"],"NOT_VERIFIED")
            self.assertEqual(row["status"],"NOT EVALUATED")
            self.assertEqual(row["raw_limit_status"],"PASS")


if __name__=="__main__":
    unittest.main()
