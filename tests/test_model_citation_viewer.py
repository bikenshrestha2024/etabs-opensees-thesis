"""Citation viewer and Stage 02 reference packaging regression (headless)."""
import tempfile
import unittest
from pathlib import Path
from components.ui.reference_documents import (
    DEFAULT_REFERENCE, MAX_REFERENCE_BYTES, resolve_reference_document,
)


class CitationViewerTests(unittest.TestCase):
    def test_current_repo_reference_exists_and_is_bounded(self):
        path = resolve_reference_document()
        self.assertEqual(path.name, "02_MODEL_NBC_REFERENCE_AND_VALIDATION.md")
        self.assertLess(path.stat().st_size, MAX_REFERENCE_BYTES)
        content = path.read_text(encoding="utf-8")
        for required in ("NBC 105:2025", "MESH_04", "MESH_08", "MESH_16",
                         "P-Delta", "gravity", "Source"):
            self.assertIn(required.lower(), content.lower())

    def test_missing_document_has_readable_error(self):
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaisesRegex(FileNotFoundError, "Reference document missing"):
                resolve_reference_document(Path(name))

    def test_no_path_traversal(self):
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaisesRegex(ValueError, "within this repository"):
                resolve_reference_document(Path(name), "../outside.md")

    def test_no_giant_file_freeze(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            path = root / DEFAULT_REFERENCE
            path.parent.mkdir(parents=True)
            path.write_bytes(b"x" * (MAX_REFERENCE_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "too large"):
                resolve_reference_document(root)

    def test_launcher_no_longer_uses_nonexistent_sibling_markdown(self):
        source = (Path(__file__).parents[1] / "components/ui/application.py").read_text(
            encoding="utf-8")
        self.assertIn("open_reference_viewer(win)", source)
        self.assertNotIn('with_name("NBC105_FORMULA_REFERENCE_V116.md")', source)


if __name__ == "__main__":
    unittest.main()
