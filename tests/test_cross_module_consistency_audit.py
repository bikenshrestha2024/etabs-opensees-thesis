"""Static source consistency coverage: no native solver is executed.

[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]
"""
import tempfile
import unittest
from pathlib import Path

from tools.audit_cross_module_consistency import scan_consistency,save,owner


class CrossModuleConsistencyTests(unittest.TestCase):
    def test_scans_all_domains_and_reports_shadowed_definitions_clones_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=root/"components"/"gravity"/"alpha.py"
            b=root/"components"/"validation"/"beta.py"
            a.parent.mkdir(parents=True)
            b.parent.mkdir(parents=True)
            body='''def same_algorithm(x, values):
    total = 0
    for item in values:
        if item < 0:
            total = total - item
        else:
            total = total + item
    if x > total:
        return x - total
    elif x == total:
        return 0
    return total - x
'''
            a.write_text(
                "from components.model import analysis_basis\n"+
                body+"\nSOURCE='NBC105_2025_95m_12m_MODEL_ALIGNED_V10_6.xlsx'\n",
                encoding="utf-8")
            b.write_text(body.replace("same_algorithm","other_algorithm"),
                         encoding="utf-8")
            c=root/"components"/"gravity"/"override.py"
            c.write_text('''class Duplicate:
    def calculate(self):
        return 1
    def calculate(self):
        return 2
''',encoding="utf-8")
            report=scan_consistency(root)
            self.assertEqual(report["active_sources_scanned"],3)
            self.assertEqual(len(report["shadowed_definitions"]),1)
            self.assertEqual(report["shadowed_definitions"][0]["symbol"],
                             "calculate")
            self.assertEqual(len(report["cross_file_exact_body_clone_candidates"]),1)
            self.assertEqual(report["versioned_workbook_literal_review"][0]["version"],
                             "V10_6")
            self.assertIn(
                {"from_owner":"GRAVITY","to_owner":"MODEL",
                 "source_files_with_import":1},
                report["module_owner_import_links"])
            self.assertFalse(report["historical_files_mutated"])
            out=root/"audit"
            save(report,out)
            self.assertTrue((out/"01_ALL_MODULE_CONSISTENCY.json").is_file())
            self.assertTrue((out/"03_DUPLICATE_FUNCTION_CANDIDATES.csv").is_file())

    def test_historic_github_snapshots_excluded_and_no_auto_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            old=root/"Saved_Project_V156"/"copy.py"
            old.parent.mkdir()
            old.write_text("def a():return 1\ndef a():return 2\n")
            fresh=root/"components"/"modal"/"current.py"
            fresh.parent.mkdir(parents=True)
            fresh.write_text("def current(): return 1\n",encoding="utf-8")
            report=scan_consistency(root)
            self.assertEqual(report["active_sources_scanned"],1)
            self.assertEqual(report["shadowed_definitions"],[])
            self.assertTrue(old.exists())

    def test_owner_catalog_includes_every_live_engineering_module(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        report=scan_consistency(root)
        present=set(report["owner_counts"])
        required={"SOURCE_INPUTS","MODEL","GRAVITY","ESM","MODAL","MRSM",
                  "LTHA","NLTHA","NBC105","SECTIONS","VALIDATION","GUI"}
        self.assertTrue(required <= present)
        self.assertEqual(report["parse_errors"],[])
        self.assertEqual(report["active_sources_scanned"],
                         sum(report["owner_counts"].values()))
        self.assertEqual(owner("components/nbc105/dispatch.py"),"NBC105")


if __name__=="__main__":
    unittest.main()
