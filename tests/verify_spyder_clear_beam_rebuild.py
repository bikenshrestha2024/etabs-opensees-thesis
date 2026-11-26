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

    def test_changed_edb_blocks_rebuild_before_creating_destination(self):
        edb=self.root/"Selected.EDB"
        edb.write_bytes(b"edited after conversion")
        (self.source/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":str(edb)}),encoding="utf-8")
        context=self.source/"00_SOURCE_MANIFEST"
        context.mkdir()
        (context/"PROJECT_CONTEXT.json").write_text(json.dumps(
            {"source_edb":str(edb),"source_edb_sha256":"0"*64}),encoding="utf-8")
        with patch("openpyxl.load_workbook",return_value=FakeBook(build.REQUIRED_SHEETS)):
            with self.assertRaisesRegex(ValueError,"changed since export"):
                build.rebuild_verified_clear_beam(self.source,self.book,self.destination)
        self.assertFalse(self.destination.exists())

    def test_rebuild_with_project_context_reaches_assembly(self):
        """Exercise actual rebuild orchestration through the reported failure point."""
        import sys
        from types import ModuleType
        from unittest.mock import Mock
        from components.inputs.project_output_layout import (
            create_project_layout, require_import_root)
        edb=self.root/"ULTIMATE.EDB"
        edb.write_bytes(b"synthetic source")
        (self.source/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":str(edb)}),encoding="utf-8")
        ctx=create_project_layout(edb,self.source)
        manifest=self.source/"00_SOURCE_MANIFEST"/"PROJECT_CONTEXT.json"
        before=manifest.read_bytes()
        original_config=self.config.read_bytes()
        assembly=ModuleType("components.model.assembly")
        assembly.prepare_complete_export=Mock(side_effect=RuntimeError("assembly checkpoint"))
        for target in (build.canonical_clear_beam_destination(self.source,stamp="RUN_001"),
                       self.destination):
            with self.subTest(target=target):
                with patch("openpyxl.load_workbook",return_value=FakeBook(build.REQUIRED_SHEETS)):
                    with patch.dict(sys.modules,{"components.model.assembly":assembly}):
                        with self.assertRaisesRegex(RuntimeError,"assembly checkpoint"):
                            build.rebuild_verified_clear_beam(self.source,self.book,target)
                assembly.prepare_complete_export.assert_called_with(target,runtime_dir=build.ROOT)
                rebuilt=json.loads((target/"00_SOURCE_MANIFEST"/"PROJECT_CONTEXT.json").read_text())
                self.assertEqual(rebuilt["source_edb_sha256"],ctx["source_edb_sha256"])
                self.assertEqual(rebuilt["output_root"],str(target))
                self.assertEqual(rebuilt["original_export_root"],str(self.source))
                self.assertEqual(rebuilt["layout_kind"],"CLEAR_BEAM_REBUILD")
                status=json.loads((target/"CLEAR_BEAM_REBUILD_STATUS.json").read_text())
                self.assertEqual(status["status"],"BLOCKED")
                self.assertIn("assembly checkpoint",status["error"])
                self.assertFalse((target/"02_GRAVITY").exists())
                with self.assertRaises(ValueError):
                    require_import_root(target)
                with self.assertRaises(FileExistsError):
                    build.rebuild_verified_clear_beam(self.source,self.book,target)
                self.assertEqual(manifest.read_bytes(),before)
                self.assertEqual(self.config.read_bytes(),original_config)
                self.assertEqual(edb.read_bytes(),b"synthetic source")

    def test_rebuild_rejects_other_project_stage_and_linked_destination(self):
        other=self.root/"other"/"04_MODAL"/"RUNS"/"case"
        with self.assertRaisesRegex(ValueError,"stage/run"):
            build._verify_before_creating_output(self.source,self.book,other)
        self.assertFalse(other.exists())
        outside=self.root/"outside"
        outside.mkdir()
        link=self.root/"link"
        try:
            link.symlink_to(outside,target_is_directory=True)
        except (OSError,NotImplementedError):
            self.skipTest("Directory symlinks unavailable")
        with self.assertRaisesRegex(ValueError,"linked"):
            build._verify_before_creating_output(self.source,self.book,link/"new")
        self.assertEqual(list(outside.iterdir()),[])

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
