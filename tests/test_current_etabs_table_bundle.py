"""ETABS table registration: one canonical current-source registry, no file copies."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openpyxl import Workbook

from components.inputs.etabs_table_bundle import register_current_etabs_tables, audit_analysis_workbooks
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

    def add_table(self, sheet, columns, units, rows, *, title=None):
        ws = self.book.create_sheet(sheet)
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


if __name__=="__main__":
    unittest.main()
