"""Regression: complete gravity evidence must not await slow Excel formulas."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from components.gravity.storey_loads import export_storey_gravity, main


class DeferredStoreyWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.data={
            "nodes":{1:[0.,0.,0.],2:[0.,0.,3.8]},
            "base_z_m":0.,
            "diaphragms":[{"storey_number":1,"master_xyz":[0.,0.,3.8]}],
            "load_provenance":[
                {"node":1,"source":"FRAME:1","component":"self_weight_column",
                 "pattern":"Self Weight","downward_kN":5.},
                {"node":2,"source":"AREA:100","component":"area_load",
                 "pattern":"Floor Finish","downward_kN":10.},
                {"node":2,"source":"AREA:100","component":"area_load",
                 "pattern":"Live","downward_kN":2.}
            ],
            "total_downward_load_kN":17.,
            "config_sha256":"recorded-sha"
        }
        self.cfg={"gravity_factors":{"Self Weight":1.,"Floor Finish":1.,"Live":1.},
                  "mass_factors":{"Self Weight":1.,"Floor Finish":1.,"Live":.3}}

    def test_deferred_import_keeps_full_ledger_without_excel(self):
        before=json.dumps(self.data,sort_keys=True)
        result=export_storey_gravity(self.root,self.data,self.cfg,
                                    pattern_types={"Live":3},
                                    generate_workbook=False)
        self.assertEqual(result["total_applied_kN"],17.)
        self.assertEqual(result["reconciliation_error_kN"],0.)
        self.assertEqual(json.dumps(self.data,sort_keys=True),before)
        self.assertTrue((self.root/"Gravity_Storey_Load_Breakdown_V131.json").is_file())
        self.assertTrue((self.root/"Gravity_Storey_Load_Breakdown_V131.csv").is_file())
        self.assertTrue((self.root/"Gravity_Source_Load_Detail_V131.csv").is_file())
        self.assertFalse((self.root/"Gravity_Storey_Load_Breakdown_V131.xlsx").exists())
        marker=json.loads((self.root/"Gravity_Storey_Workbook_Status_V131.json").read_text())
        self.assertEqual(marker["status"],"DEFERRED_FORMULA_WORKBOOK_NOT_A_MODEL_FAILURE")
        self.assertEqual(marker["detail_rows"],3)
        self.assertEqual(marker["gravity_total_kN"],17.)
        self.assertEqual(len(result["rows"]),2)  # BASE + Storey 1
        self.assertEqual(sum(row["applied_total_kN"] for row in result["rows"]),17.)

    def test_old_workbook_archived_not_mistaken_for_new_model(self):
        old=self.root/"Gravity_Storey_Load_Breakdown_V131.xlsx"
        old.write_bytes(b"old workbook from different source EDB")
        export_storey_gravity(self.root,self.data,self.cfg,generate_workbook=False)
        self.assertFalse(old.exists())
        marker=json.loads((self.root/"Gravity_Storey_Workbook_Status_V131.json").read_text())
        archived=Path(marker["original_xlsx_archived_at"])
        self.assertTrue(archived.is_file())
        self.assertEqual(archived.read_bytes(),b"old workbook from different source EDB")
        self.assertIn("09_SOFTWARE_DIAGNOSTICS",str(archived))

    def test_failed_formula_save_preserves_previous_workbook(self):
        import sys
        import types
        from unittest.mock import patch
        old=self.root/"Gravity_Storey_Load_Breakdown_V131.xlsx"
        old.write_bytes(b"PREVIOUS_VALID_WORKBOOK_BYTES")
        extra=types.ModuleType("OpenSees_Load_Path_V141")
        extra.add_formula_audit=lambda wb, folder, data, cfg: wb.create_sheet("Formula")
        attempted=[]

        def broken_save(workbook, path):
            attempted.append(Path(path))
            Path(path).write_bytes(b"PARTIAL_XLSX")
            raise OSError("simulated interrupted XLSX serialization")

        with patch.dict(sys.modules,{"OpenSees_Load_Path_V141":extra}), \
             patch("openpyxl.workbook.workbook.Workbook.save",
                   autospec=True,side_effect=broken_save):
            with self.assertRaisesRegex(OSError,"interrupted XLSX"):
                export_storey_gravity(self.root,self.data,self.cfg,
                                     generate_workbook=True)
        self.assertEqual(old.read_bytes(),b"PREVIOUS_VALID_WORKBOOK_BYTES")
        self.assertTrue(attempted)
        self.assertNotEqual(attempted[0],old)
        self.assertFalse(attempted[0].exists())
        marker=json.loads((self.root/"Gravity_Storey_Workbook_Status_V131.json").read_text())
        self.assertEqual(marker["status"],"FORMULA_WORKBOOK_EXPORT_FAILED")
        self.assertNotIn("workbook_sha256",marker)

    def test_successful_but_corrupt_zip_is_not_marked_ready(self):
        import sys
        import types
        extra=types.ModuleType("OpenSees_Load_Path_V141")
        extra.add_formula_audit=lambda wb,folder,data,cfg:wb.create_sheet("Formula")
        old=self.root/"Gravity_Storey_Load_Breakdown_V131.xlsx"
        old.write_bytes(b"KNOWN_PREVIOUS_EVIDENCE")
        def corrupt_save(wb,path):
            Path(path).write_bytes(b"NOT_AN_XLSX_ZIP")
        with patch.dict(sys.modules,{"OpenSees_Load_Path_V141":extra}), \
             patch("openpyxl.workbook.workbook.Workbook.save",
                   autospec=True,side_effect=corrupt_save):
            with self.assertRaisesRegex(ValueError,"invalid XLSX"):
                export_storey_gravity(self.root,self.data,self.cfg,generate_workbook=True)
        self.assertEqual(old.read_bytes(),b"KNOWN_PREVIOUS_EVIDENCE")
        marker=json.loads((self.root/"Gravity_Storey_Workbook_Status_V131.json").read_text())
        self.assertEqual(marker["status"],"FORMULA_WORKBOOK_EXPORT_FAILED")
        self.assertFalse(list(self.root.glob(".gravity_*.xlsx")))

    def test_optional_workbook_sha256_streams_file_instead_of_reading_all_bytes(self):
        import sys
        import types
        extra=types.ModuleType("OpenSees_Load_Path_V141")
        extra.add_formula_audit=lambda wb, folder, data, cfg: wb.create_sheet("Formula")
        read_bytes=Path.read_bytes

        def reject_eager_xlsx_read(path):
            if Path(path).suffix.casefold()==".xlsx":
                raise AssertionError("XLSX checksum must stream, not read all bytes")
            return read_bytes(path)

        with patch.dict(sys.modules,{"OpenSees_Load_Path_V141":extra}), \
             patch.object(Path,"read_bytes",reject_eager_xlsx_read):
            result=export_storey_gravity(self.root,self.data,self.cfg,
                                        generate_workbook=True)
        xlsx=self.root/"Gravity_Storey_Load_Breakdown_V131.xlsx"
        marker=json.loads((self.root/"Gravity_Storey_Workbook_Status_V131.json").read_text())
        self.assertEqual(result["total_applied_kN"],17.)
        self.assertTrue(xlsx.is_file())
        self.assertEqual(marker["status"],"FORMULA_WORKBOOK_READY")
        self.assertEqual(marker["workbook_sha256"],
                         hashlib.sha256(read_bytes(xlsx)).hexdigest())
        self.assertFalse(list(self.root.glob(".gravity_*.xlsx")))

    def test_manual_regeneration_rejects_mismatched_configuration(self):
        cfg=self.root/"OpenSees_Complete_Model_Config_V118.json"
        model=self.root/"OpenSees_Complete_Model_Data_V118.json"
        report=self.root/"OpenSees_Complete_Export_Report_V118.json"
        (self.root/"OpenSees_Load_Conversion_Audit.json").write_text("{}")
        cfg.write_text(json.dumps(self.cfg))
        report.write_text('{"assembly_errors":[],"elastic_assembled":true}')
        model.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError,"Config changed"):
            main(["--workbook",str(self.root)])
        self.assertFalse((self.root/"Gravity_Storey_Load_Breakdown_V131.xlsx").exists())

    def test_manual_regeneration_rejects_incomplete_assembly(self):
        cfg=self.root/"OpenSees_Complete_Model_Config_V118.json"
        model=self.root/"OpenSees_Complete_Model_Data_V118.json"
        report=self.root/"OpenSees_Complete_Export_Report_V118.json"
        config_bytes=json.dumps(self.cfg).encode()
        cfg.write_bytes(config_bytes)
        self.data["config_sha256"]=hashlib.sha256(config_bytes).hexdigest()
        model.write_text(json.dumps(self.data))
        report.write_text('{"assembly_errors":["failed mesh"],"elastic_assembled":false}')
        with self.assertRaisesRegex(ValueError,"incomplete"):
            main(["--workbook",str(self.root)])


if __name__=="__main__":
    unittest.main()
