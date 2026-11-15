"""Non-native regression tests for nondestructive Windows output auditing."""
import tempfile
import unittest
import json
from pathlib import Path

from tools.audit_output_storage import scan_output, write_report


class OutputStorageAuditTests(unittest.TestCase):
    def test_exact_bytes_only_and_never_change_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            root.mkdir()
            (root / "02_GRAVITY").mkdir()
            (root / "OpenSees_Analysis_Results").mkdir()
            a = root / "02_GRAVITY" / "same.txt"
            b = root / "OpenSees_Analysis_Results" / "duplicate.txt"
            c = root / "02_GRAVITY" / "different.txt"
            a.write_bytes(b"same source evidence")
            b.write_bytes(b"same source evidence")
            c.write_bytes(b"another solver case")
            before = {p: p.read_bytes() for p in (a, b, c)}
            audit = scan_output(root)
            self.assertEqual(audit["total_files"], 3)
            self.assertEqual(audit["total_bytes"],
                             sum(len(x) for x in before.values()))
            self.assertEqual(len(audit["exact_duplicate_groups"]), 1)
            group = audit["exact_duplicate_groups"][0]
            self.assertEqual(group["repeat_count"], 2)
            self.assertEqual(group["redundant_bytes"], len(before[a]))
            self.assertTrue(group["review_only"])
            dest = Path(td) / "disk_report"
            write_report(audit, dest)
            self.assertTrue((dest / "REPORT" / "READ_FIRST.md").is_file())
            self.assertTrue((dest / "JSON" / "DISK_AUDIT.json").is_file())
            self.assertTrue((dest / "CSV" / "EXACT_DUPLICATES.csv").is_file())
            with self.assertRaises(FileExistsError):
                write_report(audit, dest)
            self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_cli_default_uses_canonical_diagnostics_per_run(self):
        from tools.audit_output_storage import main
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"case"
            root.mkdir()
            (root/"Gravity_Result.json").write_text("{}")
            self.assertEqual(main(["--root",str(root),"--no-hash"]),0)
            runs=root/"09_SOFTWARE_DIAGNOSTICS"/"DISK_AUDITS"/"RUNS"
            results=list(runs.glob("*/JSON/DISK_AUDIT.json"))
            self.assertEqual(len(results),1)
            self.assertEqual(len(list(runs.glob("*/CSV/EXACT_DUPLICATES.csv"))),1)
            self.assertEqual(len(list(runs.glob("*/REPORT/READ_FIRST.md"))),1)
            report=json.loads(results[0].read_text())
            self.assertEqual(report["total_files"],1)
            self.assertEqual(report["status"],"DISK_FOOTPRINT_ONLY_NOT_ENGINEERING_EQUIVALENCE")

    def test_linked_source_and_output_roots_are_refused_before_resolution(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            original=base/"original"
            original.mkdir()
            (original/"private_result.json").write_text('{"private":true}')
            redirected=base/"linked_root"
            try:
                redirected.symlink_to(original,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create a directory symlink")
            with self.assertRaisesRegex(ValueError,"linked disk-audit"):
                scan_output(redirected)
            with self.assertRaisesRegex(ValueError,"linked disk-audit"):
                write_report({"status":"synthetic"},redirected/"new_audit")
            self.assertEqual([p.name for p in original.iterdir()],
                             ["private_result.json"])
            self.assertFalse((original/"new_audit").exists())

    def test_linked_parent_in_report_path_cannot_redirect_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            outside=base/"outside"
            outside.mkdir()
            alias=base/"alias"
            try:
                alias.symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create a directory symlink")
            with self.assertRaisesRegex(ValueError,"linked disk-audit"):
                write_report({},alias/"08_AUDIT")
            self.assertEqual(list(outside.iterdir()),[])

    def test_no_hash_does_not_infer_duplicate_from_equal_size(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_bytes(b"aaaa")
            (root / "b.txt").write_bytes(b"bbbb")
            audit = scan_output(root, hash_duplicates=False)
            self.assertEqual(audit["exact_duplicate_groups"], [])
            self.assertEqual(audit["total_bytes"], 8)
            self.assertFalse(audit["hash_duplicates"])


if __name__ == "__main__":
    unittest.main()
