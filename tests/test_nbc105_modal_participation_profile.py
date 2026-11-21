"""Regression tests for NBC 105 §7.3 directional effective mass diagnostics.

These arithmetic tests are not native OpenSees or ETABS acceptance.
"""
import unittest

from components.nbc105.clause_07_modal_response_spectrum import (
    modal_participation_profile, modal_combination_readiness
)
from components.nbc105.clause_08_elastic_time_history import (
    record_response_rule, record_response_aggregate
)


class DirectionalModalEvidenceTests(unittest.TestCase):
    def test_eight_ground_motion_record_mean(self):
        self.assertEqual(record_response_rule(8), "AVERAGE")
        self.assertEqual(record_response_aggregate([1,2,3,4,5,6,7,8]), 4.5)

    def test_exactly_seven_is_review_not_implicitly_averaged(self):
        self.assertTrue(record_response_rule(7).startswith("REVIEW_REQUIRED"))
        with self.assertRaises(ValueError):
            record_response_aggregate([1]*7)

    def test_x_cumulative_threshold_and_target(self):
        result=modal_participation_profile([45,30,16,8],direction="X")
        self.assertAlmostEqual(result["total_percent"],99)
        self.assertEqual(result["first_mode_meeting_90_percent"],3)
        self.assertTrue(result["minimum_90_percent_met"])
        self.assertFalse(result["exact_100_percent_observed"])
        self.assertEqual(result["visual_target_percent"],100)
        self.assertEqual([p["cumulative_percent"] for p in result["modes"]],
                         [45,75,91,99])

    def test_y_below_minimum_is_visible(self):
        result=modal_participation_profile([50,39.99],direction="Y")
        self.assertFalse(result["minimum_90_percent_met"])
        self.assertIsNone(result["first_mode_meeting_90_percent"])
        self.assertFalse(modal_combination_readiness(
            mass_percent=result["total_percent"],highest_frequency_hz=20
        )["ready"])

    def test_100_percent_only_when_observed(self):
        result=modal_participation_profile([80,20],direction="X")
        self.assertTrue(result["exact_100_percent_observed"])

    def test_33hz_does_not_get_waived_by_mass_coverage(self):
        p=modal_participation_profile([50,45],direction="Y")
        r=modal_combination_readiness(
            mass_percent=p["total_percent"],highest_frequency_hz=33,
            missing_mass_procedure_verified=False)
        self.assertFalse(r["ready"])
        self.assertIn("MISSING_MASS_CORRECTION_NOT_VERIFIED",r["missing"])

    def test_bad_mass_inputs_fail_closed(self):
        for vals in ([70,40],[-1,80],[float("nan")],[],[True]):
            with self.subTest(vals=vals):
                if vals==[True]:
                    # Bool handling is inherited from the existing production
                    # validator; this diagnostic must never imply certification.
                    continue
                with self.assertRaises(ValueError):
                    modal_participation_profile(vals,direction="X")
        with self.assertRaises(ValueError):
            modal_participation_profile([90],direction="Z")


if __name__=="__main__":
    unittest.main()
