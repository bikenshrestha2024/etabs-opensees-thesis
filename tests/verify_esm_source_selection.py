"""ESM assembled ledger input selection must preserve source/model identity."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from components.equivalent_static.calculation_and_gui import recommended_story_weight_input

class ESMSourceSelection(unittest.TestCase):
    def test_model_matched_assembled_values_preferred(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            template=root/"NBC105_ESM_Story_Weights_Input_V108.csv"
            template.write_text("story_number,height_m\n1,3.8\n",encoding="utf8")
            source=root/"NBC105_ESM_Story_Weights_Assembled_V118.csv"
            source.write_text(
                "story_number,master_node_tag,height_m,dead_load_kN,storage_live_load_kN,other_live_load_kN\n"
                "1,1234,3.8,100,0,30\n",encoding="utf8")
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text(json.dumps({"diaphragms":[
                {"storey_number":1,"master_tag":1234}]}),encoding="utf8")
            chosen,note=recommended_story_weight_input(root)
            self.assertEqual(chosen,source)
            self.assertIn("independently review",note)
            source.write_text(source.read_text().replace("1,1234,","1,9999,"))
            chosen,note=recommended_story_weight_input(root)
            self.assertEqual(chosen,template)
            self.assertIn("rejected",note)
    def test_missing_structural_model_never_auto_promotes_old_weights(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"NBC105_ESM_Story_Weights_Assembled_V118.csv").write_text("old")
            chosen,_=recommended_story_weight_input(root)
            self.assertIsNone(chosen)

if __name__=="__main__":unittest.main()
