"""Synthetic tests only; NOT assertions on actual user accelerograms."""
import csv
import hashlib
import tempfile
import unittest
from pathlib import Path
from tools.verify_matched_waveforms import parse_matched, check_source, audit

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


    def test_malformed_after_header_is_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.txt"
            p.write_text("Time Series matched accelerogram: x\\n"
                         "Time Step: 0.005 s\\nTime(sec) Acc(g)\\n"
                         "0.000 0.0\\n0.005 0.1\\nINVALID ROW OTHER\\n0.010 0.2\\n")
            with self.assertRaisesRegex(ValueError, "Malformed data"):
                parse_matched(p)

    def test_no_nonnumeric_data_drop(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.txt"
            p.write_text("Time Series matched accelerogram: x\\n"
                         "Time Step: 0.005 s\\nTime(sec) Acc(g)\\n"
                         "0.000 0.0\\n0.005 wrong\\n0.010 0.2\\n")
            with self.assertRaisesRegex(ValueError, "Non-numeric"):
                parse_matched(p)

    def test_register_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            reg = root / "register.csv"
            with reg.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=(
                    "event", "component", "source_filename", "matched_sha256",
                    "matched_dt_s", "matched_end_time_s", "matched_pga_g"))
                writer.writeheader()
                for i in range(16):
                    writer.writerow(dict(event="E"+str(i//2),component="A" if i%2==0 else "B",
                        source_filename=("../outside.txt" if i==0 else "safe"+str(i)+".txt"),
                        matched_sha256="0"*64,matched_dt_s="0.005",
                        matched_end_time_s="0.01",matched_pga_g="0.2"))
            with self.assertRaisesRegex(ValueError, "Unsafe source filename"):
                audit(root, reg)

    def test_pair_time_mismatch_requires_review_not_approval(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            reg = root / "register.csv"
            with reg.open("w",newline="",encoding="utf-8") as fh:
                writer=csv.DictWriter(fh,fieldnames=("event","component","source_filename",
                     "matched_sha256","matched_dt_s","matched_end_time_s","matched_pga_g"))
                writer.writeheader()
                for i in range(16):
                    n=3 if i != 15 else 4
                    content=("Time Series matched accelerogram: x\\nTime Step: 0.005 s\\n"
                             "Time(sec) Acc(g)\\n" +
                             "".join(f"{j*.005:.3f} {j*.1:.2f}\\n" for j in range(n)))
                    filename=f"case_{i}.txt"
                    p=root/filename
                    p.write_text(content,encoding="utf-8")
                    writer.writerow(dict(event=f"E{i//2}",component="A" if i%2==0 else "B",
                        source_filename=filename,matched_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                        matched_dt_s="0.005",matched_end_time_s=str((n-1)*.005),
                        matched_pga_g=str((n-1)*.1)))
            result=audit(root,reg)
            self.assertEqual(result["source_discrepancies"],0)
            self.assertEqual(result["pair_synchronization_review_count"],1)
            self.assertEqual(result["status"],"SOURCE_INTEGRITY_PASSED_PAIR_REVIEW_REQUIRED")
            self.assertFalse(result["nbc105_common_lower_factor_verified"])

if __name__ == "__main__":
    unittest.main()
