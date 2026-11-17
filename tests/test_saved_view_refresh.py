"""Regression: saved-view refresh changes HTML controls only."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.ui.saved_view_refresh import (
    VIEW_FILES, enhance_saved_html, refresh_saved_views)


class SavedViewRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.json_path = self.root / "OpenSees_Element_Connectivity.json"
        self.json_path.write_text('{"elements":[{"etabs_object":"B1"}]}',encoding="utf-8")
        self.report = self.root / "OpenSees_Complete_Export_Report_V118.json"
        self.report.write_text('{"assembly_errors":[]}',encoding="utf-8")
        self.model = self.root / "OpenSees_Complete_Model_Data_V118.json"
        self.model.write_text('{"nodes":{"1":[0,0,0]},"supports":{"1":[1,1,1,1,1,1]}}',
                              encoding="utf-8")
        self.original = {}
        for name in VIEW_FILES:
            original=('<html><body><div class="plotly-graph-div" '
                      'data-original-source="ETABS_UID_B1"></div>'
                      '<script id="shared-id-selector-v121">'
                      'const prefixes=["B","C","BR","CO","BT","CT","FVD","BRB"];'
                      '</script></body></html>')
            path=self.root/name
            path.write_text(original,encoding="utf-8")
            self.original[name]=original

    def test_load_views_collapse_and_default_specific_storey(self):
        for name in VIEW_FILES[2:]:
            html=enhance_saved_html(self.original[name],name)
            self.assertIn("load-view-collapsed",html)
            self.assertIn("highest",html)
            self.assertIn('storey.dispatchEvent(new Event("change"',html)
            self.assertIn("load-pattern-legend-v171",html)
            self.assertIn("Show element inspector / exact IDs",html)
            self.assertIn("ETABS_UID_B1",html)
            for prefix in ('"B"','"C"','"CO"','"BT"','"CT"','"FVD"','"BRB"'):
                self.assertIn(prefix,html)

    def test_structural_views_keep_inspector_expanded(self):
        for name in VIEW_FILES[:2]:
            self.assertEqual(enhance_saved_html(self.original[name],name),
                             self.original[name])

    def test_refresh_preserves_json_and_backs_up_original_html(self):
        baseline=self.model.read_bytes()
        source=self.json_path.read_bytes()
        result=refresh_saved_views(self.root)
        self.assertEqual(result["status"],"HTML_UPDATED")
        self.assertEqual(result["files"],4)
        self.assertEqual(len(result["changed"]),2)
        self.assertTrue(result["model_unchanged"])
        self.assertEqual(self.model.read_bytes(),baseline)
        self.assertEqual(self.json_path.read_bytes(),source)
        backup=Path(result["backup"])
        for name in VIEW_FILES:
            self.assertEqual((backup/name).read_text(encoding="utf-8"),
                             self.original[name])
        manifest=json.loads((backup/"VIEW_REFRESH_MANIFEST.json").read_text())
        self.assertTrue(manifest["no_etabs_or_opensees_solver_run"])
        self.assertEqual(manifest["source_connectivity_sha256"],
                         hashlib.sha256(source).hexdigest())

    def test_refresh_is_idempotent(self):
        refresh_saved_views(self.root)
        first={name:(self.root/name).read_bytes() for name in VIEW_FILES}
        result=refresh_saved_views(self.root)
        self.assertEqual(result["status"],"UNCHANGED")
        self.assertEqual(first,{name:(self.root/name).read_bytes()
                                for name in VIEW_FILES})

    def test_missing_view_fails_before_modifying_any_file(self):
        (self.root/VIEW_FILES[2]).unlink()
        with self.assertRaises(FileNotFoundError):
            refresh_saved_views(self.root)
        for name in (VIEW_FILES[0],VIEW_FILES[1],VIEW_FILES[3]):
            self.assertEqual((self.root/name).read_text(),self.original[name])

    def test_incomplete_report_is_rejected(self):
        self.report.write_text('{"assembly_errors":["problem"]}')
        with self.assertRaisesRegex(ValueError,"incomplete"):
            refresh_saved_views(self.root)
        self.assertEqual((self.root/VIEW_FILES[2]).read_text(),
                         self.original[VIEW_FILES[2]])

    def test_unsupported_and_malformed_html_rejected(self):
        with self.assertRaises(ValueError):
            enhance_saved_html("<html></html>","bad_file.html")
        with self.assertRaisesRegex(ValueError,"closing body"):
            enhance_saved_html('<div class="plotly-graph-div"></div>',
                               VIEW_FILES[2])


if __name__=="__main__":
    unittest.main()
