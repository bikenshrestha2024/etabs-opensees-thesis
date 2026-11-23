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
    # Windows temp paths may use 8.3 RUNNER~1 aliases; the production
    # output API intentionally returns resolved physical paths. Compare
    # canonical paths rather than syntactic spellings of the same folder.
    def test_result_roots_legacy_fallback_accepts_all_stage_spellings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for key, canonical, alias in (
                    ("LTHA", "06_LINEAR_TIME_HISTORY", "06_LINEAR_TH"),
                    ("NLTHA", "07_NONLINEAR_TIME_HISTORY", "07_NONLINEAR_TH")):
                legacy = root / alias
                legacy.mkdir()
                for stage in (key, canonical, alias, f" {key.lower()} "):
                    with self.subTest(stage=stage):
                        self.assertEqual(
                            result_roots(root, stages=(stage,), include_legacy=False),
                            (legacy.resolve(),))

    def test_selected_folder_inside_wrong_stage_is_not_discovered(self):
        # An ESM review snapshot or results subfolder must never re-enter a
        # Modal/MRSM-only search as an arbitrary user-selected source.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            modal=root/"04_MODAL"/"RUNS"/"ULS"/"one"
            mrsm=root/"05_MRSM"/"RUNS"/"ULS"/"two"
            esm=root/"03_ESM"/"REVIEW_SNAPSHOTS"/"old"
            for path in (modal,mrsm,esm):
                path.mkdir(parents=True)
            self.assertEqual(
                result_roots(esm,stages=("MODAL",),include_legacy=False),
                (root/"04_MODAL",))
            self.assertEqual(
                result_roots(modal,stages=("MRSM",),include_legacy=False),
                (root/"05_MRSM",))
            self.assertEqual(
                set(result_roots(esm,stages=("MODAL","ESM"),
                                 include_legacy=False)),
                {root/"04_MODAL",root/"03_ESM"})
            self.assertFalse((root/"OpenSees_Analysis_Results").exists())

    def test_every_stage_excludes_all_other_stage_selected_folders(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            selected={
                stage:root/folder/"REVIEW_SNAPSHOTS"/"sample"
                for stage,folder in STAGE_FOLDERS.items()
            }
            for path in selected.values():
                path.mkdir(parents=True)
            for wanted,wanted_folder in STAGE_FOLDERS.items():
                for passed,selected_path in selected.items():
                    with self.subTest(wanted=wanted,selected_stage=passed):
                        roots=result_roots(selected_path,stages=(wanted,),
                                           include_legacy=False)
                        self.assertEqual(roots,(root/wanted_folder,))
                        self.assertTrue(all(wanted_folder in str(p) for p in roots))

    def test_unstructured_export_root_does_not_invent_modal_results(self):
        with tempfile.TemporaryDirectory() as td:
            external=Path(td)/"scratch"
            external.mkdir()
            self.assertEqual(result_roots(external,stages=("MODAL",),
                                          include_legacy=False),())

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
            self.assertEqual(export_root_for(legacy),root.resolve())
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
                self.assertEqual(export_root_for(nested),root.resolve())
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

    def test_inspect_manifest_reports_nonscalar_solver_status(self):
        from components.inputs.output_contract import inspect_case_manifest

        with tempfile.TemporaryDirectory() as td:
            run = create_case_run(Path(td), "GRAVITY", "gravity", state="ULS")
            manifest = run / "00_INPUT_SOURCE" / "CASE_MANIFEST.json"
            original = json.loads(manifest.read_text(encoding="utf-8"))
            for invalid_status in ([], {}):
                with self.subTest(status=invalid_status):
                    manifest.write_text(json.dumps({
                        **original, "solver_status": invalid_status,
                    }), encoding="utf-8")
                    result = inspect_case_manifest(run)
                    self.assertFalse(result["valid"])
                    self.assertIn("INVALID_SOLVER_STATUS", result["issues"])

    def test_record_status_refuses_wrong_run_identity_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            run=create_case_run(root,"MRSM","X_E0",state="ULS")
            manifest=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            baseline=manifest.read_bytes()
            original=json.loads(baseline)
            for field,value in (("case_id","OTHER"),("stage","03_ESM"),
                                ("run_id","wrong_run"),("units","not_a_unit")):
                damaged=dict(original)
                damaged[field]=value
                manifest.write_text(json.dumps(damaged),encoding="utf-8")
                unchanged=manifest.read_bytes()
                with self.subTest(field=field):
                    with self.assertRaisesRegex(ValueError,"invalid case manifest"):
                        record_case_status(run,"RUNNING")
                    self.assertEqual(manifest.read_bytes(),unchanged)
            manifest.write_bytes(baseline)
            record_case_status(run,"RUNNING")
            self.assertEqual(json.loads(manifest.read_text())["solver_status"],"RUNNING")

    def test_manifest_refuses_symlinked_parent_stage_before_reading(self):
        from components.inputs.output_contract import inspect_case_manifest
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outside=root/"outside"
            outside.mkdir()
            actual=create_case_run(outside,"GRAVITY","X_E0",state="ULS")
            manifest=actual/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            original=manifest.read_bytes()
            project=root/"project"
            project.mkdir()
            linked=project/"02_GRAVITY"
            try:
                linked.symlink_to(outside/"02_GRAVITY",target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Directory symlinks unavailable")
            alias=linked/"RUNS"/"ULS"/"X_E0"/actual.name
            checked=inspect_case_manifest(alias)
            self.assertFalse(checked["valid"])
            self.assertIn("LINKED_CASE_MANIFEST_PATH",checked["issues"])
            self.assertEqual(manifest.read_bytes(),original)
            with self.assertRaisesRegex(ValueError,"invalid case manifest"):
                record_case_status(alias,"COMPLETED_SOLVER_ONLY")
            self.assertEqual(manifest.read_bytes(),original)

    def test_record_status_refuses_linked_case_manifest(self):
        from components.inputs.output_contract import inspect_case_manifest
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            run=create_case_run(root,"MRSM","X_E0",state="ULS")
            manifest=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            actual=root/"original.json"
            actual.write_bytes(manifest.read_bytes())
            manifest.unlink()
            try:
                manifest.symlink_to(actual)
            except (OSError,NotImplementedError):
                self.skipTest("File symlink unavailable")
            result=inspect_case_manifest(run)
            self.assertFalse(result["valid"])
            self.assertIn("LINKED_CASE_MANIFEST_PATH",result["issues"])
            before=actual.read_bytes()
            with self.assertRaisesRegex(ValueError,"invalid case manifest"):
                record_case_status(run,"RUNNING")
            self.assertEqual(before,actual.read_bytes())

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

    def test_shared_writers_refuse_linked_parent_or_target(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outside=root/"outside"
            outside.mkdir()
            link=root/"redirected"
            try:
                link.symlink_to(outside,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host lacks symbolic link support")
            for writer in ("json","csv"):
                dest=link/("report."+writer)
                with self.subTest(writer=writer):
                    with self.assertRaisesRegex(ValueError,"linked derived-output"):
                        if writer=="json":
                            atomic_json(dest,{"valid":True})
                        else:
                            write_table(dest,[{"value":1}],columns=("value",))
                    self.assertFalse(dest.exists())
            normal=root/"protected.json"
            normal.write_text('{"unchanged":true}',encoding="utf-8")
            linked_file=root/"alias.json"
            linked_file.symlink_to(normal)
            with self.assertRaisesRegex(ValueError,"linked derived-output"):
                atomic_json(linked_file,{"valid":False})
            self.assertEqual(normal.read_text(), '{"unchanged":true}')
            self.assertTrue(linked_file.is_symlink())

    def test_manifest_stage_identity_validated_without_expected_stage(self):
        from components.inputs.output_contract import inspect_case_manifest
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run = create_case_run(root, "GRAVITY", "X", state="ULS")
            original = run / "00_INPUT_SOURCE" / "CASE_MANIFEST.json"
            result = inspect_case_manifest(run)
            self.assertTrue(result["valid"], result["issues"])
            for false_stage, issue in (
                ("05_MRSM", "RUN_STAGE_DIRECTORY_MISMATCH"),
                ("NOT_A_STAGE", "UNKNOWN_RECORDED_STAGE"),
                ("GRAVITY", "NONCANONICAL_RECORDED_STAGE"),
            ):
                data = json.loads(original.read_text(encoding="utf-8"))
                data["stage"] = false_stage
                original.write_text(json.dumps(data), encoding="utf-8")
                with self.subTest(false_stage=false_stage):
                    audit = inspect_case_manifest(run)
                    self.assertFalse(audit["valid"])
                    self.assertIn(issue, audit["issues"])

    def test_no_missing_or_boolean_case_identifiers(self):
        for invalid in (None,True,False):
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(ValueError,"Unsafe run/case"):
                    safe_component(invalid)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(ValueError,"Unsafe run/case"):
                create_case_run(root,"GRAVITY",None,state="ULS")
            self.assertFalse((root/"02_GRAVITY").exists())

    def test_manifest_rejects_noncanonical_identifier_without_repair(self):
        from components.inputs.output_contract import inspect_case_manifest
        with tempfile.TemporaryDirectory() as td:
            run=create_case_run(Path(td),"GRAVITY","X_E0",state="ULS")
            manifest=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            original=json.loads(manifest.read_text())
            for field,bad in (("case_id"," X_E0 "),
                              ("case_id",None),
                              ("state",True),
                              ("run_id",run.name+" ")):
                changed=dict(original)
                changed[field]=bad
                manifest.write_text(json.dumps(changed))
                with self.subTest(field=field,bad=bad):
                    checked=inspect_case_manifest(run)
                    self.assertFalse(checked["valid"])
                    self.assertIn("INVALID_"+field.upper(),checked["issues"])
            self.assertEqual(
                json.loads(manifest.read_text())["run_id"],run.name+" ")

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
            self.assertEqual(ok.read_text(), "case,reaction\nX,-127.5\n")

    def test_csv_rejects_numpy_nonfinite_scalars_when_available(self):
        try:
            import numpy as np
        except ImportError:
            self.skipTest("NumPy not installed in optional isolated test environment")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for value in (np.float32("nan"), np.float32("inf"),
                          np.float64("-inf")):
                target = root / "nonfinite_numpy.csv"
                with self.subTest(dtype=str(type(value))):
                    with self.assertRaisesRegex(ValueError, "Nonfinite numeric CSV"):
                        write_table(target, [{"result": value}], columns=("result",))
                    self.assertFalse(target.exists())

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
            self.assertEqual(case,(out/"06_LINEAR_TIME_HISTORY"/"ULS"/"X_PLUS").resolve())
            self.assertEqual(edb.read_bytes(),b"unchanged test source")


if __name__ == "__main__":
    unittest.main()
