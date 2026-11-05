"""Deterministic NBC 105 2025 torsion checks, no solver or EDB needed."""
import csv
import tempfile
import unittest
from pathlib import Path
from components.validation.torsion_check import (
    check_floor_end_torsion,check_torsional_irregularity,
)
from torsion_check import run


class TorsionTests(unittest.TestCase):
    def test_code_uses_max_over_min_not_max_over_average(self):
        # 1.6/1.0=1.6 >1.5: Qwen's max/average would give 1.23077
        result=check_floor_end_torsion(.0016,.001)
        self.assertAlmostEqual(result["ratio"],1.6)
        self.assertEqual(result["status"],"TORSIONAL IRREGULARITY")
        self.assertFalse(result["design_acceptance_blocked"])

    def test_extreme_is_strictly_greater_than_2point5(self):
        at_limit=check_floor_end_torsion(.0025,.001)
        self.assertFalse(at_limit["extreme"])
        self.assertTrue(at_limit["torsion"])
        exceed=check_floor_end_torsion(.002501,.001)
        self.assertTrue(exceed["extreme"])
        self.assertTrue(exceed["design_acceptance_blocked"])

    def test_unbounded_and_undefined_not_pass(self):
        self.assertEqual(check_floor_end_torsion(.001,0.)["status"],"UNBOUNDED")
        self.assertEqual(check_floor_end_torsion(0.,0.)["status"],"NOT EVALUATED")
        self.assertTrue(check_floor_end_torsion(0.,0.)["design_acceptance_blocked"])

    def test_missing_center_of_mass_basis_is_not_evaluated(self):
        result=check_floor_end_torsion(.001,.002,centered_cm_load=False)
        self.assertEqual(result["status"],"NOT EVALUATED")

    def test_nonfinite_input_fails_closed(self):
        with self.assertRaises(ValueError):
            check_floor_end_torsion(float("nan"),.001)

    def test_state_and_case_identity(self):
        row={"limit_state":"ULS","case":"X_E0","axis":"X","storey":"25",
             "end_a_m":.001,"end_b_m":.003,
             "centered_cm_load":True,"same_end_basis":True}
        result=check_torsional_irregularity([row])[0]
        self.assertEqual(result["status"],"EXTREME TORSION")
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            check_torsional_irregularity([row,row])
        with self.assertRaisesRegex(ValueError,"ULS/SLS"):
            check_torsional_irregularity([{**row,"limit_state":"BOTH"}])

    def test_cli_creates_auditable_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/"torsion.csv";out=root/"review.csv"
            with source.open("w",encoding="utf-8",newline="") as file:
                writer=csv.DictWriter(file,fieldnames=["limit_state","case","axis",
                    "storey","end_a_m","end_b_m","centered_cm_load","same_end_basis"])
                writer.writeheader()
                writer.writerow(dict(limit_state="SLS",case="Y_E0",axis="Y",storey=10,
                    end_a_m=.002,end_b_m=.001,centered_cm_load="true",same_end_basis="true"))
            result=run(source,out)
            self.assertTrue(out.is_file())
            self.assertEqual(result[0]["status"],"TORSIONAL IRREGULARITY")


if __name__=="__main__":
    unittest.main(verbosity=2)
