"""Readiness checks for actual measured FVD data; no synthetic calibration claim."""
import csv
import tempfile
import unittest
from pathlib import Path
from importlib.machinery import SourceFileLoader
from unittest.mock import patch
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
    def test_outputs_cannot_replace_measured_data(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            measured="time_s,displacement_m,force_kN\n"+"".join(f"{i},{i},{i}\n" for i in range(40))
            fitted=dict(status="MEASURED_DATA_FITTED_NOT_INDEPENDENTLY_VALIDATED",
                        fitted_series=[0.0]*40)
            for name in ("FVD_Measured_vs_Maxwell.csv","FVD_Calibration_Report.json"):
                with self.subTest(name=name),patch.object(m,"fit_measured_fvd",return_value=fitted):
                    source=root/name
                    source.write_text(measured,encoding="utf-8")
                    with self.assertRaisesRegex(ValueError,"overwrite input"):
                        m.main([str(source),"--output",str(root)])
                    self.assertEqual(source.read_text(encoding="utf-8"),measured)
if __name__=="__main__":
    unittest.main()
