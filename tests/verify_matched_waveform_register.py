"""Synthetic tests only; NOT assertions on actual user accelerograms."""
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.verify_matched_waveforms import parse_matched, check_source

class WaveformTests(unittest.TestCase):
    def test_parse_declared_g_and_timing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "test.txt"
            p.write_text("Time Series matched accelerogram: example.AT2\n"
                         "Time Step: 0.005 s\nTime(sec) Acc(g)\n"
                         "0.000 0.0\n0.005 -0.1\n0.010 0.3\n",
                         encoding="utf-8")
            result = parse_matched(p)
            self.assertEqual(result["samples"], 3)
            self.assertAlmostEqual(result["max_abs_acceleration_g"], 0.3)
            row = {
                "matched_sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                "matched_dt_s": "0.005", "matched_end_time_s": "0.010",
                "matched_pga_g": "0.3", "event": "Example", "component": "A"}
            self.assertEqual(check_source(p, row)["status"], "SOURCE_REGISTER_MATCH")
            row["matched_sha256"] = "0" * 64
            self.assertIn("SHA256_MISMATCH", check_source(p, row)["errors"])
    def test_reject_wrong_units(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "not_g.txt"
            p.write_text("Time Series matched accelerogram: x\nTime Step: 0.01 s\n"
                         "Time(sec) Acc(m/s2)\n0.00 0\n0.01 1\n0.02 0\n")
            with self.assertRaisesRegex(ValueError, "units"):
                parse_matched(p)
    def test_nonuniform_dt(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "uneven.txt"
            p.write_text("Time Series matched accelerogram: x\nTime Step: 0.01 s\n"
                         "Time(sec) Acc(g)\n0.00 0\n0.01 1\n0.035 0\n")
            with self.assertRaisesRegex(ValueError, "Nonuniform"):
                parse_matched(p)

if __name__ == "__main__":
    unittest.main()
