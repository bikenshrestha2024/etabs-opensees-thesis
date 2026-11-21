"""Saved Rayleigh results made with a g that differs from the constant are rejected with a stated cause.

NBC 105 gravity is 9.81 (printed p. 7); the superseded 9.80665 is recognised
only to reject old results. Unit tests only, no ETABS/OpenSees. Tolerance and
solver numerics are unchanged.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.project_workbooks import import_project_inputs
from components.nbc105.constants import GRAVITY_M_S2, SUPERSEDED_GRAVITY_M_S2
from components.modal.rayleigh import (
    RAYLEIGH_DISPLACEMENT_BASIS, RAYLEIGH_METHOD_VERSION, empirical_esm_reference,
    rayleigh_result_prefix,
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
    def test_axis_recorded_with_superseded_g_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            verify_saved_rayleigh_axis(_axis_with_g(SUPERSEDED_GRAVITY_M_S2))
        self.assertIn("mismatch", str(ctx.exception))
        verify_saved_rayleigh_axis(_axis_with_g(GRAVITY_M_S2))  # current g accepted

    def _import(self, g):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder = Path(tmp.name)
        (folder / "OpenSees_Complete_Model_Data_V118.json").write_text("{}", encoding="utf-8")
        (folder / "OpenSees_Complete_Model_Config_V118.json").write_text("{}", encoding="utf-8")
        axis = _axis_with_g(g)
        rows = axis["rows"]
        source_rows = [
            {"height_m": 3.0 * (i + 1), "dead_load_kN": row["weight_kN"],
             "storage_live_load_kN": 0.0, "other_live_load_kN": 0.0,
             "master_node_tag": row["master_node"]}
            for i, row in enumerate(rows)
        ]
        import csv
        ledger = folder / "NBC105_ESM_Story_Weights_Assembled_V118.csv"
        with ledger.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(source_rows[0]))
            writer.writeheader()
            writer.writerows(source_rows)
        height = source_rows[-1]["height_m"]
        settings = dict(soil_type="C", zoning_factor_z=.35, importance_factor_i=1.)
        empirical, proof, forces = empirical_esm_reference(
            source_rows, height_m=height, aw_m2=10., state="ULS", settings=settings)
        for source, row, force in zip(source_rows, rows, forces, strict=True):
            row.update(height_m=source["height_m"], force_kN=force)
        rec = verify_rayleigh_sum(rows, g=g)
        axis.update(period_s=rec["period_s"], rayleigh_numerator_kN_m2=rec["numerator_kN_m2"],
                    rayleigh_denominator_gFiDi_kN_m2_s2=rec["denominator_kN_m2_s2"],
                    empirical_period_s=empirical, amplified_empirical_s=proof["period_s"],
                    adopted_period_s=min(rec["period_s"], proof["period_s"]),
                    reference_force_exponent_k=proof["period_exponent_k"],
                    reference_force_total_kN=proof["base_shear_kN"],
                    empirical_esm_reference=proof)
        axis["kinematic_audit"]["incremental_base_reaction_kN"] = -proof["base_shear_kN"]
        self.expected_period = rec["period_s"]
        result = {
            "model_config_sha256": _sha(folder / "OpenSees_Complete_Model_Config_V118.json"),
            "method_version": RAYLEIGH_METHOD_VERSION,
            "displacement_basis": RAYLEIGH_DISPLACEMENT_BASIS,
            "limit_state": "ULS",
            "model_sha256": _sha(folder / "OpenSees_Complete_Model_Data_V118.json"),
            "story_weights_sha256": _sha(folder / "NBC105_ESM_Story_Weights_Assembled_V118.csv"),
            "gravity_acceleration_m_s2": g,
            "height_m": height,
            "empirical_esm_settings": settings,
            "X": axis, "Y": json.loads(json.dumps(axis)),
        }
        out = analysis_output_folder(folder, "ULS")
        Path(out).mkdir(parents=True, exist_ok=True)
        (Path(out) / (rayleigh_result_prefix("ULS") + ".json")).write_text(
            json.dumps(result), encoding="utf-8")
        return import_project_inputs(folder, folder, "ULS")

    def test_import_states_gravity_cause_and_drops_periods(self):
        data = self._import(SUPERSEDED_GRAVITY_M_S2)
        self.assertNotIn("rayleigh_tx", data["values"])
        text = " ".join(data["notes"])
        self.assertIn("stale, incomplete, or inconsistent", text)
        self.assertIn("g=9.80665", text)  # the recorded value
        self.assertIn("this release uses g=9.81", text)
        self.assertIn("printed p. 7", text)
        self.assertIn("re-run", text)

    def test_import_with_current_g_has_no_gravity_note(self):
        data = self._import(GRAVITY_M_S2)
        self.assertNotIn("were recorded with g=", " ".join(data["notes"]))
        self.assertAlmostEqual(float(data["values"]["rayleigh_tx"]),
                               self.expected_period)


if __name__ == "__main__":
    unittest.main()
