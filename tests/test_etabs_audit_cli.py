"""Command-line behaviour of the two ETABS export audit tools.

[REF docs/source/tests/test_etabs_audit_cli.py.md]
Small real .xlsx files are written in the ETABS table layout (title row, column
names, units row) and run through the actual CLI code; no engineering result is
claimed.
"""
import json
import tempfile
import unittest
from pathlib import Path

import openpyxl

from tools import audit_beam_force_shards as beam_cli
from tools import audit_etabs_lot_consistency as lot_cli

COLS = ["Story", "Beam", "Unique Name", "Output Case", "Case Type", "Step Type", "Step Number",
        "Station", "P", "V2", "V3", "T", "M2", "M3", "Element", "Elem Station", "Location"]


def write_beam_workbook(path, elements, *, cut=None, sheet="Element Forces - Beams"):
    wb = openpyxl.Workbook()
    wb.active.title = "Program Control"
    ws = wb.create_sheet(sheet)
    ws.append(["TABLE:  Element Forces - Beams"])
    ws.append(COLS)
    ws.append(["", "", "", "", "", "", "", "m", "kN", "kN", "kN", "kN-m", "kN-m", "kN-m", "", "m", ""])
    n = 0
    for element in elements:
        for case in ("DL", "LL"):
            for station in (0.5, 1.0):
                n += 1
                if cut is not None and n > cut:
                    break
                ws.append(["Story1", "B1", element, case, "LinStatic", "Step By Step", None, station,
                           0, 1.5, 0, 0, 0, 2.5, element, station, None])
    wb.save(path)


def write_frames_workbook(path, mapping):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Objects and Elements - Frames"
    ws.append(["TABLE:  Objects and Elements - Frames"])
    ws.append(["Story", "Element Name", "Object Type", "Object Label", "Object Name", "Elm JtI", "Elm JtJ"])
    ws.append([""] * 7)
    for element, story in mapping.items():
        ws.append([story, element, "Beam", "B1", "1", "1", "2"])
    wb.save(path)


class BeamCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_shards_pass_and_report_has_no_local_path(self):
        a, b, f = self.dir / "b1.xlsx", self.dir / "b2.xlsx", self.dir / "frames.xlsx"
        write_beam_workbook(a, ["1", "2"], cut=6)       # element 2 cut after 2 of its 4 rows
        write_beam_workbook(b, ["2", "3"])               # next shard repeats and completes it
        write_frames_workbook(f, {"1": "Story1", "2": "Story1", "3": "Story1"})
        out = self.dir / "report.json"
        self.assertEqual(beam_cli.main(["--beam-files", str(a), str(b), "--frame-workbook", str(f),
                                        "--output", str(out)]), 0)
        doc = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(doc["union_status"], "UNION_COMPLETE_AND_CONSISTENT")
        self.assertEqual(doc["union"]["elements"], 3)
        self.assertEqual(doc["union"]["unique_rows"], 12)
        self.assertEqual(doc["rows_repeated_in_later_shard"], 2)
        self.assertEqual(doc["frame_table_match"]["story_disagreements"], 0)
        self.assertEqual([x["file_name"] for x in doc["ingested_files"]], ["b1.xlsx", "b2.xlsx"])
        self.assertEqual(len(doc["ingested_files"][0]["sha256"]), 64)
        self.assertNotIn(str(self.dir), out.read_text(encoding="utf-8"))

    def test_unrecovered_cut_returns_failure_status(self):
        a = self.dir / "b1.xlsx"
        write_beam_workbook(a, ["1", "2"], cut=6)
        out = self.dir / "report.json"
        self.assertEqual(beam_cli.main(["--beam-files", str(a), "--output", str(out)]), 1)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["union_status"], "UNION_HAS_ERRORS")

    def test_existing_output_is_never_overwritten(self):
        a, out = self.dir / "b1.xlsx", self.dir / "report.json"
        write_beam_workbook(a, ["1"])
        out.write_text("keep", encoding="utf-8")
        with self.assertRaises(SystemExit):
            beam_cli.main(["--beam-files", str(a), "--output", str(out)])
        self.assertEqual(out.read_text(encoding="utf-8"), "keep")

    def test_source_workbook_is_not_modified(self):
        a = self.dir / "b1.xlsx"
        write_beam_workbook(a, ["1"])
        before = a.read_bytes()
        beam_cli.main(["--beam-files", str(a), "--output", str(self.dir / "r.json")])
        self.assertEqual(a.read_bytes(), before)

    def test_wrong_sheet_name_fails_loudly(self):
        a = self.dir / "b1.xlsx"
        write_beam_workbook(a, ["1"], sheet="Something else")
        with self.assertRaises(KeyError):
            beam_cli.main(["--beam-files", str(a), "--output", str(self.dir / "r.json")])


class LotCliTests(unittest.TestCase):
    def test_public_files_keep_identity_and_drop_local_paths(self):
        entries = [{"source_path": "/private/dir/LOT.xlsx", "sha256": "ab" * 32, "size_bytes": 5,
                    "status": "OK", "worksheet_count": 1,
                    "worksheets": [{"sheet": "S", "status": "OK", "nonempty_rows": 3, "content_sha256": "cd",
                                    "local_secret": "/private/x"}]}]
        got = lot_cli._public_files(entries)
        self.assertEqual(got[0]["file_name"], "LOT.xlsx")
        self.assertNotIn("/private", json.dumps(got))
        self.assertEqual(got[0]["worksheets"][0], {"sheet": "S", "status": "OK", "nonempty_rows": 3,
                                                   "content_sha256": "cd"})

    def test_existing_report_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            out.write_text("keep", encoding="utf-8")
            with self.assertRaises(SystemExit):
                lot_cli.main(["--analysis-files", str(Path(tmp) / "x.xlsx"), "--output", str(out)])
            self.assertEqual(out.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
