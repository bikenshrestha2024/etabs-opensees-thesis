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


if __name__=="__main__":
    unittest.main()
