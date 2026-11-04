"""RTFC prompt contract checks (stdlib only, does not run OpenSees)."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROMPTS=ROOT/"docs"/"rtfc"
REQUIRED=("ROLE","TASK","FORMAT","CONSTRAINTS")
EXPECTED=(
    "00_PROJECT_ENGINEERING_RTFC.md",
    "01_X_WALL_FAILURE_RTFC.md",
    "02_SOIL_C_RECORDS_RTFC.md",
    "03_MATERIALS_WALL_FVD_BRB_RTFC.md",
    "04_M0_M6_COMPARISON_RTFC.md",
)

class RTFCContractTests(unittest.TestCase):
    def test_numbered_prompts_all_have_ordered_sections(self):
        for name in EXPECTED:
            with self.subTest(prompt=name):
                p=PROMPTS/name
                self.assertTrue(p.is_file(),name)
                data=p.read_text(encoding="utf-8")
                sections=re.findall(r"^## (ROLE|TASK|FORMAT|CONSTRAINTS)\\s*$",data,re.M)
                self.assertEqual(sections,list(REQUIRED),name)
                for section in REQUIRED:
                    self.assertGreater(len(data.split("## "+section,1)[-1].split("## ",1)[0].strip()),70)
    def test_context_invariants(self):
        text=(PROMPTS/"00_PROJECT_ENGINEERING_RTFC.md").read_text(encoding="utf-8")
        for literal in ("0.05","9.80665","1.0","XY","YX","Gorkha","Loma","Tn90"):
            self.assertIn(literal,text)
    def test_issue_template_and_agents(self):
        y=(ROOT/".github/ISSUE_TEMPLATE/engineering_rtfc.yml").read_text(encoding="utf-8")
        for part in REQUIRED:
            self.assertIn("label: "+part,y)
        self.assertIn("docs/rtfc/README.md",(ROOT/"AGENTS.md").read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
