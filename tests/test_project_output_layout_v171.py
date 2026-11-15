"""Regression tests: source-specific directory safety, no ETABS API required."""
import json
import tempfile
import unittest
from pathlib import Path
from components.inputs.project_output_layout import (
    create_project_layout, case_folder, sha256_file)


class ProjectOutputLayoutTests(unittest.TestCase):
    def test_source_binding_and_case_folders(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            source = base / "source" / "ULTIMATE.EDB"
            source.parent.mkdir()
            source.write_bytes(b"fake edb bytes for filesystem-only test")
            output = base / "exports"
            result = create_project_layout(source, output)
            self.assertEqual(result["source_edb_sha256"], sha256_file(source))
            self.assertTrue((output / "00_SOURCE_MANIFEST" / "PROJECT_CONTEXT.json").is_file())
            folder = case_folder(result, "03_ESM", "X_E0", limit_state="ULS")
            self.assertEqual(folder, output / "03_ESM" / "ULS" / "X_E0")
            before = json.loads((output / "00_SOURCE_MANIFEST" / "PROJECT_CONTEXT.json").read_text())
            create_project_layout(source, output)
            after = json.loads((output / "00_SOURCE_MANIFEST" / "PROJECT_CONTEXT.json").read_text())
            self.assertEqual(before["created_utc"], after["created_utc"])
            with self.assertRaises(ValueError):
                case_folder(result, "03_ESM", "../secret")
            with self.assertRaises(ValueError):
                case_folder(result, "03_ESM", "C:\\absolute")
            for unsafe in ("COM4", "LPT9", "NUL", "X.", "A/B"):
                with self.assertRaises(ValueError):
                    case_folder(result, "03_ESM", unsafe)
            with self.assertRaises(ValueError):
                case_folder(result, "03_ESM", "CASE", limit_state="COM6")
            source.write_bytes(b"different file")
            with self.assertRaises(ValueError):
                create_project_layout(source, output)

    def test_project_layout_rejects_linked_manifest_and_stage_without_writes(self):
        for linked_component in ("00_SOURCE_MANIFEST", "02_GRAVITY"):
            with self.subTest(linked_component=linked_component):
                with tempfile.TemporaryDirectory() as d:
                    base = Path(d)
                    source = base / "source.EDB"
                    source.write_bytes(b"original private source")
                    output = base / "export"
                    outside = base / "outside"
                    output.mkdir()
                    outside.mkdir()
                    try:
                        (output / linked_component).symlink_to(
                            outside, target_is_directory=True)
                    except (OSError, NotImplementedError):
                        self.skipTest("Directory symlinks unavailable")
                    with self.assertRaisesRegex(ValueError, "linked"):
                        create_project_layout(source, output)
                    self.assertEqual(list(outside.iterdir()), [])
                    self.assertEqual(source.read_bytes(), b"original private source")
                    self.assertFalse((output / "00_SOURCE_MANIFEST" /
                                      "PROJECT_CONTEXT.json").exists())

    def test_invalid_existing_manifest_blocks_non_destructively(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            source = base / "model.EDB"
            source.write_bytes(b"source bytes")
            folder = base / "out" / "00_SOURCE_MANIFEST"
            folder.mkdir(parents=True)
            manifest = folder / "PROJECT_CONTEXT.json"
            manifest.write_text('["unexpected", "list"]', encoding="utf-8")
            original = manifest.read_bytes()
            with self.assertRaisesRegex(ValueError, "JSON object"):
                create_project_layout(source, folder.parent)
            self.assertEqual(manifest.read_bytes(), original)
            self.assertFalse((base / "out" / "02_GRAVITY").exists())

    def test_case_folder_rejects_linked_case_component(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            source = base / "model.EDB"
            source.write_bytes(b"source bytes")
            layout = create_project_layout(source, base / "export")
            outside = base / "outside"
            outside.mkdir()
            link = base / "export" / "03_ESM" / "ULS"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlinks unavailable")
            with self.assertRaisesRegex(ValueError, "linked"):
                case_folder(layout, "ESM", "X_E0", limit_state="ULS")
            self.assertEqual(list(outside.iterdir()), [])

    def test_optional_workbook_lfs_does_not_block_source(self):
        from components.inputs.lfs_workbook_recovery import audit_optional_gui_workbooks
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            source = base / "model.EDB"
            source.write_bytes(b"untouched source EDB placeholder")
            out = base / "out"
            data = audit_optional_gui_workbooks(base, out, source)
            self.assertFalse(data["conversion_blocked"])
            self.assertEqual(data["evidence_status"],
                             "INCOMPLETE_OPTIONAL_GRAVITY_VALIDATION")
            self.assertTrue((out / "Optional_Workbook_Conversion_Audit.json").exists())


if __name__ == "__main__":
    unittest.main()
