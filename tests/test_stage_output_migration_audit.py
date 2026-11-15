"""Audit-only stage verification is non-mutating unless --write is requested."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import create_case_run, record_case_status
from tools.audit_stage_output_migration import audit_stage_migration


class NativeStageMigrationAuditTests(unittest.TestCase):
    def test_dry_run_and_explicit_write_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"OpenSees_Analysis_Results"/"older").mkdir(parents=True)
            modal=create_case_run(root,"MODAL","X_MODE",state="ULS")
            record_case_status(modal,"COMPLETED_SOLVER_ONLY")
            first=audit_stage_migration(root)
            self.assertTrue(first["legacy_analysis_root_exists"])
            modal_entry=next(x for x in first["stages"] if x["stage"]=="MODAL")
            self.assertEqual(modal_entry["run_manifest_count"],1)
            self.assertEqual(modal_entry["solver_status_counts"]["COMPLETED_SOLVER_ONLY"],1)
            self.assertEqual(modal_entry["cases"][0]["engineering_acceptance"],"NOT_VERIFIED")
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())
            script=Path(__file__).resolve().parents[1]/"tools"/"audit_stage_output_migration.py"
            completed=subprocess.run([sys.executable,str(script),str(root)],
                                     capture_output=True,text=True,check=True)
            self.assertIn("FILESYSTEM ONLY",completed.stdout)
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())
            subprocess.run([sys.executable,str(script),str(root),"--write"],
                           capture_output=True,text=True,check=True)
            base=root/"09_SOFTWARE_DIAGNOSTICS"/"MIGRATION_AUDITS"/"RUNS"
            files=list(base.glob("*/JSON/Live_Stage_Output_Audit.json"))
            excels=list(base.glob("*/EXCEL/Live_Stage_Output_Audit.xlsx"))
            self.assertEqual(len(files),1)
            self.assertEqual(len(excels),1)
            self.assertEqual(files[0].parent.parent,excels[0].parent.parent)
            data=json.loads(files[0].read_text())
            self.assertEqual(data["schema"],"THESIS_LIVE_STAGE_OUTPUT_MIGRATION_AUDIT_V1")
            self.assertEqual(data["assessment"],"FILESYSTEM_ONLY_NOT_SOLVER_OR_ETABS_EQUIVALENCE")


    def test_unmanifested_run_folders_and_linked_cases_are_visible(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"export"
            missing=root/"02_GRAVITY"/"RUNS"/"ULS"/"X"/"run_without_manifest"
            missing.mkdir(parents=True)
            reference=root/"02_GRAVITY"/"RUNS"/"ULS"/"Y"
            external=Path(td)/"external"
            external.mkdir()
            try:
                reference.symlink_to(external, target_is_directory=True)
            except (OSError,NotImplementedError):
                self.skipTest("Host cannot create a directory symlink")
            before=list(external.iterdir())
            report=audit_stage_migration(root)
            gravity=next(x for x in report["stages"] if x["stage"]=="GRAVITY")
            problems={row["problem"] for row in gravity["unreadable_or_invalid_manifests"]}
            self.assertIn("MISSING_CASE_MANIFEST",problems)
            self.assertIn("SYMLINKED_RUN_CASE_REFUSED",problems)
            self.assertEqual(gravity["missing_run_manifest_count"],1)
            self.assertEqual(gravity["linked_run_path_count"],1)
            self.assertEqual(report["summary"]["missing_run_manifest_count"],1)
            self.assertEqual(report["summary"]["linked_run_path_count"],1)
            self.assertEqual(gravity["run_manifest_count"],0)
            self.assertEqual(list(external.iterdir()),before)
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())

    def test_linked_input_folder_or_manifest_is_never_counted_as_local_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"selected_case"
            root.mkdir()
            external=Path(td)/"outside"
            external.mkdir()
            outside_manifest=external/"CASE_MANIFEST.json"
            outside_manifest.write_text('{"private":"untouched"}', encoding="utf-8")
            original=outside_manifest.read_bytes()
            for case_id, linked_at, problem in (
                ("LINKED_INPUT", "directory", "SYMLINKED_RUN_INPUT_SOURCE_REFUSED"),
                ("LINKED_FILE", "file", "SYMLINKED_RUN_MANIFEST_REFUSED"),
            ):
                run=root/"04_MODAL"/"RUNS"/"ULS"/case_id/"run001"
                run.mkdir(parents=True)
                source=run/"00_INPUT_SOURCE"
                try:
                    if linked_at=="directory":
                        source.symlink_to(external, target_is_directory=True)
                    else:
                        source.mkdir()
                        (source/"CASE_MANIFEST.json").symlink_to(outside_manifest)
                except (OSError,NotImplementedError):
                    self.skipTest("Host does not allow symlinks")
                report=audit_stage_migration(root)
                modal=next(row for row in report["stages"]
                           if row["stage"]=="MODAL")
                problems={item["problem"] for item in
                          modal["unreadable_or_invalid_manifests"]}
                self.assertIn(problem, problems)
                self.assertEqual(modal["run_manifest_count"],0)
                self.assertEqual(modal["linked_run_path_count"],
                                 1 if linked_at=="directory" else 2)
                self.assertEqual(modal["solver_status_counts"],{})
                self.assertEqual(outside_manifest.read_bytes(),original)
            self.assertFalse((root/"09_SOFTWARE_DIAGNOSTICS").exists())

    def test_write_refuses_linked_migration_audit_destinations(self):
        from tools.audit_stage_output_migration import main
        for segment in ("09_SOFTWARE_DIAGNOSTICS",
                        "09_SOFTWARE_DIAGNOSTICS/MIGRATION_AUDITS",
                        "09_SOFTWARE_DIAGNOSTICS/MIGRATION_AUDITS/RUNS"):
            with self.subTest(segment=segment):
                with tempfile.TemporaryDirectory() as td:
                    root=Path(td)/"export"
                    root.mkdir()
                    outside=Path(td)/"outside"
                    outside.mkdir()
                    link=root/segment
                    link.parent.mkdir(parents=True,exist_ok=True)
                    try:
                        link.symlink_to(outside,target_is_directory=True)
                    except (OSError,NotImplementedError):
                        self.skipTest("Host cannot create symlinks")
                    with self.assertRaisesRegex(ValueError,"linked migration-audit"):
                        main([str(root),"--write"])
                    self.assertEqual(list(outside.iterdir()), [])

    def test_nonobject_manifest_is_reported_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            run=root/"04_MODAL"/"RUNS"/"ULS"/"X"/"abc"/"00_INPUT_SOURCE"
            run.mkdir(parents=True)
            (run/"CASE_MANIFEST.json").write_text('["not", "a", "record"]')
            report=audit_stage_migration(root)
            modal=next(x for x in report["stages"] if x["stage"]=="MODAL")
            self.assertEqual(modal["run_manifest_count"],0)
            self.assertEqual(modal["unreadable_or_invalid_manifests"][0]["problem"],
                             "NONOBJECT_CASE_MANIFEST")



if __name__=="__main__":
    unittest.main()
