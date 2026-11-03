"""Readiness checks for actual measured FVD data; no synthetic calibration claim."""
import csv
import tempfile
import unittest
from pathlib import Path
from importlib.machinery import SourceFileLoader
SRC=Path(__file__).resolve().parents[1]/"30_CALIBRATE_FVD_FROM_TEST.py"
m=SourceFileLoader("fvd_calibration_cli",str(SRC)).load_module()
class Tests(unittest.TestCase):
    def test_reject_missing_measured_data(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.csv"
            p.write_text("time_s,displacement_m,force_kN\n")
            with self.assertRaisesRegex(ValueError,"40"):
                m.read_experiment(p)
    def test_nonfinite_data_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.csv"
            with p.open("w",newline="") as f:
                w=csv.writer(f);w.writerow(["time_s","displacement_m","force_kN"])
                for i in range(40):
                    w.writerow([i*.01,i*.001,float("nan") if i==10 else i])
            with self.assertRaisesRegex(ValueError,"Nonfinite"):
                m.read_experiment(p)
    def test_valid_csv_data_reads(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.csv"
            with p.open("w",newline="") as f:
                w=csv.writer(f);w.writerow(["time_s","displacement_m","force_kN"])
                for i in range(40):
                    w.writerow([i*.01,i*.001,i*.1])
            self.assertEqual(len(m.read_experiment(p)["time_s"]),40)
if __name__=="__main__":
    unittest.main()
