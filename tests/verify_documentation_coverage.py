"""Static check that every source-module guide resolves its internal links."""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DocumentationCoverage(unittest.TestCase):
    def test_source_guides_exist(self):
        paths=sorted((ROOT/"components").rglob("*.py"))
        self.assertGreaterEqual(len(paths),80)
        missing=[str(p.relative_to(ROOT)) for p in paths
                 if not (ROOT/"docs"/"source"/(str(p.relative_to(ROOT))+".md")).is_file()]
        self.assertEqual(missing,[])

    def test_all_relative_source_guide_links_resolve(self):
        files=[ROOT/"docs"/"source"/"00_SOURCE_GUIDE_INDEX.md"]
        files += sorted((ROOT/"docs"/"source"/"components").rglob("*.md"))
        unresolved=[]
        for file in files:
            content=file.read_text(encoding="utf-8")
            for raw in re.findall(r"\]\(([^)]+)\)", content):
                if "://" in raw or raw.startswith("#"):continue
                dest=(file.parent/raw.split("#")[0]).resolve()
                if not dest.is_relative_to(ROOT.resolve()) or not dest.exists():
                    unresolved.append((str(file.relative_to(ROOT)),raw))
        self.assertEqual(unresolved,[])

    def test_critical_module_sources_parse(self):
        paths=["components/model/assembly.py",
               "components/nonlinear_time_history/building_exploratory.py",
               "components/nonlinear_time_history/research_building_materials.py",
               "components/sections/devices.py",
               "components/validation/nonlinear_performance.py"]
        for name in paths:
            with self.subTest(path=name):
                ast.parse((ROOT/name).read_text(encoding="utf-8-sig"),filename=name)

    def test_research_register_and_gates(self):
        refs=(ROOT/"docs"/"00_RESEARCH_REFERENCES.md").read_text(encoding="utf-8")
        gates=(ROOT/"docs"/"00_THESIS_ACCEPTANCE_GATES.md").read_text(encoding="utf-8")
        self.assertIn("R01",refs)
        self.assertIn("R13",refs)
        self.assertIn("G00",gates)
        self.assertIn("G10",gates)

if __name__=="__main__":
    unittest.main()
