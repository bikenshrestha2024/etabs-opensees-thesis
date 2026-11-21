"""Saved Rayleigh results made with g = 9.81 are rejected with a stated cause.

NBC 105 gravity constant changed 9.81 -> 9.80665 in this release; unit tests
only, no ETABS/OpenSees. Tolerance and solver numerics are unchanged.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.project_workbooks import import_project_inputs
from components.modal.rayleigh import (
    RAYLEIGH_DISPLACEMENT_BASIS, RAYLEIGH_METHOD_VERSION, rayleigh_result_prefix,
)
from components.modal.rayleigh_ledger_audit import (
    verify_rayleigh_sum, verify_saved_rayleigh_axis,
)
from components.inputs.project_workbooks import analysis_output_folder
from tests.test_rayleigh_saved_evidence_gate import valid_axis


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _axis_with_g(g):
    axis = valid_axis()
    rec = verify_rayleigh_sum(axis["rows"], g=g)
    axis.update(period_s=rec["period_s"], rayleigh_numerator_kN_m2=rec["numerator_kN_m2"],
                rayleigh_denominator_gFiDi_kN_m2_s2=rec["denominator_kN_m2_s2"],
                Aw_m2=10.0)
    return axis


class SavedRayleighGravityTests(unittest.TestCase):
    def test_axis_recorded_with_9_81_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            verify_saved_rayleigh_axis(_axis_with_g(9.81))
        self.assertIn("mismatch", str(ctx.exception))
        verify_saved_rayleigh_axis(_axis_with_g(9.80665))  # current g accepted

    def _import(self, g):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder = Path(tmp.name)
        (folder / "OpenSees_Complete_Model_Data_V118.json").write_text("{}", encoding="utf-8")
        (folder / "OpenSees_Complete_Model_Config_V118.json").write_text("{}", encoding="utf-8")
        (folder / "NBC105_ESM_Story_Weights_Assembled_V118.csv").write_text("a\n", encoding="utf-8")
        axis = _axis_with_g(g)
        result = {
            "model_config_sha256": _sha(folder / "OpenSees_Complete_Model_Config_V118.json"),
            "method_version": RAYLEIGH_METHOD_VERSION,
            "displacement_basis": RAYLEIGH_DISPLACEMENT_BASIS,
            "limit_state": "ULS",
            "model_sha256": _sha(folder / "OpenSees_Complete_Model_Data_V118.json"),
            "story_weights_sha256": _sha(folder / "NBC105_ESM_Story_Weights_Assembled_V118.csv"),
            "gravity_acceleration_m_s2": g,
            "X": axis, "Y": json.loads(json.dumps(axis)),
        }
        out = analysis_output_folder(folder, "ULS")
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / (rayleigh_result_prefix("ULS") + ".json")).write_text(
            json.dumps(result), encoding="utf-8")
        return import_project_inputs(folder, folder, "ULS")

    def test_import_states_gravity_cause_and_drops_periods(self):
        data = self._import(9.81)
        self.assertNotIn("rayleigh_tx", data["values"])
        text = " ".join(data["notes"])
        self.assertIn("stale, incomplete, or inconsistent", text)
        self.assertIn("g=9.81", text)
        self.assertIn("9.80665", text)
        self.assertIn("re-run", text)
        self.assertIn("1.25 x empirical", text)

    def test_import_with_current_g_has_no_gravity_note(self):
        data = self._import(9.80665)
        self.assertNotIn("were recorded with g=", " ".join(data["notes"]))
        self.assertAlmostEqual(float(data["values"]["rayleigh_tx"]),
                               _axis_with_g(9.80665)["period_s"])


if __name__ == "__main__":
    unittest.main()
