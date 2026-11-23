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
            model.write_bytes(b"assert True\n")
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

    def test_history_run_compact_case_name_is_source_bound(self):
        import hashlib
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            stem="OpenSees_Complete_Linear_Model_"+"LONG_NAME_"*20
            model=root/(stem+".py")
            model.write_text("print('source A')\\n",encoding="utf-8")
            run=prepare_history_run(model,"LTHA","ULS","Trial",
                                    model_length_unit="m")
            case=run.parent.name
            expected=hashlib.sha256(model.read_bytes()).hexdigest()[:12]
            self.assertLessEqual(len(case),48)
            self.assertIn(expected,case)
            self.assertNotIn("LONG_NAME",case)
            manifest=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
            evidence=json.loads((run/"00_INPUT_SOURCE"/"HISTORY_INPUT_PROVENANCE.json").read_text())
            self.assertEqual(manifest["case_id"],case)
            self.assertEqual(evidence["model_script_sha256"],hashlib.sha256(model.read_bytes()).hexdigest())
            model.write_text("print('source B')\\n",encoding="utf-8")
            second=prepare_history_run(model,"LTHA","ULS","Trial",
                                       model_length_unit="m")
            self.assertNotEqual(case,second.parent.name)
            self.assertTrue(run.exists())

    def test_compact_case_id_is_shared_across_stage_keys(self):
        from components.inputs.output_contract import compact_case_id
        from components.inputs.output_layout import STAGE_FOLDERS
        digest="a"*64
        for method in ("MODEL","GRAVITY","ESM","MODAL","MRSM","LTHA","NLTHA"):
            with self.subTest(method=method):
                value=compact_case_id(method,"Test scope",digest)
                self.assertLessEqual(len(value),48)
                self.assertTrue(value.endswith(digest[:12]))
                self.assertNotIn(" ",value)

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
