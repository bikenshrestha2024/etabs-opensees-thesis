"""Non-native integration tests for V135 derived outputs and legacy inputs.

[REF docs/source/components/validation/design_checks.py.md]
"""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.validation.design_checks import (
    design_check_locations, discover_design_drift, run,
)


class DesignChecksCanonicalTests(unittest.TestCase):
    def test_new_and_legacy_drift_are_discovered_once(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            drift=base/"03_ESM"/"RUNS"/"ULS"/"X"
            drift.mkdir(parents=True)
            filename=drift/"Drift_Check_ULS_X.csv"
            with filename.open("w",newline="",encoding="utf-8") as stream:
                w=csv.DictWriter(stream,fieldnames=[
                    "limit_state","design_drift_ratio","story_number","axis"
                ])
                w.writeheader()
                w.writerow(dict(limit_state="ULS",design_drift_ratio="0.005",
                                story_number=1,axis="X"))
            review=base/"03_ESM"/"REVIEW_SNAPSHOTS"/"copy"
            review.mkdir(parents=True)
            (review/filename.name).write_bytes(filename.read_bytes())
            rows,issues=discover_design_drift(base)
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]["status"],"PASS")
            self.assertEqual(rows[0]["limit_state"],"ULS")

    def test_legacy_criteria_read_without_overwriting_and_canonical_report(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            source=base/"OpenSees_Complete_Model_Data_V118.json"
            source.write_text(json.dumps({"frames":[],"shells":[]}),encoding="utf-8")
            modelhash=hashlib.sha256(source.read_bytes()).hexdigest()
            new,old=design_check_locations(base)
            old.mkdir(parents=True)
            legacy=old/"Section_Criteria_V135.csv"
            with legacy.open("w",newline="",encoding="utf-8") as stream:
                writer=csv.DictWriter(stream,fieldnames=[
                    "limit_state","case","member","check","demand","limit",
                    "unit","concurrent_action_id","model_sha256","reviewed",
                    "source","clause","result_file"])
                writer.writeheader()
                writer.writerow(dict(limit_state="ULS",case="TEST",member="FRAME:1",
                    check="shear",demand="10",limit="20",unit="kN",
                    concurrent_action_id="source:1",model_sha256=modelhash,
                    reviewed="true",source="reviewed synthetic test",clause="TEST",
                    result_file=str(source)))
            legacy_sha=hashlib.sha256(legacy.read_bytes()).hexdigest()
            with patch("components.validation.settings_audit.audit",
                       return_value={"rows":[]}):
                report,out=run(base)
            self.assertEqual(out,new)
            self.assertEqual(report["tables"]["Section checks"][0]["status"],"PASS")
            self.assertEqual(report["overall"],"INCOMPLETE")
            self.assertEqual(report["input_criteria_sources"]["Section_Criteria_V135.csv"],
                             str(legacy.resolve()))
            self.assertEqual(hashlib.sha256(legacy.read_bytes()).hexdigest(),legacy_sha)
            self.assertTrue((new/"Design_Check_Report_V135.xlsx").exists())
            self.assertFalse((old/"Design_Check_Report_V135.xlsx").exists())
            new_criteria=new/"Section_Criteria_V135.csv"
            with new_criteria.open("a",encoding="utf-8",newline="") as stream:
                stream.write("SLS,EDITED,FRAME:2,shear,11,20,kN,source:2,"+
                             modelhash+",true,reviewed synthetic test,TEST,"+
                             str(source)+"\n")
            with patch("components.validation.settings_audit.audit",
                       return_value={"rows":[]}):
                report2,out2=run(base)
            self.assertEqual(out2,new)
            self.assertEqual(report2["input_criteria_sources"]["Section_Criteria_V135.csv"],
                             str(new_criteria.resolve()))
            self.assertEqual(hashlib.sha256(legacy.read_bytes()).hexdigest(),legacy_sha)


if __name__=="__main__":
    unittest.main()
