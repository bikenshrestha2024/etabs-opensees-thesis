"""V142 output location and response-source tests. No native solver required."""
import csv
import tempfile
import unittest
from pathlib import Path
from components.validation.case_review import collect, export


class CaseReviewCanonicalOutputTests(unittest.TestCase):
    def test_drift_visible_from_new_stage_and_report_is_not_legacy(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            saved=root/"03_ESM"/"RUNS"/"ULS"/"X_E0"
            saved.mkdir(parents=True)
            drift=saved/"Drift_Check_ULS_X_E0.csv"
            with drift.open("w",encoding="utf-8",newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=[
                    "limit_state","design_drift_ratio","story_number","axis"])
                writer.writeheader()
                writer.writerow({"limit_state":"ULS","design_drift_ratio":"0.01",
                                 "story_number":"1","axis":"X"})
            result=collect(root)
            self.assertEqual(len(result["drift"]),1)
            self.assertEqual(result["drift"][0]["status"],"PASS")
            self.assertEqual(result["deflection"],[])
            self.assertIn("NO_SAVED_LATERAL_DEFLECTION",
                          [x.get("status") for x in result["issues"]])
            exported,out=export(root)
            self.assertEqual(out,root/"09_SOFTWARE_DIAGNOSTICS"/"CASE_REVIEW_V142")
            self.assertTrue((out/"All_Case_Review_V142.xlsx").is_file())
            self.assertFalse((root/"OpenSees_Analysis_Results").exists())
            exported2,out2=export(saved)
            self.assertEqual(out2,out)
            self.assertEqual(len(exported2["drift"]),1)


    def test_corrupt_evidence_is_reported_and_not_plotted(self):
        import json
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"Gravity_Profile_ULS_V142.json").write_text(
                '["not-a-gravity-profile"]',encoding="utf-8")
            stage=root/"03_ESM"/"RUNS"/"ULS"/"X"/"case"
            stage.mkdir(parents=True)
            (stage/"Floor_Edge_Drift_ULS.csv").write_text(
                "limit_state,story_number,axis,floor_displacement_m\n"
                "ULS,25,X,0.012\nULS,24,X,NaN\n",encoding="utf-8")
            (stage/"Deformation_ULS.json").write_text(
                json.dumps({"limit_state":"ULS",
                            "nodes":{"1":[0,0,95]},
                            "displacements":{"1":["NaN",0]}}))
            result=collect(root)
            statuses={r.get("status") for r in result["issues"]}
            self.assertIn("INVALID_GRAVITY_PROFILE",statuses)
            self.assertIn("INVALID_FLOOR_EDGE_DRIFT",statuses)
            self.assertIn("INVALID_DEFORMATION_RESULT",statuses)
            self.assertEqual(result["preload_profiles"],[])
            self.assertEqual(result["deflection"],[])

    def test_export_rejects_linked_diagnostics_without_external_writes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            outside=Path(td)/"outside"
            root.mkdir()
            outside.mkdir()
            try:
                (root/"09_SOFTWARE_DIAGNOSTICS").symlink_to(
                    outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host has no directory symlink support")
            with self.assertRaisesRegex(ValueError,"linked case-review"):
                export(root)
            self.assertEqual(list(outside.iterdir()),[])

    def test_excel_report_is_replaced_without_partial_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            result,out=export(root)
            xlsx=out/"All_Case_Review_V142.xlsx"
            self.assertTrue(xlsx.is_file())
            self.assertEqual(list(out.glob(".case_review_*")),[])
            from openpyxl import load_workbook
            book=load_workbook(xlsx,read_only=True)
            self.assertIn("Read errors",book.sheetnames)
            book.close()
            export(root)
            self.assertEqual(list(out.glob(".case_review_*")),[])

if __name__=="__main__":
    unittest.main()
