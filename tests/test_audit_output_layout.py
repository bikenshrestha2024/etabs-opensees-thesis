"""Tests for tools/audit_output_layout.py. [REF docs/OUTPUT_FOLDER_STANDARD.md]"""
import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT))
import audit_output_layout as aol  # noqa: E402
from components.inputs.output_contract import RUN_SUBFOLDERS, create_case_run  # noqa: E402


def snapshot(path):
    return sorted((str(p.relative_to(path)), p.is_symlink(),
                   p.stat().st_mtime_ns if not p.is_symlink() else 0)
                  for p in Path(path).rglob('*'))


class AuditOutputLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        export = Path(self.tmp.name) / 'export'
        export.mkdir()
        self.run = create_case_run(export, 'NLTHA', 'CASE1')

    def test_conforming_run_ok(self):
        r = aol.audit_run_layout(self.run)
        self.assertEqual((r['missing'], r['unexpected'], r['symlinks']), ([], [], []))
        self.assertEqual(r['manifest_issues'], [])
        self.assertTrue(r['ok'])
        self.assertEqual(r['status'], 'LAYOUT_ONLY_NOT_ENGINEERING_ACCEPTANCE')

    def test_missing_subfolder_reported(self):
        (self.run / '03_EXCEL').rmdir()
        r = aol.audit_run_layout(self.run)
        self.assertEqual(r['missing'], ['03_EXCEL'])
        self.assertFalse(r['ok'])
        self.assertIn('MISSING_03_EXCEL', r['manifest_issues'])

    def test_unexpected_entry_reported(self):
        (self.run / 'stray.txt').write_text('x')
        (self.run / 'extra_dir').mkdir()
        r = aol.audit_run_layout(self.run)
        self.assertEqual(r['unexpected'], ['extra_dir', 'stray.txt'])
        self.assertFalse(r['ok'])

    def test_symlink_reported(self):
        target = Path(self.tmp.name) / 'elsewhere'
        target.mkdir()
        try:
            os.symlink(target, self.run / 'link', target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('platform cannot create symlinks')
        r = aol.audit_run_layout(self.run)
        self.assertEqual(r['symlinks'], ['link'])
        self.assertFalse(r['ok'])

    def test_missing_run_dir_not_ok(self):
        r = aol.audit_run_layout(Path(self.tmp.name) / 'nope')
        self.assertFalse(r['ok'])
        self.assertEqual(r['missing'], list(RUN_SUBFOLDERS))

    def test_audit_is_read_only(self):
        (self.run / 'stray.txt').write_text('x')
        before = snapshot(self.run)
        aol.audit_run_layout(self.run)
        self.assertEqual(before, snapshot(self.run))

    def test_cli_exit_codes(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(aol.main([str(self.run), '--json']), 0)
        self.assertIn('"ok": true', out.getvalue())
        (self.run / 'stray.txt').write_text('x')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(aol.main([str(self.run)]), 1)


if __name__ == '__main__':
    unittest.main()
