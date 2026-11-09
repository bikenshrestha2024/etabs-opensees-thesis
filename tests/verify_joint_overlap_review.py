"""Check separate wall/column junction weights without applying trial deductions.

[REF docs/source/components/gravity/joint_overlap_review.py.md]
"""
import tempfile
import unittest
from pathlib import Path
from components.gravity.joint_overlap_review import (
    USER_HYPOTHESIS, review_joint_overlap)


class JointTypeReviewTests(unittest.TestCase):
    def setUp(self):
        self.work=tempfile.TemporaryDirectory()
        self.addCleanup(self.work.cleanup)
        self.output=Path(self.work.name)
        self.ledger={
            "schema":"joint-volume-ownership-v1",
            "policy":"AUDIT_ONLY","geometry_verified":False,
            "potentially_duplicated_RCC_weight_kN":5.,
            "rows":[
                dict(kind="frame",index=0,object="C-1",category="COLUMN",
                     gross_weight_kN=24.2,removed_weight_kN=0.,net_weight_kN=24.2,
                     unit_weight_kN_m3=25.,retained_ratio=1.),
                dict(kind="shell",index=0,object="W-1",category="SHEAR WALL",
                     gross_weight_kN=7.2,removed_weight_kN=5.,net_weight_kN=2.2,
                     unit_weight_kN_m3=25.,retained_ratio=2.2/7.2,
                     overlap_with_COLUMN_m3=.2),
            ]
        }

    def test_project_junction_arithmetic_and_one_union(self):
        result=review_joint_overlap(self.ledger,self.output,
                                   beam_offset_candidate_kN=8652.444,
                                   observed_global_gap_kN=8680.475)
        self.assertEqual(result["arithmetic_check"][
            "subtraction_result_32_minus_8_minus_2_minus_4"],18)
        self.assertAlmostEqual(result["arithmetic_check"][
            "assumed_column_joint_kN_each"],24.2)
        self.assertAlmostEqual(result["arithmetic_check"][
            "assumed_wall_joint_kN_each"],7.2)
        self.assertAlmostEqual(result["alternative_joint_estimates"][0][
            "assumed_overlap_weight_kN"],13410.)
        self.assertAlmostEqual(result["alternative_joint_estimates"][1][
            "assumed_overlap_weight_kN"],11710.)
        self.assertAlmostEqual(result["alternative_joint_estimates"][2][
            "assumed_overlap_weight_kN"],2520.)
        self.assertEqual(result["actual_ledger_global_overlap_kN"],5.)
        self.assertEqual(result["owner_relationship_overlap_kN"][
            "SHEAR WALL_OVERLAPS_COLUMN"],5.)
        self.assertTrue((self.output/"Gravity_Joint_Type_Overlap_Review.xlsx").is_file())
        self.assertTrue((self.output/"Gravity_Joint_Type_Overlap_Solids.csv").is_file())
        self.assertEqual(result["interpretation"],"AUDIT ONLY, not an ETABS mass/weight convention match")

    def test_rejects_wrong_union_or_double_classification(self):
        bad=dict(self.ledger,potentially_duplicated_RCC_weight_kN=10.)
        with self.assertRaisesRegex(ValueError,"Ledger total overlap"):
            review_joint_overlap(bad,self.output)

    def test_missing_actual_ledger_is_not_replaced_with_guessed_counts(self):
        with self.assertRaisesRegex(ValueError,"Actual RCC geometric"):
            review_joint_overlap({},self.output)
    def test_impossible_joint_counts_block(self):
        with self.assertRaisesRegex(ValueError,"Excluded junction"):
            review_joint_overlap(self.ledger,self.output,
                hypothesis=dict(candidate_points_per_level=1))
if __name__=="__main__":
    unittest.main()
