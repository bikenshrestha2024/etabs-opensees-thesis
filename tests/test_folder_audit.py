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
