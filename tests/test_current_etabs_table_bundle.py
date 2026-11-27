"""ETABS table registration: one canonical current-source registry, no file copies."""
import hashlib
import json
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openpyxl import Workbook, load_workbook

from components.inputs.etabs_table_bundle import (
    audit_analysis_workbooks, read_first_lot_reference, register_current_etabs_tables,
)
from components.inputs.project_workbooks import registered_project_source
from tools.REGISTER_CURRENT_ETABS_TABLES import main


class CurrentEtabsBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/"export"
        self.root.mkdir()
        self.edb=self.root/"ULTIMATE MODEL.EDB"
        self.edb.write_bytes(b"source EDB native bytes")
        self.books=[]
        for i in range(4):
            p=self.root.parent/f"source_{i}.xlsx"
            w=Workbook();w.active.title=f"TablePart{i}"
            w.active["A1"]=f"Source table {i}"
            w.save(p)
            self.books.append(p)

    def test_current_tables_are_read_only_hash_registered_in_etabs_stage(self):
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=str(self.edb)):
            target,registry=register_current_etabs_tables(
                self.root,self.books[0],self.books[1:])
            self.assertEqual(target,self.root/"01_ETABS_EXPORT"/"00_MANIFEST"/
                             "PROJECT_SOURCES.private.json")
            self.assertFalse((self.root/"project_sources.private.json").exists())
            self.assertNotIn("etabs_assignment",registry["sources"])
            for path in self.books:
                self.assertTrue(path.is_file())
            self.assertEqual(len(registry["source_workbook_inventory"]),4)
            variant=(self.root/"02_MODEL"/"REBUILDS"/"VERIFIED_CLEAR_BEAM"/"one")
            variant.mkdir(parents=True)
            actual=registered_project_source(variant,"etabs_full_table")
            self.assertEqual(Path(actual),self.books[0])
            # Canonical current export does not contain native assignment
            # sheets: an older root-level registry must NOT fill this gap.
            import json
            old={"source_edb_sha256":registry["source_edb_sha256"],
                 "sources":{"etabs_assignment":{
                     "path":str(self.books[1]),
                     "sha256":hashlib.sha256(self.books[1].read_bytes()).hexdigest()}}}
            (self.root/"project_sources.private.json").write_text(
                json.dumps(old),encoding="utf-8")
            self.assertIsNone(registered_project_source(
                variant,"etabs_assignment"))

    def test_variable_number_of_beam_parts_and_stale_role_cleanup(self):
        extra=self.root.parent/"extra_part.xlsx"
        w=Workbook();w.active.title="ExtraBeamForcePart";w.active["A1"]="Distinct";w.save(extra)
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=str(self.edb)):
            _,initial=register_current_etabs_tables(
                self.root,self.books[0],[self.books[1],self.books[2],self.books[3],extra])
            self.assertIn("etabs_beam_forces_element_4",initial["sources"])
            _,updated=register_current_etabs_tables(
                self.root,self.books[0],[self.books[1],self.books[2]])
            self.assertNotIn("etabs_beam_forces_element_3",updated["sources"])
            self.assertNotIn("etabs_beam_forces_element_4",updated["sources"])
            self.assertEqual(len([k for k in updated["sources"]
                                  if k.startswith("etabs_beam_forces_element_")]),2)

    def test_empty_beam_selection_fails_before_manifest(self):
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=str(self.edb)):
            with self.assertRaisesRegex(ValueError,"at least one"):
                register_current_etabs_tables(self.root,self.books[0],[])
        self.assertFalse((self.root/"01_ETABS_EXPORT").exists())

    def test_byte_identical_beam_parts_are_rejected(self):
        # Distinct paths whose bytes are identical cannot represent
        # two independently exported beam-force table parts.
        self.books[2].write_bytes(self.books[1].read_bytes())
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=str(self.edb)):
            with self.assertRaisesRegex(ValueError,"identical bytes"):
                register_current_etabs_tables(
                    self.root,self.books[0],self.books[1:])
        self.assertFalse((self.root/"01_ETABS_EXPORT"/"00_MANIFEST").exists())

    def test_nested_model_folder_cannot_own_duplicate_etabs_manifest(self):
        nested=self.root/"02_MODEL"/"REBUILDS"/"VERIFIED_CLEAR_BEAM"/"run"
        nested.mkdir(parents=True)
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=str(self.edb)):
            with self.assertRaisesRegex(ValueError,"ORIGINAL export"):
                register_current_etabs_tables(nested,self.books[0],self.books[1:])
        self.assertFalse((nested/"01_ETABS_EXPORT").exists())

    def test_multi_lot_all_sheets_and_duplicate_evidence(self):
        a,b=self.books[:2]
        for p in (a,b):
            w=Workbook();w.active.title="Joint Reactions"
            w.active.append(["Joint","OutputCase","F3"])
            w.active.append(["1","Dead",100])
            s=w.create_sheet("Element Connectivity - Shells")
            s.append(["Object","Elm","Joint1","Joint2","Joint3","Joint4"])
            s.append(["W","E","1","2","3","4"])
            s.sheet_state="hidden"
            w.create_sheet("Empty")
            w.save(p)
        before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)]
        report=audit_analysis_workbooks([a,b])
        self.assertEqual(report["status"],"ALL_WORKSHEETS_SCANNED_NOT_ENGINEERING_VALIDATION")
        self.assertEqual(report["fully_scanned_worksheets"],6)
        self.assertEqual(report["nonempty_rows"],8)
        self.assertEqual(report["populated_cells"],36)
        self.assertEqual(len(report["repeated_sheet_names"]),3)
        self.assertEqual(len(report["identical_populated_cell_content"]),3)
        self.assertEqual(report["files"][0]["worksheets"][1]["state"],"hidden")
        self.assertIn("analytical_mesh",report["candidate_evidence_families"])
        self.assertEqual(before,[hashlib.sha256(p.read_bytes()).hexdigest() for p in (a,b)])
        self.assertEqual(report["engineering_acceptance"],"NOT_VERIFIED")

    def test_bad_lot_does_not_hide_readable_lot(self):
        bad=self.root.parent/"broken.xlsx";bad.write_bytes(b"not a workbook")
        report=audit_analysis_workbooks([self.books[0],bad])
        self.assertEqual(report["status"],"INCOMPLETE_SCAN")
        self.assertEqual(report["fully_scanned_worksheets"],1)
        self.assertEqual(report["files"][1]["status"],"WORKBOOK_SCAN_FAILED")
        self.assertEqual(len(report["errors"]),1)
        with self.assertRaisesRegex(ValueError,"distinct"):
            audit_analysis_workbooks([self.books[0],self.books[0]])

    def test_missing_native_source_blocks_creation(self):
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=None):
            with self.assertRaisesRegex(FileNotFoundError,"source EDB"):
                register_current_etabs_tables(self.root,self.books[0],self.books[1:])
        self.assertFalse((self.root/"01_ETABS_EXPORT").exists())


class FirstLotReferenceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.source = Path(tmp.name) / "first.xlsx"
        self.output = Path(tmp.name) / "reference"
        self.book = Workbook()
        self.book.remove(self.book.active)
        self.add_table("Program Control", "ProgramName|Version|CurrUnits", "||",
                       [("ETABS", "23.2.0", "kip, in, F")])
        self.add_table(
            "Story Forces", "Story|Output Case|Case Type|Step Type|Step Number|Location|P|VX|VY|T|MX|MY",
            "||||||kN|kN|kN|kN-m|kN-m|kN-m", [
                ("Story25", "EQX", "LinStatic", "Step By Step", 1, "Bottom", 0, -12, 0, 0, 0, 0),
                ("Story25", "EQX", "LinStatic", "Step By Step", 2, "Bottom", 0, 3, 0, 0, 0, 0),
                ("Story25", "EQX+ P-Delta", "LinStatic", "Step By Step", 1, "Top", 0, 8, 0, 0, 0, 0),
            ])
        self.add_table(
            "Story Max Over Avg Disp",
            "Story|Output Case|Case Type|Step Type|Step Number|Direction|Maximum|Average|Ratio",
            "||||||mm|mm|", [("Story25", "EQX", "LinStatic", None, None, "X", 250, 125, 2)],
            title="Story Max Over Avg Displacements")
        self.add_table(
            "Response Spectrum Modal Info",
            "SpecCase|ModalCase|Mode|Period|DampRatio|U1Acc|U2Acc|U3Acc|U1Amp|U2Amp|U3Amp",
            "|||sec||mm/sec²|mm/sec²|mm/sec²|mm|mm|mm",
            [("RS X", "Modal Ritz", "1", 2.4, 0.05, 800, 0, 0, 0.5, 0, 0)])

    def add_table(self, sheet, columns, units, rows, *, title=None, book=None):
        ws = (self.book if book is None else book).create_sheet(sheet)
        ws.append(["TABLE:  " + (title or sheet)])
        ws.append(columns.split("|"))
        ws.append(units.split("|"))
        for row in rows:
            ws.append(row)

    def run_import(self, *args):
        self.book.save(self.source)
        return main(["--analysis-reference", str(self.source),
                     "--reference-output", str(self.output), *args])

    def test_export_reference_with_exact_cases_steps_units_and_provenance(self):
        self.assertEqual(self.run_import("--reference-case", "EQX", "--reference-case", "RS X"), 0)
        report = json.loads((self.output / "FIRST_LOT_REFERENCE.private.json").read_text("utf-8"))
        self.assertEqual(report["source"]["workbook_sha256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(report["source"]["reported_current_units"], "kip, in, F")
        self.assertIsNone(report["source"]["edb_sha256"])
        self.assertEqual(report["engineering_acceptance"], "NOT_VERIFIED")
        self.assertIn("Pier Forces", report["missing_tables"])
        forces = report["tables"]["Story Forces"]
        self.assertEqual(forces["case_row_counts"], {"EQX": 2, "EQX+ P-Delta": 1})
        self.assertEqual(forces["stories"], ["Story25"])
        self.assertEqual([row[0] for row in forces["rows"]], [4, 5])
        self.assertEqual([row[forces["columns"].index("VX")] for row in forces["rows"]], [-12, 3])
        self.assertEqual(forces["units"]["VX"], "kN")
        disp = report["tables"]["Story Max Over Avg Disp"]
        self.assertEqual(disp["units"]["Maximum"], "m")
        self.assertEqual(disp["rows"][0][disp["columns"].index("Maximum")], 0.25)
        modal = report["tables"]["Response Spectrum Modal Info"]
        self.assertEqual(modal["units"]["U1Acc"], "m/s²")
        self.assertEqual(modal["rows"][0][modal["columns"].index("U1Acc")], 0.8)
        self.assertEqual(modal["rows"][0][modal["columns"].index("Mode")], 1)
        self.assertFalse(list(self.output.rglob("PROJECT_SOURCES.private.json")))

    def test_display_diagnostics_keep_original_values_and_prefilter_scope(self):
        self.book["Story Max Over Avg Disp"].append(
            ["Story25", "OTHER", "LinStatic", None, None, "Y", 1, 0, 999])
        self.add_table(
            "Story Max Over Avg Drifts",
            "Story|Output Case|Case Type|Step Type|Step Number|Direction|Max Drift|Avg Drift|Ratio",
            "||||||mm|mm|", [("Story25", "EQX", "LinStatic", None, None, "X", 1, 0, 999)])
        self.add_table(
            "Story Drifts",
            "Story|Output Case|Case Type|Step Type|Step Number|Direction|Drift|Drift/|Label|X|Y|Z",
            "|||||||||m|m|m", [
                ("Story25", "EQX", "LinStatic", None, None, "X", 0.000001, "1/0", "A", 0, 0, 95),
                ("Story25", "EQX", "LinStatic", None, None, "Y", 0, "1/0", "B", 0, 0, 95),
            ])
        self.book.save(self.source)
        from components.inputs.etabs_table_bundle import read_analysis_reference
        zero_flag = "ZERO_REPORTED_AVERAGE_RATIO_UNRESOLVED"
        for storage in (None, self.source.with_suffix(".sqlite3")):
            with self.subTest(storage=storage):
                report = read_analysis_reference([self.source], cases=["EQX"], row_database=storage)
                tables = report["tables"]
                for name, position in [("Story Max Over Avg Drifts", 4), ("Story Max Over Avg Disp", 5)]:
                    flags = tables[name]["source_display_diagnostics"]
                    self.assertEqual(flags["scope"], "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER")
                    self.assertEqual(flags["status"], "REFERENCE_ONLY_NOT_NBC_TORSION_EVALUATION")
                    self.assertEqual(flags["worksheet_rows"][zero_flag], [position])
                    self.assertEqual(flags["flag_counts"][zero_flag], 1)
                drift = tables["Story Drifts"]
                flags = drift["source_display_diagnostics"]["worksheet_rows"]
                self.assertEqual(flags["RECIPROCAL_DISPLAY_ONE_OVER_ZERO"], [4, 5])
                self.assertEqual(flags["RECIPROCAL_DISPLAY_ONE_OVER_ZERO_NONZERO_DRIFT"], [4])
                if storage is None:
                    self.assertEqual(drift["rows"][0][drift["columns"].index("Drift")], 0.000001)
                    table = tables["Story Max Over Avg Drifts"]
                    self.assertEqual(table["rows"][0][table["columns"].index("Ratio")], 999)
                    self.assertEqual(len(tables["Story Max Over Avg Disp"]["rows"]), 1)
                self.assertEqual(report["engineering_acceptance"], "NOT_VERIFIED")

    def test_invalid_workbook_or_selection_never_publishes(self):
        for extra, bad_cell, value, message in [
            (("--reference-case", "EQ"), None, None, "case"),
            (("--analysis-files", str(self.source)), None, None, "mode"),
            ((), "H3", "kip", "unit"),
            (("--reference-case", "EQX"), "H6", "=8", "numeric"),
        ]:
            with self.subTest(extra=extra, bad_cell=bad_cell):
                cell = self.book["Story Forces"][bad_cell] if bad_cell else None
                old = cell.value if cell else None
                if cell:
                    cell.value = value
                with patch("sys.stderr") as errors, self.assertRaises(SystemExit) as reason:
                    self.run_import(*extra)
                self.assertEqual(reason.exception.code, 2)
                self.assertIn(message, "".join(call.args[0] for call in errors.write.call_args_list))
                self.assertFalse(self.output.exists())
                if cell:
                    cell.value = old

    def test_duplicate_result_key_rejected(self):
        table = self.book["Story Forces"]
        table.append([cell.value for cell in table[4]])
        with patch("sys.stderr") as errors, self.assertRaises(SystemExit) as reason:
            self.run_import()
        self.assertEqual(reason.exception.code, 2)
        self.assertIn("duplicate result key", "".join(call.args[0] for call in errors.write.call_args_list))
        self.assertFalse(self.output.exists())

    def test_program_metadata_must_be_literal_and_inside_its_columns(self):
        for address, invalid in [("B4", '= "23.2.0"'), ("C4", "#REF!"), ("D4", "overflow")]:
            with self.subTest(address=address):
                cell = self.book["Program Control"][address]
                original = cell.value
                cell.value = invalid
                with patch("sys.stderr") as errors, self.assertRaises(SystemExit) as reason:
                    self.run_import()
                self.assertEqual(reason.exception.code, 2)
                self.assertIn("Program Control", "".join(call.args[0] for call in errors.write.call_args_list))
                self.assertFalse(self.output.exists())
                cell.value = original

    def test_existing_output_is_rejected(self):
        self.output.mkdir()
        existing = self.output / "FIRST_LOT_REFERENCE.private.json"
        existing.write_text("existing", encoding="utf-8")
        with self.assertRaises(SystemExit) as reason:
            self.run_import()
        self.assertEqual(reason.exception.code, 2)
        self.assertEqual(existing.read_text("utf-8"), "existing")

    def test_single_first_lot_preserves_exact_title_and_missing_input_error(self):
        with self.assertRaisesRegex(ValueError, "Select one local ETABS"):
            read_first_lot_reference(self.source)
        self.book.create_sheet("Story Forces ").append(["Unrecognized extra sheet"])
        self.book.save(self.source)
        report = read_first_lot_reference(self.source)
        self.assertIn("Story Forces", report["tables"])
        self.assertEqual(report["unrecognized_sheets"], ["Story Forces "])

    def second_lot(self, *, period=2.4, include_missing_joint=False):
        source = self.source.with_name("second.xlsx")
        book = Workbook()
        book.remove(book.active)
        self.add_table(
            "Objects and Elements - Joints",
            "Story|Element Name|Object Type|Object Label|Object Name|Global X|Global Y|Global Z",
            "|||||mm|mm|mm", [
                ("Story25", "01", "Joint", "A", "01", 0, 0, 1000),
                ("Story25", "02", "Joint", "B", "02", 2000, 0, 1000),
                ("Story25", "03", "Joint", "C", "03", 2000, 3000, 1000),
                ("Story25", "04", "Joint", "D", "04", 0, 3000, 1000),
            ], book=book)
        edge = ("Story25", "4", "Shell", "F1", "1", "01", "02")
        self.add_table(
            "Objects and Elements - Frames",
            "Story|Element Name|Object Type|Object Label|Object Name|Elm JtI|Elm JtJ",
            "||||||", [edge, edge, (*edge[:5], "02", "99" if include_missing_joint else "03")], book=book)
        self.add_table(
            "Objects and Elements - Areas",
            "Story|Element Name|Object Type|Object Label|Object Name|Elm Jt1|Elm Jt2|Elm Jt3|Elm Jt4",
            "||||||||", [("Story25", "4", "Floor", "F1", "1", "01", "02", "03", "04")], book=book)
        self.add_table(
            "Modal Periods And Frequencies", "Case|Mode|Period|Frequency|CircFreq|Eigenvalue",
            "||sec|cyc/sec|rad/sec|rad²/sec²", [("Modal Ritz", "1", period, 0.4, 2.6, 6.7)], book=book)
        self.add_table(
            "Modal Participation Factors", "Case|Mode|Period|UX|UY|UZ|RX|RY|RZ|ModalMass|ModalStiff",
            "||sec|kN-m|kN-m|kN-m|kN-m|kN-m|kN-m|kN-m-s²|kN-m",
            [("Modal Ritz", "1", period, 0, 1, -2, 0, 0, 0, 0.1, 0.6)], book=book)
        self.add_table(
            "Modal Participating Mass Ratios", "Case|Mode|Period|UX|UY|UZ|SumUX|SumUY|SumUZ|RX|RY|RZ|SumRX|SumRY|SumRZ",
            "||sec||||||||||||", [("Modal Ritz", "1", period, 0, 0.5, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0)],
            book=book)
        self.add_table(
            "Modal Direction Factors", "Case|Mode|Period|UX|UY|UZ|RZ", "||sec||||",
            [("Modal Ritz", "1", period, 0, 1, 0, 0)], book=book)
        self.add_table(
            "Modal Load Participation Ratios", "Case|ItemType|Item|Static|Dynamic",
            "|||%|%", [("Modal Ritz", "Acceleration", "UX", 100, 98.78)], book=book)
        book.save(source)
        return source

    def test_integrated_reference_keeps_source_keys_and_collapses_only_identical_frame_rows(self):
        second = self.second_lot()
        self.assertEqual(self.run_import("--analysis-reference", str(second),
                                         "--reference-case", "EQX", "--reference-case", "Modal Ritz"), 0)
        report = json.loads((self.output / "ETABS_ANALYSIS_REFERENCE.private.json").read_text("utf-8"))
        self.assertEqual(report["schema"], "ETABS_ANALYSIS_REFERENCE_V1")
        self.assertEqual(report["engineering_acceptance"], "NOT_VERIFIED")
        self.assertEqual([s["edb_sha256"] for s in report["files"]], [None, None])
        self.assertIsNone(report["files"][1]["etabs_version"])
        self.assertEqual(report["files"][1]["sha256"], hashlib.sha256(second.read_bytes()).hexdigest())
        tables = report["tables"]
        self.assertEqual(tables["Story Forces"]["file_index"], 0)
        frames = tables["Objects and Elements - Frames"]
        self.assertEqual(frames["file_index"], 1)
        self.assertEqual(frames["source_row_count"], 3)
        self.assertEqual([row[0] for row in frames["rows"]], [4, 6])
        self.assertEqual(frames["duplicate_worksheet_rows"], [{"worksheet_row": 4, "also_at": [5]}])
        self.assertEqual(frames["rows"][1][-2:], ["02", "03"])
        joints = tables["Objects and Elements - Joints"]
        self.assertEqual(joints["units"]["Global Z"], "m")
        self.assertEqual(joints["rows"][0][-1], 1)
        modal = tables["Modal Load Participation Ratios"]
        self.assertEqual(modal["units"]["Dynamic"], "1")
        self.assertAlmostEqual(modal["rows"][0][-1], 0.9878)
        self.assertEqual(report["checks"]["modal_periods"]["Response Spectrum Modal Info"],
                         {"matched_rows": 1, "unmatched_rows": 0})
        self.assertEqual(report["checks"]["modal_periods"]["Modal Participation Factors"],
                         {"matched_rows": 1, "unmatched_rows": 0})
        self.assertEqual(report["checks"]["connectivity"]["Objects and Elements - Frames"]["unresolved_joint_ids"], [])
        self.assertEqual(report["checks"]["connectivity"]["Objects and Elements - Areas"]["checked_rows"], 1)
        self.assertEqual(tables["Modal Participation Factors"]["units"]["ModalMass"], "kN-m-s²")
        self.assertEqual(tables["Modal Participating Mass Ratios"]["rows"][0][5], 0.5)

    def test_cumulative_reference_diagnostics_before_case_filter(self):
        from components.inputs.etabs_table_bundle import read_analysis_reference
        second = self.second_lot()
        book = load_workbook(second)
        book["Objects and Elements - Joints"].append(
            ["Story25", "05", "Joint", "A", "05", 0, 0, 1000])
        book["Modal Periods And Frequencies"].append(
            ["Modal Ritz", "2", 0.2, 5, 31.4159, 986.96])
        book["Modal Participating Mass Ratios"].append(
            ["Modal Ritz", "2", 0.2, 0.91, 0.45, 0, 0.91, 0.95, 0, 0, 0, 0, 0, 0, 0])
        book.save(second)
        book.close()
        self.add_table(
            "Story Drifts",
            "Story|Output Case|Case Type|Step Type|Step Number|Direction|Drift|Drift/|Label|X|Y|Z",
            "|||||||||m|m|m", [
                ("Story25", "EQX", "LinStatic", None, None, "X", 0.001, "1/1000", "C", 2, 3, 1),
                ("Story25", "EQX", "LinStatic", None, None, "Y", 0.001, "1/1000", "B", 5, 0, 1),
                ("Story25", "OTHER", "LinStatic", None, None, "X", 0.001, "1/1000", "MISSING", 0, 0, 1),
                ("Story25", "OTHER", "LinStatic", None, None, "Y", 0.001, "1/1000", "A", 0, 0, 1),
            ])
        self.book.save(self.source)
        for database in (None, self.source.with_suffix(".sqlite3")):
            with self.subTest(database=database):
                report = read_analysis_reference([self.source, second], cases=["EQX"],
                                                 row_database=database)
                checks = report["checks"]
                modal = checks["modal_mass_reference"]["cases"]["Modal Ritz"]
                self.assertTrue(modal["contiguous_from_one"])
                self.assertAlmostEqual(modal["axes"]["UY"]["reported_final_fraction"], 0.95)
                self.assertEqual(modal["axes"]["UY"]["first_reported_90_percent"]["mode"], 2)
                self.assertIsNone(modal["axes"]["UZ"]["first_reported_90_percent"])
                self.assertEqual(modal["axes"]["UX"]["out_of_range_rows"], [])
                drift = checks["story_drift_joint_reference"]
                self.assertEqual(drift["counts"], {
                    "UNIQUE_COORDINATE_MATCH": 1, "COORDINATE_MISMATCH": 1,
                    "NO_STORY_LABEL_MATCH": 1, "AMBIGUOUS_COORDINATE_MATCH": 1})
                self.assertEqual(drift["exception_worksheet_rows"]["NO_STORY_LABEL_MATCH"], [6])
                self.assertEqual(report["engineering_acceptance"], "NOT_VERIFIED")

    def test_joint_identity_and_static_reaction_reference_before_filter(self):
        from components.inputs.etabs_table_bundle import read_analysis_reference
        second = self.second_lot()
        third = self.source.with_name("third.xlsx")
        book = Workbook()
        book.remove(book.active)
        self.add_table(
            "Joint Reactions",
            "Story|Label|Unique Name|Output Case|Case Type|Step Type|Step Number|FX|FY|FZ|MX|MY|MZ",
            "|||||||kN|kN|kN|kN-m|kN-m|kN-m", [
                ("Story25", "A", "01", "Dead", "LinStatic", None, None, 0, 0, 10, 0, 0, 0),
                ("Story25", "B", "02", "Dead", "LinStatic", None, None, 0, 0, 0, 0, 0, 0),
                ("Story25", "C", "03", "EQX", "LinStatic", "Step By Step", 1, -5, 0, 0, 0, 0, 0),
                ("Story25", "C", "03", "EQX", "LinStatic", "Step By Step", 1, -6, 0, 0, 0, 0, 0),
                ("Story25", "D", "04", "Live", "LinStatic", None, None, 0, 0, None, 0, 0, 0),
                ("Story25", "A", "01", "RS", "LinRespSpec", "Max", None, 3, 0, 0, 0, 0, 0),
                ("Story25", "X", "99", "RS", "LinRespSpec", "Max", None, 4, 0, 0, 0, 0, 0),
                ("WrongStory", "A", "01", "RS", "LinRespSpec", "Max", None, 2, 0, 0, 0, 0, 0),
                ("Story25", "WrongLabel", "02", "RS", "LinRespSpec", "Max", None, 1, 0, 0, 0, 0, 0),
                ("Story25", None, "04", "RS", "LinRespSpec", "Max", None, 1, 0, 0, 0, 0, 0),
            ], book=book)
        book.save(third)
        book.close()
        report = read_analysis_reference([second, third], cases=["EQX"],
                                         row_database=self.source.with_suffix(".sqlite3"))
        identity = report["checks"]["joint_response_identity"]["tables"]["Joint Reactions"]
        self.assertEqual(identity["counts"], {"MATCHED": 6, "UNKNOWN_JOINT_ID": 1,
                         "STORY_MISMATCH": 1, "LABEL_MISMATCH": 1, "MISSING_RESPONSE_LABEL": 1})
        self.assertEqual(identity["unresolved_joint_ids"], ["99"])
        self.assertEqual(identity["exception_worksheet_row_samples"]["UNKNOWN_JOINT_ID"], [10])
        reactions = report["checks"]["static_reaction_reference"]
        groups = {group["Output Case"]: group for group in reactions["groups"]}
        self.assertEqual(set(groups), {"Dead", "EQX", "Live"})
        self.assertEqual(groups["Dead"]["reported_force_sum_kN"], {"FX": 0, "FY": 0, "FZ": 10})
        self.assertEqual(groups["Dead"]["nonzero_reaction_joint_ids"], ["01"])
        self.assertEqual(groups["Dead"]["zero_reaction_joint_ids"], ["02"])
        self.assertEqual(groups["EQX"]["ambiguous_joint_ids"], ["03"])
        self.assertIsNone(groups["EQX"]["reported_force_sum_kN"])
        self.assertEqual(groups["Live"]["incomplete_joint_ids"], ["04"])
        self.assertIsNone(groups["Live"]["reported_force_sum_kN"])
        self.assertEqual(reactions["excluded_row_counts_by_case_step_type"], {"LinRespSpec | Max": 5})
        self.assertEqual(report["tables"]["Joint Reactions"]["stored_row_count"], 2)
        self.assertEqual(report["engineering_acceptance"], "NOT_VERIFIED")

    def test_second_lot_can_be_read_alone_and_reports_unresolved_joint_ids(self):
        second = self.second_lot(include_missing_joint=True)
        self.assertEqual(main(["--analysis-reference", str(second), "--reference-output", str(self.output)]), 0)
        report = json.loads((self.output / "ETABS_ANALYSIS_REFERENCE.private.json").read_text("utf-8"))
        self.assertEqual(report["checks"]["connectivity"]["Objects and Elements - Frames"]["unresolved_joint_ids"], ["99"])
        self.assertIn("Story Forces", report["missing_tables"])
        self.assertIsNone(report["files"][0]["reported_current_units"])

    def test_modal_conflict_in_a_filtered_out_case_blocks_publication(self):
        second = self.second_lot(period=2.5)
        with patch("sys.stderr") as errors, self.assertRaises(SystemExit) as reason:
            self.run_import("--analysis-reference", str(second), "--reference-case", "EQX")
        self.assertEqual(reason.exception.code, 2)
        self.assertIn("conflicting modal period", "".join(call.args[0] for call in errors.write.call_args_list))
        self.assertFalse(self.output.exists())

    def test_repeated_workbooks_and_overlapping_tables_fail_without_output(self):
        second = self.second_lot()
        copy = self.source.with_name("copy.xlsx")
        copy.write_bytes(second.read_bytes())
        overlap = self.source.with_name("overlap.xlsx")
        with second.open("rb") as original:
            book = load_workbook(original)
        book["Modal Periods And Frequencies"]["D4"] = 0.45
        book.save(overlap)
        book.close()
        for other, message in [(second, "distinct analysis workbook lots"), (copy, "identical bytes"),
                               (overlap, "more than one workbook")]:
            with self.subTest(other=other):
                with patch("sys.stderr") as errors, self.assertRaises(SystemExit) as reason:
                    main(["--analysis-reference", str(second), str(other),
                          "--reference-output", str(self.output)])
                self.assertEqual(reason.exception.code, 2)
                self.assertIn(message, "".join(call.args[0] for call in errors.write.call_args_list))
                self.assertFalse(self.output.exists())

    def test_sqlite_reference_validates_large_lot_rows_and_retains_duplicate_positions(self):
        source = self.source.with_name("fourth.xlsx")
        book = Workbook()
        book.remove(book.active)
        headers = ("Story|Shell Object|Unique Name|Design Type|Shell Element|Joint|Output Case|Case Type|"
                   "Step Type|Step Number|S11 Top|S22 Top|S12 Top|SMax Top|SMin Top|SVM Top|"
                   "S11 Bottom|S22 Bottom|S12 Bottom|SMax Bottom|SMin Bottom|SVM Bottom|"
                   "S13 Average|S23 Average|SMaxV Average")
        row = ("Story25", "F1", "004", "Floor", "5", "01", "EQX", "LinStatic", "Max", None, 1.25, *([0] * 14))
        excluded = (*row[:6], "Gravity", *row[7:])
        self.add_table("Element Stresses - Area Shells", headers, "||||||||||" + "|".join(["MPa"] * 15),
                       [row, row, excluded, excluded], book=book)
        book.save(source)
        args = ["--analysis-reference", str(source), "--reference-case", "EQX",
                "--reference-output", str(self.output)]
        self.assertEqual(main([*args, "--reference-storage", "sqlite"]), 0)
        reference = json.loads((self.output / "ETABS_ANALYSIS_REFERENCE.private.json").read_text("utf-8"))
        self.assertEqual(reference["schema"], "ETABS_ANALYSIS_SQLITE_REFERENCE_V1")
        storage = reference["row_storage"]
        database = self.output / storage["file"]
        self.assertEqual(storage["sha256"], hashlib.sha256(database.read_bytes()).hexdigest())
        data = reference["tables"]["Element Stresses - Area Shells"]
        self.assertEqual(data["source_row_count"], 4)
        self.assertEqual(data["unique_row_count"], 2)
        self.assertEqual(data["stored_row_count"], 1)
        self.assertEqual(data["case_row_counts"], {"EQX": 1, "Gravity": 1})
        self.assertEqual(data["units"]["S11 Top"], "kN/m²")
        availability = data["source_field_availability"]
        self.assertEqual(availability["scope"], "ALL_UNIQUE_SOURCE_ROWS_BEFORE_CASE_FILTER")
        self.assertEqual({g["case"] for g in availability["groups"]}, {"EQX", "Gravity"})
        for g in availability["groups"]:
            self.assertEqual(g["field_counts"]["S11 Top"], {"missing": 0, "zero": 0, "nonzero": 1})
            self.assertEqual(g["flags"], ["TOP_ALL_REPORTED_DERIVED_ZERO_WITH_NONZERO_DIRECTIONAL_UNRESOLVED"])
        with closing(sqlite3.connect(database)) as db:
            rows = db.execute("SELECT worksheet_row, values_json FROM reference_rows").fetchall()
            aliases = db.execute("SELECT worksheet_row, retained_row FROM source_row_aliases").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 4)
        self.assertEqual(json.loads(rows[0][1])[10], 1250)
        self.assertEqual(aliases, [(5, 4)])
        self.assertFalse(list(self.output.rglob("PROJECT_SOURCES.private.json")))

    def test_group_energy_zero_is_not_missing_or_nonzero(self):
        source = self.source.with_name("energy.xlsx")
        book = Workbook()
        book.remove(book.active)
        self.add_table("Element NL Energy By Group",
                       "Group|Output Case|Case Type|Step Type|Step Number|Internal Viscous Damping|Internal Hysteretic Damping|Support Viscous Damping|Support Hysteretic Damping",
                       "|||||kN-m|kN-m|kN-m|kN-m",
                       [("All", "EQX", "NonModHist", "Max", None, 0, 0, 0, 0),
                        ("Wall", "EQX", "NonModHist", "Max", None, None, 0, 0, 0),
                        ("Beam", "EQX", "NonModHist", "Max", None, 2, 0, 0, 0)],
                       title="Element Nonlinear Energy By Group", book=book)
        book.save(source)
        book.close()
        self.assertEqual(main(["--analysis-reference", str(source), "--reference-storage", "sqlite",
                               "--reference-output", str(self.output)]), 0)
        ref = json.loads((self.output / "ETABS_ANALYSIS_REFERENCE.private.json").read_text("utf-8"))
        data = ref["tables"]["Element NL Energy By Group"]["source_field_availability"]
        groups = {g["group"]: g for g in data["groups"]}
        self.assertEqual(groups["All"]["flags"], ["ALL_REPORTED_ENERGY_ZERO_UNRESOLVED"])
        self.assertEqual(groups["Wall"]["flags"], [])
        self.assertEqual(groups["Wall"]["field_counts"]["Internal Viscous Damping"]["missing"], 1)
        self.assertEqual(groups["Beam"]["flags"], [])
        self.assertEqual(groups["Beam"]["field_counts"]["Internal Viscous Damping"]["nonzero"], 1)

    def test_later_lot_response_variants_stay_distinct_and_invalid_sqlite_import_is_cleaned_up(self):
        source = self.source.with_name("third.xlsx")
        book = Workbook()
        book.remove(book.active)
        for suffix in ("Relative", "Absolute"):
            self.add_table(
                f"Joint Velocities - {suffix}",
                "Story|Label|Unique Name|Output Case|Case Type|Step Type|Step Number|UX|UY|UZ|RX|RY|RZ",
                "|||||||mm/sec|mm/sec|mm/sec|rad/sec|rad/sec|rad/sec",
                [("Story1", "A", "001", "EQX", "LinStatic", "Max", None, value, 0, None, 0, 0, 0)
                 for value in (0.4892, 0.4892000000000001)],
                book=book)
        book.save(source)
        destination = self.output.with_name("bad_reference")
        cases = ["--analysis-reference", str(source), "--reference-storage", "sqlite"]
        book["Joint Velocities - Absolute"]["H4"] = "=20"
        book.save(source)
        with patch("sys.stderr") as errors, self.assertRaises(SystemExit) as reason:
            main([*cases, "--reference-output", str(destination)])
        self.assertEqual(reason.exception.code, 2)
        self.assertIn("finite numeric value", "".join(call.args[0] for call in errors.write.call_args_list))
        self.assertFalse(destination.exists())
        self.assertFalse(list(source.parent.glob(".etabs-reference-*")))
        book["Joint Velocities - Absolute"]["H4"] = 0.4892
        book.save(source)
        self.assertEqual(main([*cases, "--reference-output", str(self.output)]), 0)
        report = json.loads((self.output / "ETABS_ANALYSIS_REFERENCE.private.json").read_text("utf-8"))
        for table in report["tables"].values():
            self.assertEqual(table["stored_row_count"], 2)
            self.assertEqual(table["blank_measure_counts"], {"UZ": 2})
            self.assertEqual(table["units"]["UX"], "m/s")
        self.assertEqual(len(report["tables"]), 2)

    def test_interrupted_manifest_write_does_not_publish_database(self):
        with patch("components.inputs.output_contract.atomic_json", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_import("--reference-storage", "sqlite")
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.source.parent.glob(".etabs-reference-*")))


if __name__=="__main__":
    unittest.main()
