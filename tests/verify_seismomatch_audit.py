"""Solver-free source provenance and literal 9.3.2.2 matching-window checks."""
import tempfile
import unittest
from pathlib import Path
from components.nonlinear_time_history.seismomatch_audit import (
    assess_preprocessed_sources,screen_fitting_window)
class SeismoMatchTests(unittest.TestCase):
 def sample(self,folder):
    x=Path(folder)/"a.txt";y=Path(folder)/"b.txt"
    for p in (x,y):
        p.write_text("Time Series matched accelerogram: RSN001.AT2\nTime Step: 0.005 s\nTime(sec) Acc(g)\n0.00 0.0\n0.005 0.001\n")
    return x,y
 def test_already_matched_scale_one(self):
    with tempfile.TemporaryDirectory() as d:
        x,y=self.sample(d)
        result=assess_preprocessed_sources(x,y,open_sees_scale=1,declared_already_matched=True)
        self.assertTrue(result["both_headers_identify_matched_outputs"])
        self.assertFalse(result["independent_seismomatch_scale_factors_verified"])
 def test_no_second_scaling(self):
    with tempfile.TemporaryDirectory() as d:
        x,y=self.sample(d)
        with self.assertRaisesRegex(ValueError,"MUST be 1.0"):
            assess_preprocessed_sources(x,y,open_sees_scale=1.4)
        with self.assertRaisesRegex(ValueError,"declares unscaled"):
            assess_preprocessed_sources(x,y,open_sees_scale=1,declared_already_matched=False)
 def test_window_6_seconds_not_enough_for_long_period(self):
    r=screen_fitting_window(.05,6.,tn90_x_s=.2,tn90_y_s=.25,
      t1_x_s=3.622,t1_y_s=3.0,r_mu=3.5)
    self.assertEqual(r["status"],"FITTING_WINDOW_DOES_NOT_COVER_NBC_INTERVAL")
    self.assertGreater(r["axes"]["x"]["long_period_gap_s"],.7)
    self.assertTrue(r["axes"]["y"]["covered"])
 def test_window_6_enough_with_shorter_t1(self):
    r=screen_fitting_window(.05,6.,tn90_x_s=.2,tn90_y_s=.25,
      t1_x_s=3.0,t1_y_s=3.0,r_mu=3.5)
    self.assertEqual(r["status"],"PERIOD_WINDOW_COVERED")
if __name__=="__main__":unittest.main()
