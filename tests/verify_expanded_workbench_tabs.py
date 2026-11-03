"""Solver-free expansion checks; no native/OpenSees/Tk display required."""
import tempfile
import unittest
from pathlib import Path
from components.validation.expanded_workbench_tabs import (
    ALL_MODELS,EXTRA_MODELS,catalog_for,source_card,validate_measured_csv
)
class WorkbenchTests(unittest.TestCase):
    def test_models(self):
        self.assertEqual(len(ALL_MODELS),8)
        self.assertEqual(set(EXTRA_MODELS),{"Concrete02","ConcreteCM","SteelMPF","SFI_MVLEM_3D"})
    def test_catalog_models(self):
        for model in ALL_MODELS:
            for entry in catalog_for(model):
                self.assertEqual(entry["model"],model)
    def test_cards(self):
        for model in ALL_MODELS:
            with self.subTest(model=model):
                d=source_card(model)
                self.assertEqual(d["model"],model)
                self.assertIn("parameter_basis",d)
    def test_measurement(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.csv"
            p.write_text("x,y\n0,1\n1,2\n0,-1\n",encoding="utf-8")
            self.assertEqual(validate_measured_csv(p),3)
            p.write_text("x,y\n0,1\n1,nan\n0,-1\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Nonfinite"):
                validate_measured_csv(p)
if __name__=="__main__":unittest.main()
