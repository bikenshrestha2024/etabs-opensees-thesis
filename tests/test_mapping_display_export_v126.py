"""Regression checks: V126 uses the same display aliases as ID lookup.

Tests are static/stdlib-only because GitHub CI does not execute Windows ETABS or Tk/Matplotlib.
Native on-screen PNG/SVG/PDF export still requires a Windows GUI smoke test.
"""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "components/sections/mapping_audit.py"
GUI = ROOT / "components/sections/mapping_gui.py"


class TestMappingDisplayAndExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = AUDIT.read_text(encoding="utf-8")
        cls.gui = GUI.read_text(encoding="utf-8")

    def test_source_syntax(self):
        ast.parse(self.audit, filename=str(AUDIT))
        ast.parse(self.gui, filename=str(GUI))

    def test_shared_id_namespace(self):
        self.assertIn("from components.model.display_ids import build_labels", self.audit)
        self.assertIn("display_label=display_labels.get", self.audit)
        self.assertIn("str(e.get('dimension'))+':'+str(e.get('etabs_object'))", self.audit)
        self.assertIn("topology_tag=e.get('element_tag')", self.audit)
        self.assertIn("solver_tags=element_map.get(key,[])", self.audit)

    def test_gui_shows_alias_and_preserves_native_tag(self):
        self.assertIn("Display / topology tag", self.gui)
        self.assertIn('label=r.get(\'display_label\')', self.gui)
        self.assertIn("r['topology_tag']", self.gui)
        self.assertIn("f'{len(keys)} selected: '", self.gui)

    def test_explicit_export(self):
        self.assertIn("text='Export 3D figure…'", self.gui)
        self.assertIn("def export_figure(self):", self.gui)
        for suffix in (".png", ".svg", ".pdf"):
            self.assertIn(suffix, self.gui)
        self.assertIn("self.figure.savefig(", self.gui)
        self.assertIn("parent=self.win", self.gui)


if __name__ == "__main__":
    unittest.main()
