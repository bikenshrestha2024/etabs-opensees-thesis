"""Source EDB SHA and workbook identity: never silently use stale 12m data."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook
from components.inputs.model_aligned_reference import verified_reference
from components.inputs.project_workbooks import source_workbooks


class Registered12mModelWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.edb=self.root/"ULTIMATE LOAD - Model.EDB"
        self.edb.write_bytes(b"native source model A")
        self.reference=self.root/"NBC105_2025_95m_12m_MODEL_ALIGNED_V10_7.xlsx"
        wb=Workbook();wb.active.title="NBC Calculator"
        wb.save(self.reference)
        self.model_data=self.root/"OpenSees_Complete_Model_Data_V118.json"
        self.model_data.write_text('{"source":"unaltered"}',encoding="utf-8")
        self.manifest=self.root/"00_SOURCE_MANIFEST"/"MODEL_ALIGNED_12M_WORKBOOK.json"
        self.manifest.parent.mkdir()
        self.config=self.root/"OpenSees_Complete_Model_Config_V118.json"
        self.config.write_text('{"require_model_aligned_workbooks":true}',
                               encoding="utf-8")
        def sha(path):
            return hashlib.sha256(path.read_bytes()).hexdigest()
        self.record={
            "status":"CURRENT_12M_WORKBOOK_SOURCE_IDENTIFIED_NOT_CODE_ACCEPTED",
            "workbook_path":str(self.reference),
            "workbook_sha256":sha(self.reference),
            "source_edb":str(self.edb),
            "source_edb_sha256":sha(self.edb),
            "assembled_model_sha256":sha(self.model_data),
            "limit_state":"ULS",
            "sheets":["NBC Calculator"],
            "wall_geometry_verification":{
                "classification":"EXPORTED_GEOMETRY_VERIFIED_NOT_NATIVE_ETABS_CERTIFIED",
            },
        }
        self.manifest.write_text(json.dumps(self.record),encoding="utf-8")

    def _guards(self):
        return patch("components.inputs.project_workbooks._source_edb_path",
                     return_value=str(self.edb))

    def test_exact_current_source_workbook_is_selected_only_for_same_state(self):
        with self._guards():
            with patch("components.inputs.project_workbooks.source_limit_state",
                       return_value=("ULS","source")):
                selected=source_workbooks(self.root,self.root,"ULS")
                self.assertEqual(selected,[self.reference,None])
                with self.assertRaisesRegex(ValueError,"state mismatch"):
                    verified_reference(self.root,state="SLS")

    def test_modified_workbook_invalidates_registry_and_never_falls_back(self):
        self.reference.write_bytes(self.reference.read_bytes()+b"tampered")
        with self._guards():
            with self.assertRaisesRegex(ValueError,"changed"):
                source_workbooks(self.root,self.root,"ULS")

    def test_changed_rebuilt_shell_geometry_invalidates_workbook(self):
        self.model_data.write_text('{"source":"new shell geometry"}',encoding="utf-8")
        with self._guards():
            with self.assertRaisesRegex(ValueError,"shell/model bytes changed"):
                source_workbooks(self.root,self.root,"ULS")

    def test_wrong_edb_blocks_selection(self):
        self.edb.write_bytes(b"different source ETABS EDB")
        with self._guards():
            with self.assertRaisesRegex(ValueError,"EDB changed"):
                source_workbooks(self.root,self.root,"ULS")

    def test_absent_registration_selects_no_legacy_calculator(self):
        self.manifest.unlink()
        with self._guards():
            self.assertEqual(source_workbooks(self.root,self.root,"ULS"),
                             [None,None])


if __name__=="__main__":
    unittest.main()
