"""Owner ruling 8: every cross-reference printed in NBC 105:2025 is classified. Unit tests only."""
import importlib.util
import os
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("crossref", ROOT / "tools" / "nbc105_crossref_audit.py")
A = importlib.util.module_from_spec(spec)
sys.modules["crossref"] = A
spec.loader.exec_module(A)

PDF_CANDIDATES = [os.environ.get("NBC105_PDF", ""),
                  "/mnt/user-data/uploads/3aaf535f-NBC_105_2025_Seismic_Design_of_Buildings_in_Nepal_lqqvx6a_2.pdf"]


def _pdf():
    for c in PDF_CANDIDATES:
        if c and Path(c).exists() and shutil.which("pdftotext"):
            return c
    return None


class Classification(unittest.TestCase):
    def setUp(self):
        self.rows = A.read_crossrefs()

    def test_no_row_is_unclassified_and_csv_is_consistent(self):
        self.assertEqual(A.check_rows(self.rows), [])

    def test_known_misdirected_references(self):
        mis = {(r["printed_page"], r["target"]): r["correct_target"] for r in self.rows
               if r["classification"] == A.CLASS_MISDIRECTED}
        self.assertEqual(mis[("43", "5.6")], "5.5.3")
        self.assertEqual(mis[("48", "5.6")], "5.5.3")
        self.assertEqual(mis[("15", "5.6")], "5.5.1")
        self.assertEqual(mis[("26", "Figure 4-4")], "Figure 4-3")
        self.assertEqual(mis[("22", "Figure 4-1")], "Figure 4-2")

    def test_ambiguous_names_both_targets(self):
        amb = [r for r in self.rows if r["classification"] == A.CLASS_AMBIGUOUS]
        self.assertTrue(amb)
        self.assertTrue(all(";" in r["correct_target"] for r in amb))

    def test_unclassified_row_is_detected(self):
        fake = dict(self.rows[0], ref_id="XR-9999", classification=A.UNCLASSIFIED)
        self.assertIn("XR-9999", " ".join(A.check_rows(self.rows + [fake])))
        extra = dict(pdf_page=999, target="9.9", line_sha256="0" * 64)
        self.assertEqual(A.unclassified_references([extra], self.rows), [extra])

    def test_misdirected_without_corrected_citation_fails(self):
        bad = [dict(r) for r in self.rows]
        for r in bad:
            if r["classification"] == A.CLASS_MISDIRECTED:
                r["corrected_citation"] = ""
                break
        self.assertTrue(A.check_rows(bad))


class CodeAndDocsCiteCorrectedClause(unittest.TestCase):
    def test_corrected_citations_present_in_named_files(self):
        # check_rows verifies every citation_files entry contains corrected_citation
        problems = [p for p in A.check_rows(A.read_crossrefs()) if "does not cite" in p]
        self.assertEqual(problems, [])

    def test_no_stale_5_6_drift_citation(self):
        self.assertEqual(A.stale_citation_scan(), [])

    def test_scan_catches_stale_text(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "components").mkdir()
            (root / "components" / "x.py").write_text("# drift limits per clause 5.6\n", encoding="utf-8")
            old = A.ROOT
            A.ROOT = root
            try:
                self.assertEqual(A.stale_citation_scan(roots=("components",)), ["components/x.py:1"])
            finally:
                A.ROOT = old


@unittest.skipUnless(_pdf(), "NBC 105 PDF or pdftotext not available")
class AgainstPdf(unittest.TestCase):
    def test_every_printed_reference_is_classified(self):
        refs = A.extract_from_pdf(_pdf())
        self.assertEqual(A.unclassified_references(refs, A.read_crossrefs()), [])
        self.assertEqual(len(refs), len(A.read_crossrefs()))


if __name__ == "__main__":
    unittest.main()
