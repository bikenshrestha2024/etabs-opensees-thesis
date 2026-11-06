"""Reproduce screenshot: Rayleigh button had float('') on missing Aw.

The preflight must provide actionable, source-state-aware diagnostics.
These tests use synthetic current-export fixtures, not project EDB physics.
"""
import json
import tempfile
import unittest
from pathlib import Path
from components.equivalent_static.calculation_and_gui import ESMGui


class ESMRayleighPreflight(unittest.TestCase):
    def folder(self,root,model):
        (root/"OpenSees_Complete_Model_Data_V118.json").write_text("{}")
        (root/"NBC105_ESM_Story_Weights_Assembled_V118.csv").write_text(
            "story_number,story_name,height_m,dead_load_kN,storage_live_load_kN,other_live_load_kN\n"
            "1,Story1,3,100,0,0\n")
        (root/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":model}))

    def test_screenshot_blank_aw_replaced_by_clear_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.folder(root,"D:/Models/ULTIMATE MODEL.EDB")
            values,issues=ESMGui._rayleigh_input_preflight("","", "ULS",root)
            self.assertEqual(values,{})
            self.assertTrue(any("Aw-X is blank" in i for i in issues))
            self.assertTrue(any("Aw-Y is blank" in i for i in issues))
            self.assertFalse(any("convert string to float" in i for i in issues))

    def test_rejects_scaling_label_and_nonfinite_number(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.folder(root,"D:/Models/ULTIMATE MODEL.EDB")
            _,issues=ESMGui._rayleigh_input_preflight("Aw (m²)","nan","ULS",root)
            self.assertTrue(any("not 'Aw (m²)'" in i for i in issues))
            self.assertTrue(any("finite" in i for i in issues))

    def test_source_service_cannot_be_uls_rayleigh(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.folder(root,"D:/Models/SERVICE MODEL.EDB")
            values,issues=ESMGui._rayleigh_input_preflight("3.5","1.2","ULS",root)
            self.assertEqual(values,{"X":3.5,"Y":1.2})
            self.assertTrue(any("Cross-state" in i for i in issues))

    def test_correct_state_numeric_values_do_not_get_invented(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.folder(root,"D:/Models/ULTIMATE MODEL.EDB")
            values,issues=ESMGui._rayleigh_input_preflight("3.5","1.2","ULS",root)
            self.assertEqual(values,{"X":3.5,"Y":1.2})
            self.assertFalse(issues)

    def test_missing_assembled_inputs_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            _,issues=ESMGui._rayleigh_input_preflight("3.5","1.2","ULS",temp)
            self.assertTrue(any("Missing current-export input" in i for i in issues))


if __name__=="__main__":
    unittest.main(verbosity=2)
