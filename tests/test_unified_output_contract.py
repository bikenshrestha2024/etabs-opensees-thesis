"""Filesystem-only compatibility tests for seven-stage run output contract."""
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_layout import (
    canonical_stage_folder, export_root_for, result_roots, STAGE_FOLDERS,
)
from components.inputs.output_contract import (
    RUN_SUBFOLDERS, create_case_run, record_case_status, atomic_json,
    write_table, safe_component, style_workbook,
)
from components.inputs.project_output_layout import create_project_layout, case_folder


class UnifiedOutputContractTests(unittest.TestCase):
    def test_canonical_aliases_and_no_side_effects(self):
        self.assertEqual(canonical_stage_folder("06_LINEAR_TH"), "06_LINEAR_TIME_HISTORY")
        self.assertEqual(canonical_stage_folder("07_NONLINEAR_TH"), "07_NONLINEAR_TIME_HISTORY")
        self.assertEqual(canonical_stage_folder("MODEL"), "02_MODEL")
        self.assertEqual(canonical_stage_folder("03_ESM"), "03_ESM")
        with self.assertRaises(ValueError):
            canonical_stage_folder("INVALID")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            legacy=root/"06_LINEAR_TH"/"case"
            self.assertEqual(export_root_for(legacy),root)
            self.assertEqual(result_roots(legacy,stages=("LTHA",)),())
            self.assertFalse(root.exists())

    def test_read_both_canonical_legacy_without_nested_duplication(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            old=root/"OpenSees_Analysis_Results"/"ULS"
            new=root/"02_GRAVITY"/"RUNS"/"ULS"
            older=root/"06_LINEAR_TH"/"X"
            for p in (old,new,older):p.mkdir(parents=True)
            roots=result_roots(new,stages=("GRAVITY","LTHA"))
            self.assertEqual(set(roots), {
                old.parent.resolve(), new.parent.parent.resolve(),older.parent.resolve()
            })
            self.assertEqual(len(roots),3)

    def test_review_and_source_manifest_nested_paths_map_to_export_root(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            for name in ("REVIEW_MAIN","00_SOURCE_MANIFEST",
                         "09_SOFTWARE_DIAGNOSTICS"):
                nested=root/name/"RUNS"/"case"
                self.assertEqual(export_root_for(nested),root)
            self.assertFalse(root.exists())

    def test_uniform_case_folders_and_manifest_is_not_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for stage in STAGE_FOLDERS:
                run=create_case_run(root,stage,"ULS_X_PLUS",state="ULS",
                                    model_sha256="a"*64,
                                    source_edb_sha256="b"*64)
                for name in RUN_SUBFOLDERS:
                    self.assertTrue((run/name).is_dir())
                manifest=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
                self.assertEqual(manifest["solver_status"],"CREATED")
                self.assertEqual(manifest["structural_acceptance"],"NOT_VERIFIED")
                record_case_status(run,"COMPLETED_SOLVER_ONLY")
                manifest=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
                self.assertEqual(manifest["structural_acceptance"],"NOT_VERIFIED")
                with self.assertRaises(ValueError):
                    record_case_status(run,"VERIFIED_ETABS_EQUIVALENCE")
            self.assertEqual(len(list(root.rglob("CASE_MANIFEST.json"))),len(STAGE_FOLDERS))

    def test_linked_stage_or_case_folder_is_refused_without_external_writes(self):
        for linked_at in ("stage", "runs", "state", "case"):
            with self.subTest(linked_at=linked_at):
                with tempfile.TemporaryDirectory() as td:
                    root = Path(td) / "export"
                    outside = Path(td) / "outside"
                    root.mkdir()
                    outside.mkdir()
                    parts = ("02_GRAVITY", "RUNS", "ULS", "X")
                    depth = {"stage": 0, "runs": 1, "state": 2, "case": 3}[linked_at]
                    link = root.joinpath(*parts[:depth + 1])
                    link.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        link.symlink_to(outside, target_is_directory=True)
                    except (OSError, NotImplementedError):
                        self.skipTest("Host cannot create directory symlinks")
                    with self.assertRaisesRegex(ValueError, "linked run-output"):
                        create_case_run(root, "GRAVITY", "X", state="ULS")
                    self.assertEqual(list(outside.iterdir()), [])
                    self.assertFalse((root / "02_GRAVITY" / "RUNS" / "ULS" / "X" / "00_INPUT_SOURCE" / "CASE_MANIFEST.json").exists())

    def test_path_safety_and_format_writers(self):
        for value in ("../hack","C:/temp","a\\b","CON","COM4","COM9",
                      "LPT4","LPT9","", "A." ):
            with self.assertRaises(ValueError):
                safe_component(value)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            target=atomic_json(root/"s"/"j.json",{"z":2,"a":1})
            self.assertEqual(target.read_text(),'{\n  "a": 1,\n  "z": 2\n}\n')
            table=write_table(root/"s"/"data.csv",[
                {"case":"ULS","kN":100},{"case":"SLS","kN":50}
            ],columns=("case","kN"))
            self.assertEqual(table.read_text(),'case,kN\nULS,100\nSLS,50\n')
            with self.assertRaises(ValueError):
                atomic_json(root/"broken.json",{"nonfinite":float("nan")})
            self.assertFalse((root/"broken.json").exists())

    def test_csv_rejects_nonfinite_numeric_values_without_publishing(self):
        from decimal import Decimal
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for value in (float("nan"), float("inf"), -float("inf"),
                          Decimal("NaN"), Decimal("Infinity")):
                with self.subTest(value=str(value)):
                    target = root / "bad.csv"
                    with self.assertRaisesRegex(ValueError, "Nonfinite numeric CSV"):
                        write_table(target, [{"case": "X", "reaction": value}],
                                    columns=("case", "reaction"))
                    self.assertFalse(target.exists())
                    self.assertEqual(list(root.glob(".writing_*.partial")), [])
            ok = write_table(root / "valid.csv",
                             [{"case": "X", "reaction": -127.5}],
                             columns=("case", "reaction"))
            self.assertEqual(ok.read_text(), "case,reaction\\nX,-127.5\\n")

    def test_csv_rejects_empty_and_nonstring_headers(self):
        with tempfile.TemporaryDirectory() as td:
            for columns in (("",), (" ",), ("case", None), ("case", 5)):
                with self.subTest(columns=columns):
                    with self.assertRaisesRegex(ValueError, "nonempty string"):
                        write_table(Path(td) / "invalid.csv", [], columns=columns)

    def test_excel_style_preserves_values_and_adds_common_header(self):
        from openpyxl import Workbook
        wb=Workbook()
        ws=wb.active
        ws.append(["Source ID","Gravity reaction (kN)"])
        ws.append(["ETABS:263",3041.266])
        style_workbook(wb)
        self.assertEqual(ws["B2"].value,3041.266)
        self.assertEqual(ws["A1"].font.color.rgb,"00FFFFFF")
        self.assertFalse(ws.sheet_view.showGridLines)
        self.assertEqual(ws.freeze_panes,"A2")
        self.assertTrue(ws.auto_filter.ref)

    def test_large_excel_style_preserves_data_and_bounded_column_width(self):
        from openpyxl import Workbook
        book=Workbook()
        sheet=book.active
        sheet.append(("ETABS object","Reaction (kN)","Formula"))
        for i in range(1,1201):
            sheet.append((f"FRAME_{i}",float(i),f"=B{i+1}*2"))
        original=sheet["C1201"].value
        style_workbook(book)
        self.assertEqual(sheet["C1201"].value,original)
        self.assertEqual(sheet["B1201"].value,1200.0)
        self.assertEqual(sheet["C2"].fill.fgColor.rgb,"00F2F5F9")
        self.assertEqual(sheet["B3"].alignment.vertical,"top")
        self.assertLessEqual(sheet.column_dimensions["A"].width,58)
        self.assertTrue(sheet.auto_filter.ref)

    def test_project_layout_canonicalizes_old_callers(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            edb=root/"source.EDB"
            edb.write_bytes(b"unchanged test source")
            out=root/"output"
            ctx=create_project_layout(edb,out)
            self.assertIn("06_LINEAR_TIME_HISTORY",ctx["modules"])
            self.assertNotIn("06_LINEAR_TH",ctx["modules"])
            self.assertIn("02_MODEL",ctx["modules"])
            case=case_folder(ctx,"06_LINEAR_TH","X_PLUS",limit_state="ULS")
            self.assertEqual(case,out/"06_LINEAR_TIME_HISTORY"/"ULS"/"X_PLUS")
            self.assertEqual(edb.read_bytes(),b"unchanged test source")


if __name__ == "__main__":
    unittest.main()
