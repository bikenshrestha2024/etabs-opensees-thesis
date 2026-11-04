"""Pure-stdlib wall-probe preparation tests; never launches OpenSees."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.run_native_wall_probes import prepare, execute, PROBES


class ProbePreparation(unittest.TestCase):
    def test_four_cases_and_model_fingerprint(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            model=root/"model";model.mkdir()
            (model/"OpenSees_Complete_Model_Data_V118.json").write_text('{"nodes":{}}')
            source=root/"source.json"
            source.write_text(json.dumps({"model_folder":str(model),
                                          "analysis_intent":"RESEARCH_DIAGNOSTIC"}))
            dest=root/"probes"
            path=prepare(source,dest)
            doc=json.loads(path.read_text())
            self.assertEqual(set(doc["cases"]),set(PROBES))
            self.assertEqual(len(doc["input_probes"]),4)
            self.assertFalse(doc["native_model_verified"])
            with self.assertRaisesRegex(FileExistsError,"existing probe"):
                prepare(source,dest)
            with self.assertRaisesRegex(ValueError,"Explicit"):
                execute(path,allow_native=False)
    def test_thesis_mode_cannot_bypass_project_material_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);model=root/"model";model.mkdir()
            source=root/"source.json"
            source.write_text(json.dumps({"model_folder":str(model),
                                          "analysis_intent":"THESIS_NLTHA"}))
            with self.assertRaisesRegex(ValueError,"RESEARCH_DIAGNOSTIC"):
                prepare(source,root/"probes")

if __name__=="__main__":
    unittest.main()
