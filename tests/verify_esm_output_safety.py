"""ESM P-Delta output safety and ULS/SLS period metadata regressions."""
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.calculation_and_gui import (
    validated_pdelta_sidecar_path, state_rayleigh_provenance,
)


class ESMOutputSafetyTests(unittest.TestCase):
    def test_blank_model_does_not_write_into_cwd(self):
        self.assertIsNone(validated_pdelta_sidecar_path(""))
        self.assertIsNone(validated_pdelta_sidecar_path("  "))
        self.assertIsNone(validated_pdelta_sidecar_path(None))

    def test_missing_model_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(validated_pdelta_sidecar_path(Path(tmp)/"missing.py"))

    def test_explicit_existing_model_retains_legacy_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            model=Path(tmp)/"model.py"
            model.write_text("# synthetic fixture\n",encoding="utf-8")
            self.assertEqual(
                validated_pdelta_sidecar_path(str(model)),
                Path(tmp)/"OpenSees_Initial_PDelta_Input_V124.json",
            )

    def test_non_python_file_not_selected_as_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            model=Path(tmp)/"results.csv"
            model.write_text("data",encoding="utf-8")
            self.assertIsNone(validated_pdelta_sidecar_path(model))

    def test_sls_period_provenance_is_not_uls(self):
        state=state_rayleigh_provenance(
            "SLS","Y",{"X":1.1,"Y":1.4},{"X":2.0,"Y":2.5})
        self.assertEqual(state["Rayleigh_T1_X_s"],2.0)
        self.assertEqual(state["Rayleigh_T1_Y_s"],2.5)
        self.assertEqual(state["Rayleigh_evidence_state"],"SLS")

    def test_uls_period_provenance_unchanged(self):
        state=state_rayleigh_provenance(
            "ULS","X",{"X":1.1,"Y":1.4},{"X":2.0,"Y":2.5})
        self.assertEqual(state["Rayleigh_T1_X_s"],1.1)
        self.assertEqual(state["Rayleigh_T1_Y_s"],1.4)

    def test_sls_missing_evidence_is_not_fabricated(self):
        state=state_rayleigh_provenance("SLS","X",{"X":1.1,"Y":1.4},{})
        self.assertIsNone(state["Rayleigh_T1_X_s"])
        self.assertIsNone(state["Rayleigh_T1_Y_s"])


if __name__=="__main__":
    unittest.main(verbosity=2)
