"""Native-free, source-preserving time-history stage output regression."""
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import prepare_history_run, record_case_status


class HistoryOutputContractTests(unittest.TestCase):
    def test_unique_ltha_nltha_runs_and_declared_units(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"OpenSees_Complete_Linear_Model.py"
            model.write_text("assert True\n",encoding="utf-8")
            for method,stage in (("LTHA","06_LINEAR_TIME_HISTORY"),
                                 ("NLTHA","07_NONLINEAR_TIME_HISTORY")):
                for unit,basis in (("m","kN-m-s"),("mm","kN-mm-s")):
                    run=prepare_history_run(model,method,"ULS","Trial",
                                             model_length_unit=unit)
                    self.assertTrue(run.is_relative_to(root/stage/"RUNS"/"ULS"))
                    manifest=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
                    self.assertEqual(manifest["units"],basis)
                    self.assertEqual(manifest["solver_status"],"CREATED")
                    provenance=json.loads((run/"00_INPUT_SOURCE"/"HISTORY_INPUT_PROVENANCE.json").read_text())
                    self.assertIsNone(provenance["assembled_model_sha256"])
                    self.assertEqual(provenance["method"],method)
                    self.assertEqual(provenance["model_length_unit"],unit)
                    record_case_status(run,"INCOMPLETE")
                    updated=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
                    self.assertEqual(updated["structural_acceptance"],"NOT_VERIFIED")
            self.assertEqual(model.read_bytes(),b"assert True\n")

    def test_bad_configuration_does_not_create_spurious_run(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            model=root/"Source.py"
            model.write_text("pass")
            for args in (("LTHA","BOTH","Trial","m"),
                         ("LTHA","ULS","../hack","m"),
                         ("NLTHA","ULS","Suite","cm"),
                         ("ESM","ULS","Suite","m")):
                with self.assertRaises(ValueError):
                    prepare_history_run(model,*args[:3],model_length_unit=args[3])
            self.assertFalse((root/"06_LINEAR_TIME_HISTORY").exists())
            self.assertFalse((root/"07_NONLINEAR_TIME_HISTORY").exists())


if __name__=="__main__":
    unittest.main()
