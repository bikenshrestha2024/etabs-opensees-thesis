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

    def test_non_beam_force_sheet_with_same_columns_is_excluded(self):
        from openpyxl import load_workbook
        source=self.part("mixed.xlsx",[self.row(unique="BEAM")])
        book=load_workbook(source)
        other=book.create_sheet("Element Forces - Columns")
        other.append(self.headers)
        other.append(self.row(unique="COLUMN"))
        book.save(source)
        result=consolidate([source],self.root/"beam_only")
        self.assertEqual(result["source_rows"],1)
        self.assertEqual(result["unique_rows"],1)
        self.assertEqual(len(result["input_files"][0]["sheets"]),1)

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

    def test_native_unit_row_is_not_a_result(self):
        from openpyxl import Workbook
        path = self.root / "native.xlsx"
        book = Workbook()
        sheet = book.active
        sheet.title = "Element Forces - Beams"
        sheet.append(["TABLE: Element Forces - Beams"])
        sheet.append(["Story", "Beam", "Unique Name", "Output Case", "Case Type",
                      "Step Type", "Step Number", "Station", "P", "V2", "V3",
                      "T", "M2", "M3", "Element", "Elem Station", "Location"])
        sheet.append(["", "", "", "", "", "", None, "m", "kN", "kN",
                      "kN", "kN-m", "kN-m", "kN-m", "", "m", ""])
        sheet.append(["Story1", "B1", "123", "1. DL + LL", "Combination",
                      None, None, 0.55, 0, 5, 0, 0, 0, 1, "123", 0.55, None])
        book.save(path)
        report = consolidate([path], self.root / "native")
        self.assertEqual(report["source_rows"], 1)
        sheet["H3"] = "mm"
        book.save(path)
        with self.assertRaisesRegex(ValueError, "incomplete beam-force identity"):
            consolidate([path], self.root / "bad_units")
        self.assertFalse((self.root / "bad_units").exists())
        book.close()

    def test_wrong_case_fails_closed(self):
        row = self.row()
        row[3] = "1.5(DL+LL)"
        a = self.part("one.xlsx", [row])
        with self.assertRaisesRegex(ValueError, "unexpected Output Case"):
            consolidate([a], self.root / "out")

    def test_explicit_exact_case_projection_preserves_exclusion_counts(self):
        selected = self.row()
        other = self.row(unique="124")
        other[3] = "Modal Ritz"
        similar = self.row(unique="125")
        similar[3] = "1. dl + ll"
        a = self.part("one.xlsx", [other, selected])
        b = self.part("two.xlsx", [similar])
        with self.assertRaisesRegex(ValueError, "unexpected Output Case"):
            consolidate([a, b], self.root / "strict")
        report = consolidate([a, b], self.root / "selected", select_exact_case=True)
        self.assertEqual(report["source_rows"], 1)
        self.assertEqual(report["scanned_source_rows"], 3)
        self.assertEqual(report["case_selection_policy"], "EXACT_EXPLICIT_PROJECTION")
        self.assertEqual(report["input_files"][0]["excluded_case_row_counts"], {"Modal Ritz": 1})
        self.assertEqual(report["input_files"][1]["excluded_case_row_counts"], {"1. dl + ll": 1})
        self.assertEqual(report["input_files"][1]["rows_read"], 0)
        self.assertEqual(report["input_files"][1]["rows_scanned"], 1)
        self.assertEqual(report["input_files"][1]["sheets"][0]["rows_scanned"], 1)
        with (self.root / "selected" / "ETABS_Beam_Forces_Consolidated.csv").open(
                encoding="utf-8-sig", newline="") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual([row["Output Case"] for row in rows], ["1. DL + LL"])
        with self.assertRaisesRegex(ValueError, "No beam-force rows"):
            consolidate([b], self.root / "missing", select_exact_case=True)
        self.assertFalse((self.root / "missing").exists())

    def test_native_all_case_keys_keep_element_and_case_type_and_reject_conflict(self):
        from openpyxl import Workbook
        def native(name, records):
            path = self.root / name
            book = Workbook()
            ws = book.active
            ws.title = "Element Forces - Beams"
            ws.append(["TABLE: Element Forces - Beams"])
            ws.append(["Story", "Beam", "Unique Name", "Output Case", "Case Type",
                       "Step Type", "Step Number", "Station", "P", "V2", "V3",
                       "T", "M2", "M3", "Element", "Elem Station", "Location"])
            ws.append(["", "", "", "", "", "", None, "m", "kN", "kN",
                       "kN", "kN-m", "kN-m", "kN-m", "", "m", ""])
            for row in records:
                ws.append(row)
            book.save(path)
            book.close()
            return path
        a = ["Story1", "B1", "123", "Modal Ritz", "LinModRitz", "Mode",
             1, 0.55, 0, 5, 0, 0, 0, 1, "123", 0.55, None]
        b = a.copy(); b[14] = "124"; b[15] = 0.25
        c = a.copy(); c[4] = "OtherType"
        d = a.copy(); d[3] = "1. DL + LL"; d[4] = "Combination"; d[5] = None; d[6] = None
        first = native("first.xlsx", [a, b, c])
        second = native("second.xlsx", [a, d])
        result = consolidate([first, second], self.root / "all", all_cases=True)
        self.assertEqual(result["source_rows"], 5)
        self.assertEqual(result["unique_rows"], 4)
        self.assertEqual(result["exact_or_tolerance_matched_overlaps"], 1)
        self.assertIsNone(result["case"])
        self.assertEqual(result["case_selection_policy"], "ALL_NATIVE_CASES_EXACT")
        self.assertEqual(result["input_files"][0]["selected_case_row_counts"], {"Modal Ritz": 3})
        self.assertEqual(result["input_files"][1]["selected_case_row_counts"], {"Modal Ritz": 1, "1. DL + LL": 1})
        bad = a.copy(); bad[9] += 1e-8
        conflict = native("conflict.xlsx", [bad])
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate"):
            consolidate([first, conflict], self.root / "conflict", all_cases=True)
        self.assertFalse((self.root / "conflict").exists())
        with self.assertRaisesRegex(ValueError, "native.*units"):
            consolidate([self.part("legacy.xlsx", [self.row()])], self.root / "legacy", all_cases=True)
        self.assertFalse((self.root / "legacy").exists())
        with self.assertRaisesRegex(ValueError, "mutually exclusive"):
            consolidate([first], self.root / "both", all_cases=True, select_exact_case=True)

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
