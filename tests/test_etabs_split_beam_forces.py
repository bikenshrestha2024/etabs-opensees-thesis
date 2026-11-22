"""Synthetic split-workbook importer tests (no proprietary source files)."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from components.validation.etabs_split_beam_forces import consolidate


class SplitBeamForceTests(unittest.TestCase):
    def setUp(self):
        from openpyxl import Workbook
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.headers = ["Story", "Label", "Unique Name", "Output Case",
                        "Station", "P", "V2", "V3", "T", "M2", "M3"]

    def part(self, name, records):
        from openpyxl import Workbook
        path = self.root / name
        wb = Workbook()
        ws = wb.active
        ws.title = "Element Forces - Beams"
        ws.append(["Table: Element Forces - Beams"])
        ws.append(self.headers)
        for record in records:
            ws.append(record)
        wb.save(path)
        return path

    def row(self, story="Story1", unique="123", station=0., shear=5.):
        return [story, "B1", unique, "1. DL + LL", station,
                0., shear, 0., 0., 0., 0.]

    def test_three_beam_force_sheets_in_one_workbook(self):
        from openpyxl import Workbook
        book=Workbook()
        first=book.active; first.title="Element Forces - Beams"
        for i in range(3):
            sheet=first if i==0 else book.create_sheet(
                "Element Forces - Beams "+str(i+1))
            sheet.append(["Table: Element Forces - Beams"])
            sheet.append(self.headers)
            sheet.append(self.row(unique=str(100+i)))
        path=self.root/"all_three_sheets.xlsx"
        book.save(path)
        result=consolidate([path],self.root/"three")
        self.assertEqual(result["source_rows"],3)
        self.assertEqual(result["unique_rows"],3)
        self.assertEqual(len(result["input_files"][0]["sheets"]),3)
        self.assertEqual(
            sum(s["rows_read"] for s in result["input_files"][0]["sheets"]),3)

    def test_multi_workbook_multi_sheet_overlaps_and_late_conflict(self):
        from openpyxl import load_workbook
        first=self.part("first.xlsx",[self.row(unique="101")])
        second=self.part("second.xlsx",[self.row(unique="102")])
        book=load_workbook(second)
        sheet=book.create_sheet("Element Forces - Beams 2")
        sheet.append(self.headers)
        sheet.append(self.row(unique="101"))
        book.save(second)
        result=consolidate([first,second],self.root/"combined")
        self.assertEqual(result["source_rows"],3)
        self.assertEqual(result["unique_rows"],2)
        self.assertEqual(result["exact_or_tolerance_matched_overlaps"],1)
        self.assertEqual(result["output_format"],
                         "CSV_UNLIMITED_EXCEL_WORKSHEET_ROWS")
        book=load_workbook(second)
        sheet=book["Element Forces - Beams 2"]
        sheet["G2"]=999.0
        book.save(second)
        with self.assertRaisesRegex(ValueError,"Conflicting duplicate"):
            consolidate([first,second],self.root/"conflict")
        self.assertFalse((self.root/"conflict").exists())

    def test_overlaps_deduplicated_without_row_loss(self):
        a = self.part("one.xlsx", [self.row(), self.row(station=1.)])
        b = self.part("two.xlsx", [self.row(station=1.),
                                    self.row(story="Story2")])
        report = consolidate([a, b], self.root / "out")
        self.assertEqual(report["source_rows"], 4)
        self.assertEqual(report["unique_rows"], 3)
        self.assertEqual(report["exact_or_tolerance_matched_overlaps"], 1)
        with (self.root / "out" / "ETABS_Beam_Forces_Consolidated.csv").open(
                encoding="utf-8-sig", newline="") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 3)
        self.assertEqual(len(report["input_files"]), 2)
        self.assertTrue(report["input_files"][0]["source_sha256"])

    def test_conflicting_overlap_fails_before_creating_output(self):
        a = self.part("one.xlsx", [self.row(shear=5.)])
        b = self.part("two.xlsx", [self.row(shear=6.)])
        out = self.root / "out"
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate"):
            consolidate([a, b], out)
        self.assertFalse(out.exists())

    def test_wrong_case_fails_closed(self):
        row = self.row()
        row[3] = "1.5(DL+LL)"
        a = self.part("one.xlsx", [row])
        with self.assertRaisesRegex(ValueError, "unexpected Output Case"):
            consolidate([a], self.root / "out")

    def test_nonempty_output_is_never_overwritten(self):
        a = self.part("one.xlsx", [self.row()])
        out = self.root / "out"
        out.mkdir()
        (out / "keep.txt").write_text("original")
        with self.assertRaisesRegex(FileExistsError, "new or empty"):
            consolidate([a], out)
        self.assertEqual((out / "keep.txt").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
