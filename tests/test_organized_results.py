"""Non-native categorised evidence export tests."""
from __future__ import annotations
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from components.ui.organized_results import classify, publish_organized_results, sha256


class OrganizedReviewTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify("MRSM_Results_V134.xlsx"), "MRSM")
        self.assertEqual(classify("NBC105_ESM_Force_Profile_ULS_X.png"), "ESM")
        self.assertEqual(classify("Gravity_Result_V110.json"), "Gravity")
        self.assertEqual(classify("Modal_ULS/mode_shapes.json"), "Modal")
        self.assertEqual(classify("ETABS_Comparison_V148/Comparison.csv"), "Comparisons")

    def test_classify_time_histories_separately(self):
        self.assertEqual(classify("06_LINEAR_TIME_HISTORY/RUNS/ULS/XY/Deformation.json"),"LinearTH")
        self.assertEqual(classify("07_NONLINEAR_TIME_HISTORY/RUNS/M0/XY/Response.json"),"NonlinearTH")
        self.assertEqual(classify("06_LINEAR_TH/ULS/Linear_Time_History.csv"),"LinearTH")
        self.assertEqual(classify("07_NONLINEAR_TH/NLTHA_XY_Result.json"),"NonlinearTH")
        self.assertEqual(classify("OpenSees_NLTHA_XY_Results.json"),"NonlinearTH")
        self.assertEqual(classify("02_MODEL/SLAB_LOAD_PATH/MESH_04/EXCEL/sheet.xlsx"),"Model")

    def test_stage_folder_owns_ambiguous_file_labels(self):
        self.assertEqual(classify("03_ESM/RUNS/ULS/Gravity_Notes.csv"),"ESM")
        self.assertEqual(classify("04_MODAL/RUNS/ULS/Nonlinear_notes.json"),"Modal")
        self.assertEqual(classify("02_GRAVITY/RUNS/X/Mode_shape.json"),"Gravity")
        self.assertEqual(classify("05_MRSM/RUNS/X/Gravity_load.json"),"MRSM")
        self.assertEqual(classify("08_ETABS_COMPARISONS/RUNS/X/Modal_diff.csv"),
                         "Comparisons")

    def test_archive_excludes_private_source_and_old_sibling_snapshots(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            root.mkdir()
            (root/"03_ESM"/"RUNS").mkdir(parents=True)
            (root/"03_ESM"/"RUNS"/"ESM_Result.json").write_text("{}")
            (root/"ETABS_full_table_original.xlsx").write_bytes(b"CONFIDENTIAL")
            (root/"project_sources.private.json").write_text('{"secret":true}')
            (root/"00_SOURCE_MANIFEST").mkdir()
            (root/"00_SOURCE_MANIFEST"/"PROJECT_CONTEXT.json").write_text('{"private":"path"}')
            (root/"09_SOFTWARE_DIAGNOSTICS").mkdir()
            (root/"09_SOFTWARE_DIAGNOSTICS"/"REPORT.json").write_text("{}")
            parent=root/"EXTERNAL_RESULTS"
            old=parent/"OLD_CASE"
            old.mkdir(parents=True)
            (old/"Gravity_Run.json").write_text('{"old":true}')
            report=publish_organized_results(root,destination_parent=parent)
            manifest=json.loads(Path(report["manifest"]).read_text())
            contents=[x["source"] for x in manifest["entries"]]
            self.assertEqual(len(contents),1)
            self.assertTrue(contents[0].endswith("ESM_Result.json"))
            with zipfile.ZipFile(report["zip_files"]["ALL_MODULES"]) as z:
                public=json.loads(z.read("EVIDENCE_MANIFEST.json"))
                self.assertEqual(public["source_path_policy"],
                                 "LOCAL_PATHS_REDACTED_FOR_UPLOAD_ZIP")
                self.assertEqual(public["entries"][0]["source"],
                                 "<REDACTED_LOCAL_PATH>")
                self.assertNotIn(str(root),z.read("EVIDENCE_MANIFEST.json").decode())
                self.assertEqual(public["entries"][0]["sha256"],
                                 manifest["entries"][0]["sha256"])
            with zipfile.ZipFile(report["zip_files"]["ALL_MODULES"]) as z:
                archive=" ".join(z.namelist())
                self.assertNotIn("ETABS_full_table_original",archive)
                self.assertNotIn("project_sources.private",archive)
                self.assertNotIn("PROJECT_CONTEXT",archive)
                self.assertNotIn("OLD_CASE",archive)

    def test_no_eligible_files_creates_no_empty_review_run(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"case"
            root.mkdir()
            (root/"PRIVATE.EDB").write_bytes(b"private original")
            with self.assertRaisesRegex(ValueError,"No classifiable saved results"):
                publish_organized_results(root)
            self.assertFalse((root/"Organized_Results").exists())

    def test_source_mutating_during_copy_never_updates_latest_pointer(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"case"
            root.mkdir()
            source=root/"Gravity_Result.json"
            source.write_text('{"version":"before"}',encoding="utf-8")
            import components.ui.organized_results as organizer
            original_copy=organizer.shutil.copy2
            def mutate_after_copy(src,dst,*args,**kwargs):
                result=original_copy(src,dst,*args,**kwargs)
                source.write_text('{"version":"changed"}',encoding="utf-8")
                return result
            with patch.object(organizer.shutil,"copy2",side_effect=mutate_after_copy):
                with self.assertRaisesRegex(IOError,"Source or snapshot changed"):
                    publish_organized_results(root)
            self.assertFalse((root/"Organized_Results"/"LATEST_ORGANIZED_RESULT.txt").exists())
            self.assertEqual(source.read_text(), '{"version":"changed"}')

    def test_symlinked_source_and_latest_output_link_are_refused(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            original=base/"private"
            original.mkdir()
            (original/"Gravity_Result.json").write_text('{"private":true}')
            alias=base/"linked"
            try:
                alias.symlink_to(original,target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Directory symlinks not supported")
            with self.assertRaisesRegex(ValueError,"linked organized-result"):
                publish_organized_results(alias)
            self.assertFalse((original/"Organized_Results").exists())

            selected=base/"selected"
            selected.mkdir()
            (selected/"Gravity_Result.json").write_text('{"result":1}')
            parent=selected/"Organized_Results"
            parent.mkdir()
            target=base/"outside_pointer.txt"
            target.write_text("keep this private pointer")
            try:
                (parent/"LATEST_ORGANIZED_RESULT.txt").symlink_to(target)
            except (OSError,NotImplementedError):
                self.skipTest("File symlinks not supported")
            with self.assertRaisesRegex(ValueError,"linked organized-result"):
                publish_organized_results(selected)
            self.assertEqual(target.read_text(),"keep this private pointer")
            self.assertFalse(any(p.is_dir() for p in parent.iterdir()))

    def test_bundle_name_cannot_replace_module_archive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Gravity_Result.json").write_text("{}")
            (root / "Modal_Result.json").write_text("{}")
            for bundle in ("Gravity", "GRAVITY"):
                with self.subTest(bundle=bundle):
                    with self.assertRaisesRegex(ValueError, "module archive"):
                        publish_organized_results(root, bundle_name=bundle)
                    self.assertFalse((root / "Organized_Results").exists())

    def test_module_archive_totals_match_its_contents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "Gravity_Result.json").write_text("{}")
            (root / "Modal_Result.json").write_text("{}")
            result = publish_organized_results(root)
            for archive, expected in (
                    ("Gravity", {"Gravity": 1}),
                    ("Modal", {"Modal": 1}),
                    ("ALL_MODULES", {"Gravity": 1, "Modal": 1})):
                with self.subTest(archive=archive):
                    with zipfile.ZipFile(result["zip_files"][archive]) as package:
                        manifest = json.loads(package.read("EVIDENCE_MANIFEST.json"))
                        for entry in manifest["entries"]:
                            self.assertIn(entry["snapshot"], package.namelist())
                    self.assertEqual(manifest["file_count"], sum(expected.values()))
                    self.assertEqual(
                        {name: count for name, count in manifest["modules"].items() if count},
                        expected)

    def test_bundle_name_rejects_windows_reserved_names(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"Gravity_Result.json").write_text("{}")
            for bad in ("COM4","LPT9","../bad","C:\\temp","A."):
                with self.assertRaises(ValueError):
                    publish_organized_results(root,bundle_name=bad)
            self.assertFalse((root/"Organized_Results").exists())

    def test_time_history_files_get_dedicated_review_zip(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"case"
            root.mkdir()
            linear=root/"06_LINEAR_TIME_HISTORY"/"RUNS"/"ULS"/"LTH_XY.json"
            nonlinear=root/"07_NONLINEAR_TIME_HISTORY"/"RUNS"/"M0"/"NLTHA_XY.json"
            for file in (linear,nonlinear):
                file.parent.mkdir(parents=True,exist_ok=True)
                file.write_text('{"solver_status":"INCOMPLETE"}')
            pack=publish_organized_results(root)
            self.assertIn("LinearTH",pack["zip_files"])
            self.assertIn("NonlinearTH",pack["zip_files"])
            self.assertEqual(pack["status"],"OUTPUT_INDEX_NOT_ENGINEERING_ACCEPTANCE")
            for stage in ("LinearTH","NonlinearTH"):
                with zipfile.ZipFile(pack["zip_files"][stage]) as archive:
                    self.assertIn("EVIDENCE_MANIFEST.json",archive.namelist())

    def test_preserves_sources_exports_distinct_zip_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "ULS_MODEL_A"
            root.mkdir()
            files = {
                "MRSM_ULS/MRSM_Results_V132.json": b'{"completed":true}',
                "Gravity_Result_V110.json": b'{"ok":true}',
                "NBC105_ESM_Force_Profile_ULS_X.png": b"test illustration",
                "Modal_ULS/Modal_Periods.csv": b"mode,T\n1,2.38",
                "ETABS_Comparison_V148/Comparison.csv": b"status\nMISSING_ETABS",
                "RUN_NOTES.txt": b"test notes",
                "SourceModel.EDB": b"PRIVATE EDB",
                "Seismic_Review_Packages/OLD_UPLOAD.zip": b"archived prior run",
            }
            for name, data in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            original_hash = sha256(root / "MRSM_ULS/MRSM_Results_V132.json")
            result = publish_organized_results(root)
            self.assertEqual(result["status"], "OUTPUT_INDEX_NOT_ENGINEERING_ACCEPTANCE")
            self.assertEqual(result["file_count"], 6)
            archive = Path(result["zip_files"]["ALL_MODULES"])
            with zipfile.ZipFile(archive) as z:
                names = set(z.namelist())
                self.assertIn("MRSM/Analysis/MRSM_ULS/MRSM_Results_V132.json", names)
                self.assertIn("Unclassified/Analysis/RUN_NOTES.txt", names)
                self.assertIn("EVIDENCE_MANIFEST.json", names)
                self.assertFalse(any(x.endswith(".EDB") for x in names))
                self.assertFalse(any("OLD_UPLOAD.zip" in x for x in names))
            self.assertEqual(sha256(root / "MRSM_ULS/MRSM_Results_V132.json"), original_hash)
            manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["entries"]), 6)
            again = publish_organized_results(root)
            self.assertEqual(again["file_count"], 6)
            self.assertNotEqual(result["folder"], again["folder"])

    def test_gravity_review_under_export_02_gravity_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / "Export_02"
            root = export / "OpenSees_Analysis_Results" / "ULS_Model"
            gravity = export / "02_GRAVITY" / "SOURCE_RUNS"
            root.mkdir(parents=True)
            gravity.mkdir(parents=True)
            (root / "Gravity_Result_V110.json").write_text('{"ok":true}')
            (root / "Modal_Results.json").write_text('{"modal":true}')
            (root / "ETABS_Comparison.csv").write_text("source,open\\n1,1\\n")
            (gravity / "Gravity_Run_V110.log").write_text("gravity log")
            home = export / "02_GRAVITY" / "REVIEW_SNAPSHOTS"
            first = publish_organized_results(
                root, gravity_root=gravity, destination_parent=home,
                selected_modules=("Gravity", "Comparisons"),
                bundle_name="GRAVITY_REVIEW")
            self.assertTrue(Path(first["folder"]).is_relative_to(home))
            self.assertIn("GRAVITY_REVIEW", first["zip_files"])
            with zipfile.ZipFile(first["zip_files"]["GRAVITY_REVIEW"]) as z:
                entries = z.namelist()
                self.assertTrue(any("Gravity_Result_V110.json" in n for n in entries))
                self.assertTrue(any("ETABS_Comparison.csv" in n for n in entries))
                self.assertFalse(any("Modal_Results.json" in n for n in entries))
            self.assertTrue((root / "Gravity_Result_V110.json").exists())
            # A second snapshot must not recursively copy the first review.
            second = publish_organized_results(
                root, gravity_root=gravity, destination_parent=home,
                selected_modules=("Gravity", "Comparisons"),
                bundle_name="GRAVITY_REVIEW")
            self.assertEqual(first["file_count"], second["file_count"])

    def test_separate_gravity_output_can_be_packaged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "analysis"
            gravity = Path(tmp) / "gravity_gui"
            root.mkdir()
            gravity.mkdir()
            (root / "MRSM_Results_V134.json").write_text("{}")
            (gravity / "Gravity_Result_V110.json").write_text('{"ok":true}')
            result = publish_organized_results(root, gravity_root=gravity)
            self.assertIn("Gravity", result["zip_files"])
            manifest = json.loads(Path(result["manifest"]).read_text())
            self.assertTrue(any(row["source_root"] == str(gravity.resolve())
                                for row in manifest["entries"]))


if __name__ == "__main__":
    unittest.main()
