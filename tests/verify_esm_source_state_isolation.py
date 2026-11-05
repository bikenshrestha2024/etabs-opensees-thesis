"""Source-matched ULS/SLS ESM and ETABS case validation (synthetic).

No native ETABS, OpenSees, or private project model is required.
"""
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.project_workbooks import (
    source_limit_state, require_source_state, import_project_inputs,
)
from components.validation.etabs_direct_api import extract_from_sap


class SourceStateTests(unittest.TestCase):
    def _export(self,folder,filename):
        (folder/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps({"source_edb":r"D:\Models\"+filename}),encoding="utf-8")

    def test_ultimate_is_the_only_selected_state(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            self._export(folder,"ULTIMATE LOAD - NEPAL - 3 - BELT TRUSS.EDB")
            self.assertEqual(source_limit_state(folder)[0],"ULS")
            self.assertTrue(require_source_state(folder,"ULS"))
            with self.assertRaisesRegex(ValueError,"conflicts"):
                require_source_state(folder,"SLS")
            with self.assertRaisesRegex(ValueError,"conflicts"):
                import_project_inputs(folder,folder,"SLS")

    def test_service_is_the_only_selected_state(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            self._export(folder,"SERVICE LOAD - NEPAL - 3 - BELT TRUSS.EDB")
            self.assertEqual(source_limit_state(folder)[0],"SLS")
            self.assertTrue(require_source_state(folder,"SLS"))
            with self.assertRaisesRegex(ValueError,"conflicts"):
                import_project_inputs(folder,folder,"ULS")

    def test_ambiguous_name_is_not_automatically_classified(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            self._export(folder,"ULTIMATE SERVICE LOAD - 3 - BELT TRUSS.EDB")
            state,note=source_limit_state(folder)
            self.assertIsNone(state)
            self.assertIn("Ambiguous",note)

    def test_single_source_label_does_not_certify_material_stiffness(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            self._export(folder,"MODEL3.edb")
            state,_=source_limit_state(folder)
            self.assertIsNone(state)

    def test_direct_api_refuses_wrong_state_before_using_com(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            edb=folder/"ULTIMATE LOAD - NEPAL.EDB"
            edb.write_bytes(b"synthetic")
            mapping={"source_edb":str(edb),"cases":[
                {"etabs_case":"RS_SERVICE","method":"MRSM","limit_state":"SLS",
                 "case":"X_E0","axis":"X","story_map":{"Story25":25}}]}
            with self.assertRaisesRegex(ValueError,"Cross-limit-state"):
                extract_from_sap(object(),mapping)


if __name__=="__main__":
    unittest.main(verbosity=2)
