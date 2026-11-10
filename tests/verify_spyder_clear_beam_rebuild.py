"""Regression tests for Spyder arguments, file selection and fail-closed checks.

No ETABS, no OpenSeesPy analysis and no GUI actually shown.
"""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import REBUILD_VERIFIED_CLEAR_BEAM_MODEL as build


class FakeBook:
    def __init__(self,names):
        self.sheetnames=list(names)
        self.closed=False
    def close(self):
        self.closed=True


class RebuildEntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"source"
        self.source.mkdir()
        self.book=self.root/"Original_ETABS_Full_Assignments.xlsx"
        self.book.write_bytes(b"not read as actual Excel because mocked")
        self.destination=self.root/"new-source"
        self.config=self.source/"OpenSees_Complete_Model_Config_V118.json"
        self.config.write_text(
            json.dumps({"etabs_beam_weight_policy":"GROSS_SECTION_LENGTH",
                        "joint_volume_weight_policy":"AUDIT_ONLY"}),
            encoding="utf-8")
        for name in build.SOURCE_REQUIRED_FILES:
            file=self.source/name
            if not file.exists():
                file.write_text("{}",encoding="utf-8")

    def test_no_argument_invokes_dialog_not_argparse_error(self):
        selected=(str(self.source),str(self.book),str(self.destination))
        with patch.object(build,"_choose_in_spyder",return_value=selected) as picker:
            self.assertEqual(build._resolve_inputs([]),selected)
            picker.assert_called_once_with()

    def test_complete_cli_has_no_gui(self):
        selected=(str(self.source),str(self.book),str(self.destination))
        with patch.object(build,"_choose_in_spyder",
                          side_effect=AssertionError("GUI must not run")):
            self.assertEqual(build._resolve_inputs([
                "--source-dir",selected[0],
                "--assignment-workbook",selected[1],
                "--dest-dir",selected[2]]),selected)

    def test_partial_cli_fails_closed(self):
        with patch.object(build,"_choose_in_spyder") as picker:
            with self.assertRaises(SystemExit) as caught:
                build._resolve_inputs(["--source-dir",str(self.source)])
            self.assertEqual(caught.exception.code,2)
            picker.assert_not_called()

    def test_cancel_does_not_create_files(self):
        with patch.object(build,"_resolve_inputs",return_value=None):
            self.assertIsNone(build.main([]))
        self.assertFalse(self.destination.exists())

    def test_missing_json_blocks_before_output(self):
        (self.source/"OpenSees_Element_Connectivity.json").unlink()
        with self.assertRaisesRegex(FileNotFoundError,
                                    "OpenSees_Element_Connectivity.json"):
            build._verify_before_creating_output(
                self.source,self.book,self.destination)
        self.assertFalse(self.destination.exists())

    def test_native_workbook_sheet_requirements(self):
        workbook=FakeBook(["Material List by Object Type"])
        with patch("openpyxl.load_workbook",return_value=workbook):
            with self.assertRaisesRegex(ValueError,"Missing sheets"):
                build._verify_before_creating_output(
                    self.source,self.book,self.destination)
        self.assertTrue(workbook.closed)
        self.assertFalse(self.destination.exists())

    def test_valid_preflight_is_read_only(self):
        workbook=FakeBook(build.REQUIRED_SHEETS)
        before=self.config.read_bytes()
        with patch("openpyxl.load_workbook",return_value=workbook):
            values=build._verify_before_creating_output(
                self.source,self.book,self.destination)
        self.assertEqual(values,(self.source.resolve(),self.book.resolve(),
                                 self.destination.resolve()))
        self.assertEqual(before,self.config.read_bytes())
        self.assertFalse(self.destination.exists())

    def test_no_nested_or_existing_output(self):
        for bad in (self.source/"nested",self.source):
            with self.assertRaises((ValueError,FileExistsError)):
                build._verify_before_creating_output(
                    self.source,self.book,bad)
        self.destination.mkdir()
        with self.assertRaises(FileExistsError):
            build._verify_before_creating_output(
                self.source,self.book,self.destination)


if __name__=="__main__":
    unittest.main()
