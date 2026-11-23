"""Source-only, synthetic regression of area evidence ZIP publisher.

No ETABS, OpenSees, solver or private model inputs are used.
"""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from components.sections.area_elements import package_area_integration_evidence


class AreaEvidenceZipTests(unittest.TestCase):
    def sources(self, root):
        paths = []
        for filename, data in (
            ("topology.json", '{"node_map":[],"elements":[]}'),
            ("assignments.csv", "etabs_object,assigned_property\n"),
            ("config.json", '{"source_reviewed_by_user":false}'),
        ):
            path = root / filename
            path.write_text(data, encoding="utf-8")
            paths.append(path)
        return dict(topology_json=paths[0],
                    area_assignment_csv=paths[1], config_json=paths[2],
                    output_dir=root)

    def test_source_only_zip_has_real_files_verified_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kw = self.sources(root)
            script = root / "inactive.py"
            script.write_text("AREA_STAGE_EXECUTION = False\n", encoding="utf-8")
            zpath = package_area_integration_evidence(**kw, integration_script=script)
            self.assertEqual(zpath.parent, root / "02_MODEL" / "AREA_INTEGRATION" / "07_EXPORT_ZIP")
            with zipfile.ZipFile(zpath) as archive:
                self.assertIsNone(archive.testzip())
                manifest = json.loads(archive.read("AREA_EVIDENCE_MANIFEST.json"))
                self.assertFalse(manifest["solver_executed"])
                self.assertFalse(manifest["analysis_ready"])
                self.assertEqual(manifest["engineering_acceptance"], "NOT_VERIFIED")
                self.assertNotIn(str(root), json.dumps(manifest))
                self.assertEqual(len(manifest["files_sha256"]), 4)
                for name, expected in manifest["files_sha256"].items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)

    def test_missing_required_source_aborts_without_zip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kw = self.sources(root)
            kw["config_json"].unlink()
            with self.assertRaises(FileNotFoundError):
                package_area_integration_evidence(**kw)
            self.assertFalse((root / "02_MODEL").exists())

    def test_selected_missing_optional_file_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kw = self.sources(root)
            with self.assertRaises(FileNotFoundError):
                package_area_integration_evidence(
                    **kw, integration_script=root / "not_generated.py")

    def test_zip_is_not_a_solver_success_indicator(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kw = self.sources(root)
            result = package_area_integration_evidence(**kw)
            with zipfile.ZipFile(result) as archive:
                manifest = json.loads(archive.read("AREA_EVIDENCE_MANIFEST.json"))
            self.assertEqual(manifest["package_purpose"], "SOURCE_ONLY_AREA_INTEGRATION_REVIEW")
            self.assertIn("inventory/Area_Integration_Inventory.xlsx", manifest["missing_optional"])


if __name__ == "__main__":
    unittest.main()
