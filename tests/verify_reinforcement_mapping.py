"""Approved ETABS-equivalent bar register smoke checks; no EDB access or solver."""
import csv
import tempfile
import unittest
from pathlib import Path
from components.model.reinforcement_mapping import (read_approved_frame_register,
                                                    apply_approved_frame_register)
TEMPLATE={"RC_COLUMN_1100x1100_FIBER":{"width_mm":1100.0,"depth_mm":1100.0,
                                        "bars_per_side":4,"cover_mm":40.0}}
COLUMNS=["section_key","width_mm","depth_mm","cover_mm","bar_diameter_mm",
         "bars_per_side","tie_diameter_mm","tie_spacing_mm","source_file_sha256",
         "reviewed_by","review_status"]
def row():
    return dict(section_key="RC_COLUMN_1100x1100_FIBER",width_mm="1100",
                depth_mm="1100",cover_mm="40",bar_diameter_mm="25",
                bars_per_side="8",tie_diameter_mm="12",tie_spacing_mm="100",
                source_file_sha256="1"*64,reviewed_by="Engineer",
                review_status="APPROVED_FROM_ETABS_DRAWINGS")
class RegisterTests(unittest.TestCase):
    def load(self, r):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"register.csv"
            with p.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=COLUMNS);w.writeheader();w.writerow(r)
            return read_approved_frame_register(p,TEMPLATE)
    def test_valid_evidence(self):
        data=self.load(row())
        adopted=apply_approved_frame_register(TEMPLATE,data)
        self.assertEqual(adopted["RC_COLUMN_1100x1100_FIBER"]["bars_per_side"],8)
        self.assertEqual(TEMPLATE["RC_COLUMN_1100x1100_FIBER"]["bars_per_side"],4)
        self.assertNotIn("tie_spacing_mm",adopted["RC_COLUMN_1100x1100_FIBER"])
    def test_reject_unapproved(self):
        r=row();r["review_status"]="UNVERIFIED"
        with self.assertRaisesRegex(ValueError,"not independently approved"):self.load(r)
    def test_reject_wrong_geometry(self):
        r=row();r["width_mm"]="1200"
        with self.assertRaisesRegex(ValueError,"differs"):self.load(r)
    def test_reject_nonfinite(self):
        r=row();r["cover_mm"]="nan"
        with self.assertRaisesRegex(ValueError,"finite"):self.load(r)
if __name__=="__main__":unittest.main()
