"""Deterministic test of tools/verify_nbc105_source_pdf.py.

[REF NBC105-2025 Tables 3-1, 4-1, 5-1, 5-2, 6-1] The fixture holds only the
printed numeric rows (facts), laid out like ``pdftotext -layout`` output, not
the standard's prose. It proves the parser reads each table and that an
altered printed value is reported as MISMATCH instead of passing silently.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import verify_nbc105_source_pdf as v  # noqa: E402

T52 = [(4, 1.5, 1.25)] * 5 + [(3, 1.3, 1.15)] * 2 + [(4, 1.5, 1.25),
      (3, 1.3, 1.15), (3, 1.3, 1.15), (2.5, 1.2, 1.1), (2.5, 1.2, 1.1),
      (2, 1.2, 1.1), (4, 1.5, 1.25), (4, 1.5, 1.25), (3.5, 1.4, 1.2),
      (3.5, 1.4, 1.2), (4, 1.5, 1.25), (3.5, 1.4, 1.2), (3.5, 1.4, 1.2),
      (2.5, 1.2, 1.1)]


def fixture(beam_uls="0.35", rows=T52):
    t52 = "\n".join(f"  {i}  System {i}   {r[0]:g}   {r[1]:g}   {r[2]:g}"
                    for i, r in enumerate(rows, 1))
    return f"""
Table 3-1 Effective stiffness of different components
   1     Beam      {beam_uls} Ec Ig   0.70 Ec Ig
   2   Columns     0.70 Ec Ig   0.90 Ec Ig
   3  Wall—cracked  0.50 Ec Ig  0.70 Ec Ig
   4  Wall—uncracked 0.80 Ec Ig 0.90 Ec Ig
   5  Masonry Wall  0.45 Ec Ig  0.6 Ec Ig
   6  Flat Slabs  0.25 Ec Ig  0.50 Ec Ig
3.5 DESIGN METHODS
Table 4-1 Ta, Tc, TD
  Ta   0.1  0.1  0.1  0.5
  Tc   0.5  0.7  1.0  2.0
  Td   4.0  4.0  4.0  5.0
  α    2.5  2.5  2.5  2.25
4.1.3 Site Subsoil
increased by a factor of 1.25. 
Table 5-1: Live Load Categories and Factors
   Storage     0.60
   For Other Purpose   0.30
   Roof   Nil
5.3 SELECTION
Table 5-2: Ductility and Overstrength Factors
{t52}
5.4 STRUCTURAL IRREGULARITY
0.025 at ultimate limit state
0.006 at serviceability limit state
Linear viscous damping shall not exceed 5%.
between 0.33 and 3. Where a selected ground motion
T1/100 Tn 0.01s
Table 6-1: Deflection Scale Factors
   1    1.0
   2    0.97
   3    0.94
   4    0.91
   5    0.88
   6 or more    0.85
7   Modal Response Spectrum Method
"""


class SourcePdfVerifier(unittest.TestCase):
    def run_on(self, text, tmp):
        p = Path(tmp) / "x.txt"
        p.write_text(text, encoding="utf-8")
        return v.run(p)

    def test_printed_values_all_match_code(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            r = self.run_on(fixture(), d)
        self.assertEqual(r["failures"], [], r["failures"])
        self.assertEqual(r["status"], "ALL_PRINTED_ITEMS_MATCH")
        self.assertEqual(r["checked"], 48)
        self.assertEqual(len(r["source"]["sha256"]), 64)

    def test_altered_printed_value_is_reported(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            r = self.run_on(fixture(beam_uls="0.40"), d)
        self.assertEqual([f["item"] for f in r["failures"]], ["table_3_1.beam"])
        self.assertEqual(r["failures"][0]["status"], "MISMATCH")

    def test_missing_table_is_parse_miss_not_pass(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            r = self.run_on(fixture().replace("Table 6-1", "Table 6-X"), d)
        self.assertTrue(any(f["status"] == "PARSE_MISS" for f in r["failures"]))
        self.assertEqual(r["status"], "DISCREPANCIES_FOUND")


if __name__ == "__main__":
    unittest.main()
