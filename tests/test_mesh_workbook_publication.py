"""Mesh-specific workbook publication must retain source evidence on errors.

No ETABS/OpenSees solver and no private model file required.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile


class MeshWorkbookPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.cfg={"floor_subdivisions":4}
        config=json.dumps(self.cfg).encode()
        (self.root/"OpenSees_Complete_Model_Config_V118.json").write_bytes(config)
        (self.root/"OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps({"config_sha256":hashlib.sha256(config).hexdigest(),
                        "shells":[{"category":"FLOOR"}]}),encoding="utf-8")
        self.output=self.root/"02_MODEL"/"SLAB_LOAD_PATH"/"MESH_04"

    @staticmethod
    def small_formula(wb, folder, data, cfg, progress=None):
        wb.create_sheet("Synthetic formula").append(["SOURCE TEST",4])

    def test_interrupted_save_leaves_no_published_mesh_workbook(self):
        from components.gravity.load_path_formulas import export
        def fail_save(wb,path):
            Path(path).write_bytes(b"PARTIAL_FAKE_MESH_XLSX")
            raise OSError("interrupted mesh workbook")
        with patch("components.gravity.load_path_formulas.add_formula_audit",
                   side_effect=self.small_formula), \
             patch("openpyxl.workbook.workbook.Workbook.save",
                   autospec=True,side_effect=fail_save):
            with self.assertRaisesRegex(OSError,"interrupted mesh"):
                export(self.root)
        excel=self.output/"EXCEL"
        self.assertFalse(list(excel.glob("*.xlsx")))
        self.assertFalse(list(excel.glob(".gravity_*.xlsx")))
        self.assertFalse(list(excel.glob(".mesh_*.xlsx")))
        self.assertFalse(list((self.output/"JSON").glob("*MANIFEST.json")))

    def test_manifest_records_sha256_of_completed_xlsx(self):
        from components.gravity.load_path_formulas import export
        with patch("components.gravity.load_path_formulas.add_formula_audit",
                   side_effect=self.small_formula):
            out=export(self.root)
        self.assertTrue(out.is_file())
        with ZipFile(out) as container:
            self.assertIn("xl/workbook.xml",container.namelist())
        manifests=list((self.output/"JSON").glob("*MANIFEST.json"))
        self.assertEqual(len(manifests),1)
        row=json.loads(manifests[0].read_text(encoding="utf-8"))
        self.assertEqual(row["workbook_sha256"],
                         hashlib.sha256(out.read_bytes()).hexdigest())
        self.assertEqual(row["validity"],
                         "FORMULA_AUDIT_ONLY_NOT_SOLVER_VERIFICATION")
        self.assertFalse(list((self.output/"EXCEL").glob(".mesh_*.xlsx")))

    def test_atomic_writer_rejects_redirected_symlink_output(self):
        from openpyxl import Workbook
        from components.gravity.workbook_publishing import publish_workbook
        other=self.root/"private_destination"
        other.mkdir()
        link=self.root/"redirected_output"
        try:
            link.symlink_to(other,target_is_directory=True)
        except (OSError,NotImplementedError):
            self.skipTest("Host cannot create folder symlinks")
        target=link/"unreviewed.xlsx"
        with self.assertRaisesRegex(ValueError,"linked XLSX"):
            publish_workbook(Workbook(),target,temp_prefix=".mesh_")
        self.assertEqual(list(other.iterdir()),[])

    def test_atomic_writer_preserves_previous_file_if_excel_has_file_lock(self):
        from openpyxl import Workbook
        from components.gravity.workbook_publishing import publish_workbook
        target=self.root/"existing.xlsx"
        target.write_bytes(b"PRIOR_EVIDENCE_UNCHANGED")
        with patch("components.gravity.workbook_publishing.os.replace",
                   side_effect=PermissionError("Excel has the file open")):
            with self.assertRaisesRegex(PermissionError,"Excel"):
                publish_workbook(Workbook(),target,temp_prefix=".mesh_")
        self.assertEqual(target.read_bytes(),b"PRIOR_EVIDENCE_UNCHANGED")
        self.assertFalse(list(self.root.glob(".mesh_*.xlsx")))

    def test_successful_corrupt_mesh_xlsx_is_not_marked_ready(self):
        from components.gravity.load_path_formulas import export
        def wrong_save(wb,path):
            Path(path).write_bytes(b"NOT_A_ZIP")
        with patch("components.gravity.load_path_formulas.add_formula_audit",
                   side_effect=self.small_formula), \
             patch("openpyxl.workbook.workbook.Workbook.save",
                   autospec=True,side_effect=wrong_save):
            with self.assertRaisesRegex(ValueError,"invalid XLSX"):
                export(self.root)
        self.assertFalse(list((self.output/"EXCEL").glob("*.xlsx")))
        self.assertFalse(list((self.output/"JSON").glob("*MANIFEST.json")))


if __name__=="__main__":
    unittest.main()
