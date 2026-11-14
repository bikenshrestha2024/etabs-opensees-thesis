"""Uniform project-stage and case output verification; filesystem-only tests.

[REF docs/source/components/inputs/output_contract.py.md]
"""
import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook
from components.inputs.output_contract import create_case_run,inspect_case_manifest
from components.inputs.output_layout import STAGE_FOLDERS,AUXILIARY_FOLDERS
from tools.audit_stage_output_migration import (
    audit_stage_migration,export_uniform_inventory_excel,
)


class UniformStageInventoryTests(unittest.TestCase):
    def test_every_stage_consistent_with_auxiliary_and_formatted_workbook(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for stage in STAGE_FOLDERS:
                create_case_run(root,stage,"Case_1",state="ULS",
                                model_sha256="a"*64)
            original=root/"original.EDB"
            original.write_bytes(b"original sensitive source unchanged")
            stage_report=audit_stage_migration(root)
            self.assertEqual(stage_report["summary"]["run_manifest_count"],len(STAGE_FOLDERS))
            self.assertEqual(stage_report["summary"]["invalid_case_contract_count"],0)
            self.assertEqual(len(stage_report["auxiliary_folders"]),len(AUXILIARY_FOLDERS))
            self.assertEqual(stage_report["summary"]["engineering_acceptance"],
                             "NOT_ESTABLISHED_BY_FILESYSTEM_AUDIT")
            report=root/"local_audit.xlsx"
            export_uniform_inventory_excel(stage_report,report)
            book=load_workbook(report)
            self.assertEqual(book.sheetnames,[
                "Stage summary","Case registry","Missing or inconsistent",
                "Auxiliary folders","Read first"
            ])
            self.assertEqual(book["Case registry"].max_row,len(STAGE_FOLDERS)+1)
            self.assertEqual(book["Case registry"]["E2"].value,"CREATED")
            self.assertFalse(book["Case registry"].sheet_view.showGridLines)
            self.assertEqual(book["Case registry"].freeze_panes,"A2")
            self.assertEqual(original.read_bytes(),b"original sensitive source unchanged")
            with self.assertRaises(FileExistsError):
                export_uniform_inventory_excel(stage_report,report)

    def test_missing_subfolder_and_incorrect_manifest_identity_are_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            run=create_case_run(root,"GRAVITY","Support_32",state="ULS")
            self.assertTrue(inspect_case_manifest(run,expected_stage="GRAVITY")["valid"])
            (run/"05_COMPARISONS").rmdir()
            manifest=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            data=json.loads(manifest.read_text())
            data["case_id"]="Different_Source_Case"
            manifest.write_text(json.dumps(data))
            inspected=inspect_case_manifest(run,expected_stage="GRAVITY")
            self.assertFalse(inspected["valid"])
            self.assertIn("MISSING_05_COMPARISONS",inspected["issues"])
            self.assertIn("RUN_DIRECTORY_IDENTITY_MISMATCH",inspected["issues"])
            summary=audit_stage_migration(root)
            self.assertEqual(summary["summary"]["invalid_case_contract_count"],1)
            self.assertEqual(summary["stages"][1]["run_manifest_count"],1)
            self.assertEqual(summary["stages"][1]["unreadable_or_invalid_manifests"][0]["problem"],
                             "INVALID_CASE_CONTRACT")

    def test_invalid_and_missing_manifest_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            run=Path(td)/"02_GRAVITY"/"RUNS"/"ULS"/"case"/"run1"
            run.mkdir(parents=True)
            issue=inspect_case_manifest(run,expected_stage="GRAVITY")
            self.assertEqual(issue["issues"],["MISSING_CASE_MANIFEST"])
            src=run/"00_INPUT_SOURCE"
            src.mkdir()
            (src/"CASE_MANIFEST.json").write_text("{bad")
            issue=inspect_case_manifest(run,expected_stage="GRAVITY")
            self.assertEqual(issue["issues"],["UNREADABLE_CASE_MANIFEST"])


if __name__=="__main__":
    unittest.main()
