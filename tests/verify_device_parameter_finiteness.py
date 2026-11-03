"""Regression tests for finite physical device parameters.

These tests exercise Python guards with a recording fake; they do not check native
OpenSees element convergence, device energy dissipation or experimental calibration.
References:
  OpenSees ViscousDamper material command:
  https://opensees.berkeley.edu/wiki/index.php/ViscousDamper_Material
  OpenSees Steel02:
  https://opensees.github.io/OpenSeesDocumentation/user/manual/material/uniaxialMaterials/Steel02.html
"""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from components.sections.devices import (
    add_brb_corot_truss, define_brb_core_material, define_fvd_material,
    convert_fvd_cd_mm_to_m, summarize_fvd_history, brb_cumulative_plastic_ductility,
)

class RecordingOpenSees:
    def __init__(self):
        self.calls = []
    def uniaxialMaterial(self, *args):
        self.calls.append(("uniaxialMaterial", args))
    def element(self, *args):
        self.calls.append(("element", args))

class DeviceNumericalGuards(unittest.TestCase):
    def test_reject_nonfinite_fvd_inputs_without_native_calls(self):
        for key in ("K", "Cd", "alpha", "gap_length"):
            for invalid in (float("nan"), float("inf"), float("-inf")):
                args = dict(material_tag=1, K=1000.0, Cd=500.0,
                            alpha=0.3, gap_length=0.0)
                args[key] = invalid
                ops = RecordingOpenSees()
                with self.subTest(key=key, invalid=str(invalid)):
                    with self.assertRaisesRegex(ValueError, "finite"):
                        define_fvd_material(ops, **args)
                    self.assertEqual(ops.calls, [])

    def test_reject_nonfinite_brb_core_area(self):
        for area in (float("nan"), float("inf"), float("-inf")):
            ops = RecordingOpenSees()
            with self.subTest(area=str(area)):
                with self.assertRaisesRegex(ValueError, "finite"):
                    add_brb_corot_truss(
                        ops, element_tag=3, i_node=1, j_node=2,
                        core_area=area, material_tag=4)
                self.assertEqual(ops.calls, [])

    def test_allow_finite_positive_fvd_values(self):
        ops = RecordingOpenSees()
        result = define_fvd_material(ops, material_tag=8, K=30000.0,
                                     Cd=500.0, alpha=0.3)
        self.assertEqual(result["material_tag"], 8)
        self.assertEqual(len(ops.calls), 1)
        self.assertFalse(result.get("calibrated", False))

    def test_allow_finite_positive_core_area(self):
        ops = RecordingOpenSees()
        result = add_brb_corot_truss(ops, element_tag=5,
                    i_node=1, j_node=2, core_area=0.0025, material_tag=6)
        self.assertEqual(result["core_area"], 0.0025)
        self.assertEqual(len(ops.calls), 1)

    def test_reject_nonfinite_steel02_parameters(self):
        ops = RecordingOpenSees()
        args = dict(material_tag=1, Fy=345000.0, E0=200000000.0,
                    b=0.01, R0=20.0, cR1=0.925, cR2=0.15,
                    a1=0.0, a2=1.0, a3=0.0, a4=1.0)
        for key in ("Fy", "E0", "R0", "a1"):
            with self.subTest(key=key):
                bad = dict(args)
                bad[key] = float("nan")
                with self.assertRaises(ValueError):
                    define_brb_core_material(ops, **bad)
        self.assertEqual(ops.calls, [])

class DeviceDemandHistoryChecks(unittest.TestCase):
    def test_fvd_coefficient_conversion(self):
        self.assertAlmostEqual(convert_fvd_cd_mm_to_m(700.0, 0.3),
                               700.0 * 1000.0**0.3, places=9)
        with self.assertRaisesRegex(ValueError, "finite"):
            convert_fvd_cd_mm_to_m(float("nan"), 0.3)

    def test_fvd_work_unit_and_signed_status(self):
        # Two points: resisting force -10 kN, positive 0.1 m/s for 1 s.
        result = summarize_fvd_history([0, 1], [0, 0.1], [0.1, 0.1], [-10, -10])
        self.assertAlmostEqual(result["signed_force_velocity_work_kN_m"], -1.0)
        self.assertEqual(result["qualification_status"], "NOT_ESTABLISHED")

    def test_reject_unsorted_or_invalid_time_history(self):
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            summarize_fvd_history([0, 0], [0, 0.1], [0.1, 0.1], [1, 1])
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            summarize_fvd_history([0, 1], [0, 0.1], [float("nan"), 0.1], [1, 1])

    def test_brb_uses_actual_plastic_history(self):
        self.assertAlmostEqual(
            brb_cumulative_plastic_ductility([0, 0.01, -0.01, 0], 0.005),8.0)
        with self.assertRaisesRegex(ValueError,"finite"):
            brb_cumulative_plastic_ductility([0,float("nan")],0.005)


if __name__ == "__main__":
    unittest.main()
