"""Saved X/Y Rayleigh evidence tests; synthetic only, no native solver claim."""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from components.modal.rayleigh_xy_evidence import audit_rayleigh_pair,write_audit


def case():
    # W=981kN gives m=100kN*s²/m; F=400*.05=20kN
    # T=2pi sqrt(100/400)=pi seconds.
    reference=[{"master":1,"weight_kN":981.0,"force_kN":20.,
                "baseline_m":.01,"loaded_m":.06}]
    double=[{"master":1,"weight_kN":981.,"force_kN":40.,
             "baseline_m":.01,"loaded_m":.11}]
    return {"source":{"edb_sha256":"a"*64,"assembled_model_sha256":"b"*64,
            "story_ledger_sha256":"c"*64,"limit_state":"ULS",
            "gravity_equilibrated":True,"torsion_suppressed":True,
            "displacement_basis":"PHYSICAL_FLOOR_COM","unit":"kN_m_s"},
            "X":{"reference":reference,"perturbed":double,
                 "etabs_period_s":math.pi},
            "Y":{"reference":copy.deepcopy(reference),
                 "perturbed":copy.deepcopy(double),
                 "etabs_period_s":math.pi}}


class RayleighXYEvidenceTests(unittest.TestCase):
    def test_both_axes_analytical_period_and_amplitude(self):
        result=audit_rayleigh_pair(case())
        self.assertIn("NOT_NATIVE_ACCEPTANCE",result["status"])
        for axis in ("X","Y"):
            value=result["directions"][axis]
            self.assertAlmostEqual(value["rayleigh_period_s"],math.pi,places=10)
            self.assertAlmostEqual(value["comparison"]["difference_percent"],0,places=9)
            self.assertTrue(value["amplitude_check"]["diagnostic_linear_scaling_pass"])
            self.assertAlmostEqual(value["amplitude_check"]["force_ratio"],2)
            self.assertEqual(value["floor_count"],1)

    def test_wrong_shape_produces_failed_diagnostic_not_pass(self):
        d=case()
        d["X"]["perturbed"][0]["loaded_m"]=.09
        result=audit_rayleigh_pair(d)
        self.assertFalse(result["directions"]["X"]["amplitude_check"][
            "diagnostic_linear_scaling_pass"])

    def test_perturbation_requires_two_distinct_solved_amplitudes(self):
        d=case()
        d["X"]["perturbed"][0]["force_kN"]=20.
        with self.assertRaisesRegex(ValueError,"different force amplitude"):
            audit_rayleigh_pair(d)

    def test_fail_closed_on_missing_axis_and_wrong_com_basis(self):
        d=case();d.pop("Y")
        with self.assertRaisesRegex(ValueError,"Both X and Y"):
            audit_rayleigh_pair(d)
        d=case();d["source"]["displacement_basis"]="DIAPHRAGM_MASTER"
        with self.assertRaisesRegex(ValueError,"physical floor"):
            audit_rayleigh_pair(d)

    def test_fail_closed_on_unverified_gravity_and_hash(self):
        for field,value in (("gravity_equilibrated",False),
                            ("torsion_suppressed",False),
                            ("edb_sha256","pretend")):
            d=case();d["source"][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                audit_rayleigh_pair(d)

    def test_reject_bad_ledger_or_nonfinite_displacement(self):
        d=case();d["X"]["perturbed"][0]["master"]=2
        with self.assertRaisesRegex(ValueError,"changed floor ledger"):
            audit_rayleigh_pair(d)
        d=case();d["Y"]["reference"][0]["loaded_m"]=float("nan")
        with self.assertRaises(ValueError):
            audit_rayleigh_pair(d)

    def test_durable_audit_includes_saved_input_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path=Path(tmp)/"case.json"
            input_path.write_text(json.dumps(case()),encoding="utf-8")
            result=write_audit(input_path,Path(tmp)/"out")
            self.assertEqual(len(result["saved_source_sha256"]),64)
            self.assertTrue((Path(tmp)/"out"/"Rayleigh_XY_Independent_Evidence.json").exists())


if __name__=="__main__":
    unittest.main()
