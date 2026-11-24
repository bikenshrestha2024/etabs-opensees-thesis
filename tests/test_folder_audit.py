"""Local filesystem tests: do not access any ETABS installation or external network."""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from components.inputs.folder_audit import audit_export_structure, write_folder_audit
from components.inputs.export_mirror import export_mirror


class FolderAuditTests(unittest.TestCase):
    def test_audit_missing_mirror_and_legacy_without_mutation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "ETABS" / "Case_3"
            root.mkdir(parents=True)
            source = root / "OpenSees_Element_Connectivity.json"
            source.write_text('{"nodes":[1]}', encoding="utf-8")
            edb = root / "source.EDB"
            edb.write_bytes(b"DO NOT TOUCH")
            sidecar = root / "Model_Data.json.processing.json"
            sidecar.write_text('{"stage":"working"}', encoding="utf-8")
            (root / "OpenSees_Analysis_Results" / "ULS_3").mkdir(parents=True)
            before = source.read_bytes()
            result = audit_export_structure(root)
            self.assertEqual(result["schema"], "THESIS_FOLDER_AUDIT_V1")
            self.assertEqual(result["missing_categorized_copies"],
                             ["OpenSees_Element_Connectivity.json"])
            self.assertEqual(result["legacy_analysis_case_folders"], ["ULS_3"])
            self.assertIn(sidecar.name, result["excluded_processing_sidecars"])
            self.assertFalse((root / "01_ETABS_EXPORT").exists())
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(edb.read_bytes(), b"DO NOT TOUCH")

    def test_copy_mirror_then_audit_detects_zero_conflicts(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "OpenSees_Element_Connectivity.json"
            source.write_text('{"verified":true}', encoding="utf-8")
            sidecar = root / "OpenSees_Element_Connectivity.json.processing.json"
            sidecar.write_text('{"working":true}', encoding="utf-8")
            (root / "secret.EDB").write_bytes(b"PRIVATE")
            export_mirror(root)
            self.assertFalse(any((root / "01_ETABS_EXPORT").rglob(sidecar.name)))
            result = audit_export_structure(root, verify_copies=True)
            self.assertFalse(result["missing_categorized_copies"])
            self.assertFalse(result["conflicting_categorized_copies"])
            self.assertEqual(source.read_text(), '{"verified":true}')
            self.assertTrue((root / "secret.EDB").is_file())

    def test_conflict_is_reported_not_overwritten(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "OpenSees_Element_Connectivity.json").write_text("authoritative")
            dest = root / "01_ETABS_EXPORT" / "02_MAPPING" / "OpenSees_Element_Connectivity.json"
            dest.parent.mkdir(parents=True)
            dest.write_text("DIFFERENT")
            report = audit_export_structure(root)
            self.assertEqual(len(report["conflicting_categorized_copies"]), 1)
            self.assertEqual(dest.read_text(), "DIFFERENT")

    def test_registered_auxiliary_folders_are_not_falsely_unexpected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("01_ETABS_EXPORT", "02_MODEL", "02_GRAVITY",
                         "08_ETABS_COMPARISONS", "09_SOFTWARE_DIAGNOSTICS",
                         "90_UPLOAD_PACKAGES", "REVIEW_MAIN",
                         "00_SOURCE_MANIFEST"):
                (root / name).mkdir()
            (root / "02_GRAVITY" / "Gravity_Response.json").write_text("{}")
            (root / "09_SOFTWARE_DIAGNOSTICS" / "old_report.xlsx").write_bytes(b"legacy")
            (root / "UNMAPPED_OUTPUT").mkdir()
            audit = audit_export_structure(root, verify_copies=False)
            self.assertEqual(audit["unexpected_top_level_folders"],
                             ["UNMAPPED_OUTPUT"])
            self.assertIn("MODEL", audit["stages"])
            self.assertIn("SOFTWARE_DIAGNOSTICS", audit["stages"])
            self.assertEqual(
                {item["stage"] for item in audit["loose_stage_outputs"]},
                {"GRAVITY", "SOFTWARE_DIAGNOSTICS"})
            self.assertEqual(
                {item["id"] for item in audit["findings"]
                 if item["id"] in ("LOOSE_STAGE_OUTPUTS",
                                   "UNREGISTERED_ROOT_DIRECTORIES")},
                {"LOOSE_STAGE_OUTPUTS", "UNREGISTERED_ROOT_DIRECTORIES"})
            self.assertTrue((root / "02_GRAVITY" / "Gravity_Response.json").exists())

    def test_symlinked_stage_is_blocked_without_scanning_outside(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"selected"
            outside=Path(tmp)/"outside"
            root.mkdir()
            outside.mkdir()
            (outside/"PRIVATE.json").write_text('{"sensitive":true}')
            try:
                (root/"02_GRAVITY").symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Stage symlinks not available on this runner")
            report=audit_export_structure(root)
            self.assertIn("02_GRAVITY",report["symlinked_stage_directories"])
            self.assertFalse(report["stages"]["GRAVITY"]["exists"])
            self.assertTrue(report["stages"]["GRAVITY"]["symlink_refused"])
            self.assertEqual(report["stages"]["GRAVITY"]["loose_files"],[])
            self.assertIn("SYMLINKED_CANONICAL_STAGE_BLOCKED",
                          {item["id"] for item in report["findings"]})

    def test_symlinked_legacy_analysis_root_is_reported_without_scanning(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"selected"
            outside=Path(tmp)/"private_elsewhere"
            root.mkdir()
            (outside/"CONFIDENTIAL_PROJECT").mkdir(parents=True)
            link=root/"OpenSees_Analysis_Results"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Legacy symlinks not available on this runner")
            result=audit_export_structure(root)
            self.assertTrue(result["symlinked_legacy_analysis_root"])
            self.assertEqual(result["legacy_analysis_case_folders"], [])
            self.assertNotIn("CONFIDENTIAL_PROJECT", str(result))
            self.assertIn("SYMLINKED_LEGACY_ANALYSIS_ROOT_BLOCKED",
                          {item["id"] for item in result["findings"]})
            self.assertFalse((root/"01_ETABS_EXPORT").exists())

    def test_reports_long_case_folders_all_stages_without_scanning_private_files(self):
        from components.inputs.output_layout import ALL_STAGE_FOLDERS
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"source_export"
            root.mkdir()
            long_name="ULS_Floor_3_"+"MODEL_LONG_"*8
            short_name="ESM_ULS_a1b2c3"
            for stage,folder in ALL_STAGE_FOLDERS.items():
                (root/folder/"RUNS"/"ULS"/long_name).mkdir(parents=True)
                (root/folder/"RUNS"/"ULS"/short_name).mkdir(parents=True)
            (root/"OpenSees_Analysis_Results"/long_name).mkdir(parents=True)
            report=audit_export_structure(root,verify_copies=False)
            risks=report["long_case_directories"]
            self.assertEqual(len(risks),len(ALL_STAGE_FOLDERS)+1)
            self.assertEqual({r["case_name"] for r in risks},{long_name})
            self.assertEqual(
                {r["stage"] for r in risks},
                set(ALL_STAGE_FOLDERS)|{"LEGACY"})
            self.assertTrue(all(r["case_component_length"]>48 for r in risks))
            self.assertTrue(all(r["status"]=="REVIEW_ONLY_NO_FILES_CHANGED"
                                for r in risks))
            self.assertIn("LONG_CASE_DIRECTORY_NAMES",
                          {v["id"] for v in report["findings"]})
            self.assertFalse((root/"01_ETABS_EXPORT"/"00_MANIFEST").exists())

    def test_linked_case_folder_is_not_followed_by_length_audit(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)/"selected"
            outside=Path(tmp)/"private"
            root.mkdir()
            outside.mkdir()
            (outside/"PRIVATE.EDB").write_bytes(b"not for inspection")
            state=root/"03_ESM"/"RUNS"/"ULS"
            state.mkdir(parents=True)
            try:
                (state/"UNTRUSTED").symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Directory symlinks unavailable")
            report=audit_export_structure(root,verify_copies=False)
            self.assertEqual(report["long_case_directories"],[])
            self.assertNotIn("PRIVATE.EDB",str(report))
            self.assertEqual((outside/"PRIVATE.EDB").read_bytes(),b"not for inspection")

    def test_saved_audit_is_local_and_contains_no_compliance_claim(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "01_ETABS_EXPORT").mkdir()
            json_path, md_path = write_folder_audit(root)
            self.assertTrue(json_path.is_file())
            self.assertTrue(md_path.is_file())
            self.assertIn("NOT_ENGINEERING_VALIDATION",
                          json.loads(json_path.read_text())["status"])
            self.assertIn("not structural validation", md_path.read_text().lower())


if __name__ == "__main__":
    unittest.main()
