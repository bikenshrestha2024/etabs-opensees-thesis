"""Native-free audit for the source-aware NBC105 settings panel and V135 paths."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook
from components.ui.nbc105_settings_panel import (
    build_analysis_settings_review,
    design_check_output_diagnostic,
    export_analysis_settings_review,
)


class NBCSettingsPanelV12Tests(unittest.TestCase):
    def test_code_and_project_adoption_are_separate_from_verification(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            config=root/"OpenSees_Complete_Model_Config_V118.json"
            model.write_bytes(b'{"nodes":[]}')
            config.write_text(json.dumps({
                "slab_bending_factor":0.25,
                "slab_bending_factor_sls":0.35,
                "slab_stiffness_source":"IS 16700:2023 Table 5",
                "gravity_factors":{"DL":1,"Live":0.3}
            }))
            source_hash=model.read_bytes()
            data=build_analysis_settings_review(root)
            self.assertEqual(data["schema"],"NBC105_ANALYSIS_SETTINGS_REVIEW_V12")
            self.assertEqual(data["basis"],
                             "CODE_REFERENCE_AND_PROJECT_ADOPTION_NOT_ENGINEERING_CERTIFICATE")
            self.assertEqual(set(data["tables"]),{
                "Review & project","NBC code & combinations",
                "Mass source & patterns","Current model audit",
                "Mechanics & solver","Runtime & folders"})
            project=data["tables"]["Review & project"]
            slab=next(r for r in project if r["Item / equation"]=="Conventional beam-supported RC slab EI")
            self.assertEqual((slab["ULS / strength"],slab["SLS / service"]),
                             ("0.25 Ig","0.35 Ig"))
            self.assertIn("PROJECT-ADOPTED",slab["Evidence status"])
            self.assertFalse(any("NBC Table 3-1" in r["Authority"] for r in
                                 project if r["Item / equation"]=="Conventional beam-supported RC slab EI"))
            masses=data["tables"]["Mass source & patterns"]
            self.assertTrue(any("roof live" in r["Item / equation"].lower()
                                and r["ULS / strength"]=="0.0" for r in masses))
            audit=data["tables"]["Current model audit"]
            self.assertTrue(any(r["Item / equation"]=="Conventional slab bending factors"
                                for r in audit))
            project_names=[r["Item / equation"] for r in project]
            self.assertIn("PD_INIT_EL_X_PLUS",project_names)
            self.assertIn("PD_INIT_EL_Y_MINUS",project_names)
            code=data["tables"]["NBC code & combinations"]
            flat=next(r for r in code if r["Item / equation"]=="flat_slab")
            self.assertEqual((flat["ULS / strength"],flat["SLS / service"]),("0.25","0.5"))
            self.assertTrue(any("Rayleigh" in r["Item / equation"] for r in code))
            self.assertTrue(any("1.25" in r["ULS / strength"] for r in code))
            self.assertEqual(model.read_bytes(),source_hash)

    def test_v135_legacy_vs_canonical_diagnostic(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            initial=design_check_output_diagnostic(root)
            self.assertEqual(initial["status"],"NO_SAVED_DESIGN_REPORT")
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())
            legacy=root/"OpenSees_Analysis_Results"/"Design_Checks_V135"
            legacy.mkdir(parents=True)
            old=legacy/"Design_Check_Report_V135.json"
            old.write_text("{}")
            self.assertEqual(design_check_output_diagnostic(root)["status"],
                             "LEGACY_REPORT_ONLY")
            modern=root/"09_SOFTWARE_DIAGNOSTICS"/"DESIGN_CHECKS_V135"
            modern.mkdir(parents=True)
            new=modern/"Design_Check_Report_V135.json"
            new.write_text("{}")
            os.utime(new,ns=(100,100))
            os.utime(old,ns=(200,200))
            self.assertEqual(design_check_output_diagnostic(root)["status"],
                             "LEGACY_REPORT_NEWER_REVIEW_ACTIVE_LAUNCHER")
            os.utime(new,ns=(300,300))
            self.assertEqual(design_check_output_diagnostic(root)["status"],
                             "CANONICAL_REPORT_PRESENT")
            self.assertEqual(old.read_text(),"{}")

    def test_consistent_excel_and_json_local_canonical_export(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            root.joinpath("OpenSees_Complete_Model_Data_V118.json").write_text("{}")
            original=root/"original.EDB"
            original.write_bytes(b"unchanged sensitive source")
            report=build_analysis_settings_review(root)
            json_file,xlsx_file=export_analysis_settings_review(report)
            self.assertTrue(json_file.is_relative_to(root/"09_SOFTWARE_DIAGNOSTICS"/"ANALYSIS_SETTINGS"))
            self.assertTrue(xlsx_file.is_file())
            saved=json.loads(json_file.read_text())
            self.assertEqual(saved["schema"],report["schema"])
            book=load_workbook(xlsx_file)
            self.assertIn("Review & project",book.sheetnames)
            self.assertIn("NBC code & combinations",book.sheetnames)
            self.assertEqual(book["Review & project"]["A1"].value,"Topic")
            self.assertEqual(book["NBC code & combinations"]["B1"].value,"Item / equation")
            self.assertFalse(book["Review & project"].sheet_view.showGridLines)
            self.assertEqual(book["Review & project"].freeze_panes,"A2")
            self.assertEqual(original.read_bytes(),b"unchanged sensitive source")

    def test_nonfinite_slab_factor_is_reported_not_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text("{}")
            (root/"OpenSees_Complete_Model_Config_V118.json").write_text(
                json.dumps({"slab_bending_factor":float("nan"),
                            "slab_bending_factor_sls":float("inf"),
                            "gravity_factors":{"Self Weight":1.0,
                                               "Wall":1.0,
                                               "Floor Finish":1.0}}))
            report=build_analysis_settings_review(root)
            self.assertTrue(any("ULS slab bending factor" in x and
                                "not a valid number" in x for x in report["warnings"]))
            self.assertTrue(any("SLS slab bending factor" in x and
                                "not a valid number" in x for x in report["warnings"]))
            self.assertTrue(any("Self Weight" in x and "Wall" in x and
                                "missing from illustrative mass aliases" in x
                                for x in report["warnings"]))
            self.assertEqual(len([r for r in report["tables"]["Review & project"]
                                  if r["Topic"]=="Mandatory signed P-Delta"]),4)
            self.assertTrue(any("PD_INIT_EL_X_PLUS" in x
                                for x in report["warnings"]))

    def test_null_slab_source_does_not_crash_settings_audit(self):
        from components.validation.settings_audit import audit
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Complete_Model_Config_V118.json").write_text(
                json.dumps({"slab_stiffness_source":None,
                            "slab_bending_factor":0.25,
                            "slab_bending_factor_sls":0.35}))
            report=audit(root)
            slab=next(x for x in report["rows"]
                      if x["item"]=="Conventional slab bending factors")
            self.assertIn("No source recorded",slab["basis"])

    def test_main_gui_delegates_to_new_panel(self):
        source=Path(__file__).resolve().parents[1]/"components"/"ui"/"application.py"
        content=source.read_text(encoding="utf-8")
        self.assertIn("from components.ui.nbc105_settings_panel import launch",content)


if __name__=="__main__":
    unittest.main()
