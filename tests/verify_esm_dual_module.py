"""Static regression checks for ETABS-linked ESM GUI integration (no ETABS license required)."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[1]
GUI=ROOT/"components/equivalent_static/calculation_and_gui.py"
LINK=ROOT/"components/equivalent_static/etabs_linked_excel.py"

class TestESMModules(unittest.TestCase):
    def test_modules_parse(self):
        for path in (GUI,LINK):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"))
    def test_dual_mode_preserved(self):
        source=GUI.read_text(encoding="utf-8")
        self.assertIn("OpenSees Direct Equivalent Static",source)
        self.assertIn("ETABS Linked Equivalent Static",source)
        self.assertIn("def _run_etabs_linked(self):",source)
        self.assertIn("def _calculate(self):",source)
        self.assertIn("def _use_explicit_excel_calculation(self):",source)
    def test_no_rs_scaling_in_adapter(self):
        source=LINK.read_text(encoding="utf-8")
        self.assertIn("eng.update_excel_from_etabs",source)
        self.assertIn("eng.calculate_direction",source)
        self.assertIn("eng.write_results_to_excel",source)
        self.assertIn('"response_spectrum_scale_factors_changed":False',source)
        self.assertNotIn("SetCase",source)
        self.assertNotIn("SetScaleFactor",source)
        self.assertNotIn("sap.Analyze.RunAnalysis()",source)
    def test_adapter_requires_original_calculator(self):
        source=LINK.read_text(encoding="utf-8")
        self.assertIn("_engine(engine_path)",source)
        self.assertIn("missing=[name for name in names",source)
        self.assertIn("shutil.copy2(workbook,target)",source)
        self.assertIn("comtypes.CoInitialize()",source)

if __name__=="__main__":
    unittest.main()
