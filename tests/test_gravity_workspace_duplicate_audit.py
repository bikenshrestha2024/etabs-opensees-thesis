"""Local source-grounded gravity file-digest inventory regressions."""
import tempfile
import unittest
from pathlib import Path
from tools.audit_gravity_workspace import inspect,save_report


class GravityWorkspaceAuditTests(unittest.TestCase):
    def test_detects_exact_byte_duplicates_without_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"02_GRAVITY").mkdir()
            old=root/"OpenSees_Analysis_Results"/"ULS_Floor_3_Model"
            old.mkdir(parents=True)
            current=root/"02_GRAVITY"/"RUNS"/"CASE"/"02_RESULTS"
            current.mkdir(parents=True)
            a=current/"Gravity_Result_V110.json"
            b=old/"Gravity_Result_V110.json"
            a.write_text('{"ok":true}',encoding="utf-8")
            b.write_bytes(a.read_bytes())
            unique=current/"Gravity_Unique_V110.json"
            unique.write_text("distinct",encoding="utf-8")
            report=inspect(root)
            self.assertEqual(report["file_count"],3)
            self.assertEqual(report["exact_duplicate_groups"],1)
            dup=report["duplicate_groups"][0]
            self.assertEqual(dup["copies"],2)
            self.assertEqual(dup["potential_redundant_bytes"],a.stat().st_size)
            self.assertFalse((root/"02_GRAVITY"/"06_REVIEW").exists())
            saved=save_report(report,root)
            self.assertTrue((saved/"EXACT_DUPLICATE_REVIEW.json").is_file())
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertTrue(a.is_file() and b.is_file() and unique.is_file())

    def test_inventories_case_structure_without_discarding_distinct_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);root.joinpath("02_GRAVITY").mkdir()
            p=root/"02_GRAVITY"/"RUNS"/"Model"/"02_RESULTS"
            for tag in ("32","76","97"):
                d=p/tag
                d.mkdir(parents=True)
                (d/"Gravity_Result_V110.json").write_text(
                    '{"support_case":"'+tag+'"}',encoding="utf-8")
            r=inspect(root)
            self.assertEqual(r["exact_duplicate_groups"],0)
            self.assertEqual(r["file_count"],3)
            with self.assertRaisesRegex(ValueError,"limit"):
                inspect(root,limit_files=2)


if __name__=="__main__":
    unittest.main()
