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
        r=verify_accepted_history([dict(time_s=0.),dict(time_s=.005)],10.,.005)
        self.assertEqual(r["status"],"TRUNCATED_DIAGNOSTIC")
    def test_bad_time(self):
        with self.assertRaisesRegex(ValueError,"increase strictly"):
            verify_accepted_history([dict(time_s=0.),dict(time_s=0.)],1.,1.)
    def test_nonfinite_channel(self):
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            verify_accepted_history([dict(time_s=0.,drift=0.),
                                     dict(time_s=1.,drift=float("nan"))],1.,1.)
    def test_reject_different_source(self):
        a=dict(status="FULL_DURATION_NUMERIC_SCREEN",model_sha256="a",record_sha256="r")
        b=dict(a,model_sha256="b")
        with self.assertRaisesRegex(ValueError,"differ"):
            compare_time_step_results(a,b)
if __name__=="__main__":unittest.main()
