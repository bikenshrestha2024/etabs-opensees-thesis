"""Provenance and stage ownership for a model-aligned 12m X-wall rebuild."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.REBUILD_VERIFIED_CLEAR_BEAM_MODEL import (
    SOURCE_REQUIRED_FILES,REQUIRED_SHEETS,
    canonical_clear_beam_destination,_verify_before_creating_output)
from components.inputs.project_workbooks import (
    copy_project_workbooks,source_workbooks)
from components.inputs.aw_sources import resolve_aw


class _Book:
    sheetnames=REQUIRED_SHEETS
    def close(self): pass


class ClearBeamStageAndWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"original"
        self.root.mkdir()
        self.book=Path(self.temp.name)/"native_original.xlsx"
        self.book.write_bytes(b"mock workbook")
        for name in SOURCE_REQUIRED_FILES:
            (self.root/name).write_text("{}",encoding="utf-8")
        (self.root/"OpenSees_Complete_Model_Config_V118.json").write_text(
            '{"joint_volume_weight_policy":"AUDIT_ONLY"}',encoding="utf-8")

    def test_stage_owned_new_rebuild_is_approved_but_arbitrary_nested_rejected(self):
        target=canonical_clear_beam_destination(self.root,stamp="RUN_001")
        self.assertEqual(target,self.root/"02_MODEL"/"REBUILDS"/
                         "VERIFIED_CLEAR_BEAM"/"RUN_001")
        with patch("openpyxl.load_workbook",return_value=_Book()):
            a,b,c=_verify_before_creating_output(self.root,self.book,target)
            self.assertEqual(c,target)
            with self.assertRaisesRegex(ValueError,"ONLY"):
                _verify_before_creating_output(
                    self.root,self.book,self.root/"random"/"RUN_001")
        self.assertFalse(target.exists())
        self.assertFalse(target.parent.exists())

    def test_new_model_does_not_inherit_old_scaling_workbooks(self):
        export=Path(self.temp.name)/"new_export"
        export.mkdir()
        cfg=export/"OpenSees_Complete_Model_Config_V118.json"
        cfg.write_text(json.dumps({
            "require_model_aligned_workbooks":True,
            "required_x_wall_policy":"TWO_12M_CONTINUOUS_X_WALLS_WITH_SOURCE_OPENINGS"
        }),encoding="utf-8")
        runtime=Path(self.temp.name)/"runtime"/"excel"/"source"
        runtime.mkdir(parents=True)
        (runtime/"ULTIMATE LOAD  - NEPAL - 3 - BELT TRUSS, OUTRIGGER CAP TRUSS_NBC105_RS_Scaling.xlsx").write_bytes(b"OLD")
        self.assertEqual(copy_project_workbooks(runtime.parent.parent,export),[])
        self.assertFalse((export/"excel").exists())
        self.assertEqual(source_workbooks(runtime.parent.parent,export,"ULS"),[None,None])

    def test_missing_source_geometry_never_falls_back_to_old_aw(self):
        cfg=self.root/"OpenSees_Complete_Model_Config_V118.json"
        cfg.write_text('{"require_model_aligned_workbooks":true}',encoding="utf-8")
        with patch("components.inputs.opensees_nbc_sync._source_snapshot",
                   side_effect=ValueError("wrong 4x6m walls")):
            with patch("components.inputs.aw_sources.latest_linked_reference",
                       side_effect=AssertionError("Legacy lookup must not run")):
                got=resolve_aw(self.root,"ULS")
        self.assertIsNone(got["X"])
        self.assertIsNone(got["Y"])
        self.assertEqual(got["method"],"REQUIRES_SOURCE_VERIFIED_TWO_12M_WALLS")


if __name__=="__main__":
    unittest.main()
