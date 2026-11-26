"""Owner ruling 10: Annex C Table C-1 project rows (printed p.106) and hash discipline."""
import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from components.nbc105 import annex_c_zoning as C
from components.nbc105.clause_04_seismic_hazard import validate_zoning_factor


class AnnexC(unittest.TestCase):
    def test_project_value_reproduces_z_0_35(self):
        r = C.project_zoning_factor()
        self.assertEqual((r["z"], r["sn"], r["printed_page"]), (0.35, 346, 106))
        self.assertFalse(r["figure_4_3_used"])
        self.assertEqual(validate_zoning_factor(r["z"]), 0.35)

    def test_column_alignment_rows(self):
        data = C.load_table_c1_project_rows()
        rows = data["rows"]
        self.assertEqual(data["header"]["source_text"], "SN District Local Units PGA")
        self.assertEqual(float(rows[335]["value"]), 0.3)      # Kaski Annapurna
        self.assertEqual(float(rows[326]["value"]), 0.4)      # Kapilbastu Bijayanagar
        for sn in range(340, 351):                            # complete Kathmandu district block
            self.assertEqual(rows[sn]["district"], "Kathmandu")
            self.assertEqual(float(rows[sn]["value"]), 0.35)
        self.assertEqual(rows[346]["local_unit"], "Kirtipur Nagarpalika")
        self.assertEqual(len([r for r in data["scope"] if r["role"] == "EXTERNAL_DATA_REQUIRED"]), 1)
        self.assertEqual(data["figure_usage"][0]["role"], "FIGURE_4_3_NOT_USED_BY_PROJECT")

    def test_untranscribed_rows_are_external_data(self):
        with self.assertRaises(C.TableC1DataRequired):
            C.table_c1_value("Achham", "Mangalsen Nagarpalika")
        self.assertEqual(C.table_c1_value("kathmandu", "  Kirtipur   Nagarpalika ")["z"], 0.35)

    def test_hash_discipline_detects_tampering(self):
        tmp = Path(tempfile.mkdtemp()) / "t.csv"
        shutil.copy(C.TABLE_C1_CSV, tmp)
        text = tmp.read_text(encoding="utf-8").replace("346,Kathmandu,Kirtipur Nagarpalika,PGA,0.35", "346,Kathmandu,Kirtipur Nagarpalika,PGA,0.30")
        tmp.write_text(text, encoding="utf-8")
        with self.assertRaises(C.TableC1IntegrityError):
            C.load_table_c1_project_rows(tmp)

    def test_value_outside_printed_set_rejected(self):
        tmp = Path(tempfile.mkdtemp()) / "t.csv"
        rows = list(csv.DictReader(open(C.TABLE_C1_CSV, encoding="utf-8", newline="")))
        import hashlib
        for r in rows:
            if r["sn"] == "346":
                r["value"] = "0.33"
                r["source_text"] = "346 Kathmandu Kirtipur Nagarpalika 0.33"
                r["sha256"] = hashlib.sha256(r["source_text"].encode()).hexdigest()
        with open(tmp, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
            w.writeheader(); w.writerows(rows)
        with self.assertRaises(C.TableC1IntegrityError):
            C.load_table_c1_project_rows(tmp)

    def test_page_text_cross_check_when_pdf_text_available(self):
        # printed row text must equal what the PDF text layer shows (optional, skipped without the PDF)
        import glob, subprocess
        pdfs = glob.glob("/mnt/user-data/uploads/*NBC_105_2025*.pdf")
        if not pdfs:
            self.skipTest("standard PDF not available")
        text = subprocess.run(["pdftotext", "-layout", "-f", "129", "-l", "129", pdfs[0], "-"], capture_output=True, text=True).stdout
        import re
        flat = re.sub(r"\s+", " ", text)
        self.assertIn("346 Kathmandu Kirtipur Nagarpalika 0.35", flat)


if __name__ == "__main__":
    unittest.main()
