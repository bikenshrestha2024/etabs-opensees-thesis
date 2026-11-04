"""Numerical evidence gate tests independent of OpenSeesPy."""
import unittest
from components.nonlinear_time_history.full_record_gate import (
verify_accepted_history,compare_time_step_results)
class GateTests(unittest.TestCase):
    def test_full_record(self):
        r=verify_accepted_history([dict(time_s=0.,drift=0.),
                                   dict(time_s=.005,drift=.01)],.005,.005)
        self.assertTrue(r["full_record_completed"])
        self.assertFalse(r["model_verification_complete"])
    def test_truncated(self):
        r=verify_accepted_history([dict(time_s=0.,drift=0.),dict(time_s=.005,drift=.01)],10.,.005)
        self.assertEqual(r["status"],"TRUNCATED_DIAGNOSTIC")
    def test_bad_time(self):
        with self.assertRaisesRegex(ValueError,"increase strictly"):
            verify_accepted_history([dict(time_s=0.,drift=0.),dict(time_s=0.,drift=.01)],1.,1.)
    def test_nonfinite_channel(self):
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            verify_accepted_history([dict(time_s=0.,drift=0.),
                                     dict(time_s=1.,drift=float("nan"))],1.,1.)
    def test_reject_string_nan_and_inf_from_csv(self):
        for bad in ("NaN", "inf", "-Infinity"):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError,"Nonfinite accepted response"):
                    verify_accepted_history([dict(time_s="0",drift="0"),
                                             dict(time_s="1",drift=bad)],1,1)

    def test_reject_missing_channels_and_text(self):
        with self.assertRaisesRegex(ValueError,"channels"):
            verify_accepted_history([dict(time_s=0,drift=0),
                                     dict(time_s=1)],1,1)
        with self.assertRaisesRegex(ValueError,"Invalid accepted response"):
            verify_accepted_history([dict(time_s=0,drift=0),
                                     dict(time_s=1,drift="FAILED")],1,1)

    def test_timestep_compare_requires_evidence(self):
        fields=dict(status="FULL_DURATION_NUMERIC_SCREEN",
            peak_roof_UX_m=.1,peak_roof_UY_m=.1,
            max_story_drift_X=.01,max_story_drift_Y=.01,
            min_accepted_step_s=.005,max_accepted_step_s=.01)
        with self.assertRaisesRegex(ValueError,"64-digit"):
            compare_time_step_results(dict(fields),dict(fields))
        coarse=dict(fields,model_sha256="a"*64,record_sha256="b"*64)
        fine=dict(coarse,min_accepted_step_s=.0025,max_accepted_step_s=.005)
        result=compare_time_step_results(coarse,fine,max_relative_difference=.05)
        self.assertTrue(result["within_user_supplied_tolerance"])
        with self.assertRaisesRegex(ValueError,"smaller maximum"):
            compare_time_step_results(fine,coarse)
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            compare_time_step_results(coarse,fine,max_relative_difference=-.1)

    def test_reject_different_source(self):
        a=dict(status="FULL_DURATION_NUMERIC_SCREEN",model_sha256="a",record_sha256="r")
        b=dict(a,model_sha256="b")
        with self.assertRaisesRegex(ValueError,"differ"):
            compare_time_step_results(a,b)
if __name__=="__main__":unittest.main()
