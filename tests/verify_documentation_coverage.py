"""Static metadata contract for source guides. No native solver required."""
import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class DocumentationCoverage(unittest.TestCase):
    def test_all_active_modules_have_source_guide(self):
        paths=sorted((ROOT/"components").rglob("*.py"))
        self.assertGreaterEqual(len(paths),80)
        missing=[str(p.relative_to(ROOT)) for p in paths if not (ROOT/"docs"/"source"/(str(p.relative_to(ROOT))+".md")).is_file()]
        self.assertEqual(missing,[],f"Missing module documentation: {missing}")

    def test_key_sources_are_parseable(self):
        critical=["components/model/assembly.py",
           "components/nonlinear_time_history/building_exploratory.py",
           "components/nonlinear_time_history/research_building_materials.py",
           "components/sections/devices.py",
           "components/validation/nonlinear_performance.py"]
        for name in critical:
            with self.subTest(path=name):
                ast.parse((ROOT/name).read_text(encoding="utf-8-sig"),filename=name)

    def test_reference_and_gate_registry_present(self):
        refs=(ROOT/"docs"/"00_RESEARCH_REFERENCES.md").read_text(encoding="utf-8")
        gates=(ROOT/"docs"/"00_THESIS_ACCEPTANCE_GATES.md").read_text(encoding="utf-8")
        self.assertIn("R01",refs)
        self.assertIn("R13",refs)
        self.assertIn("G00",gates)
        self.assertIn("G10",gates)

if __name__=="__main__":
    unittest.main()
