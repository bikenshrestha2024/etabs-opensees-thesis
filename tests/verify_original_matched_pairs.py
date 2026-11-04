"""Unit test for PEER original parser, no access to source earthquake files."""
import tempfile
import unittest
from pathlib import Path
from tools.verify_original_matched_pairs import parse_original_at2

class OriginalParserTest(unittest.TestCase):
    def test_declared_npts_peak_and_dt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"example.AT2"
            p.write_text("PEER NGA STRONG MOTION DATABASE RECORD\n"
                         "Sample event\nACCELERATION TIME SERIES IN UNITS OF G\n"
                         "NPTS= 4, DT= .0200 SEC,\n"
                         "1.0E-03 -2.0E-03 1.0E-02 -4.0E-03\n",encoding="utf-8")
            result=parse_original_at2(p)
            self.assertEqual(result["npts"],4)
            self.assertAlmostEqual(result["peak_acceleration_g"],.01)
            self.assertAlmostEqual(result["duration_s"],.06)
    def test_disallow_npts_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invalid.AT2"
            p.write_text("PEER NGA\nSample\nACCELERATION TIME SERIES IN UNITS OF G\n"
                         "NPTS= 6, DT= .01 SEC,\n1 2 3\n")
            with self.assertRaisesRegex(ValueError,"Declared NPTS"):
                parse_original_at2(p)
if __name__=="__main__":
    unittest.main()
