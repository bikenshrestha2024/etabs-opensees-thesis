"""Source-bound compact manifested run folders across all canonical stages.

Synthetic temporary exports only. No ETABS, solver or private EDB access.
[REF docs/source/components/inputs/output_contract.py.md]
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import (
    compact_case_id, create_case_run, inspect_case_manifest, record_case_status)
from components.inputs.output_layout import ALL_STAGE_FOLDERS

NAME_A = "ULS_Floor_3_ULTIMATE_LOAD_NEPAL_3_BELT_TRUSS_OUTRIGGER_CAP_TRUSS_Copy_NBC105_RS_SCALE"
NAME_B = NAME_A[:-5] + "OTHER"


class CompactManifestedRunTests(unittest.TestCase):
    def test_all_canonical_stage_folders_compact_long_hashed_names(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for stage, folder in ALL_STAGE_FOLDERS.items():
                with self.subTest(stage=stage):
                    run = create_case_run(
                        root, stage, NAME_A, state="ULS",
                        model_sha256="a"*64, source_edb_sha256="b"*64)
                    self.assertLessEqual(len(run.parent.name), 48)
                    self.assertTrue(run.is_relative_to(root/folder/"RUNS"/"ULS"))
                    manifest_path=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
                    data=json.loads(manifest_path.read_text(encoding="utf-8"))
                    self.assertEqual(data["original_case_id"], NAME_A)
                    self.assertEqual(data["case_label_mode"], "COMPACT_SOURCE_BOUND")
                    self.assertEqual(data["compact_source_basis"], "MODEL_SHA256")
                    self.assertEqual(data["case_id"],run.parent.name)
                    self.assertEqual(data["source_edb_sha256"],"b"*64)
                    self.assertTrue(inspect_case_manifest(run)["valid"])
                    record_case_status(run,"COMPLETED_SOLVER_ONLY")
                    self.assertEqual(inspect_case_manifest(run)["engineering_acceptance"],
                                     "NOT_VERIFIED")

    def test_source_and_full_scope_avoid_colliding_truncated_case_names(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a=create_case_run(root,"ESM",NAME_A,model_sha256="a"*64)
            b=create_case_run(root,"ESM",NAME_A,model_sha256="c"*64)
            c=create_case_run(root,"ESM",NAME_B,model_sha256="a"*64)
            self.assertEqual(len({a.parent.name,b.parent.name,c.parent.name}),3)
            self.assertNotEqual(
                compact_case_id("ESM",NAME_A,"a"*64),
                compact_case_id("ESM",NAME_B,"a"*64))

    def test_source_edb_fingerprint_used_if_no_assembled_model_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            run=create_case_run(root,"GRAVITY",NAME_A,source_edb_sha256="f"*64)
            data=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
            self.assertEqual(data["compact_source_basis"],"SOURCE_EDB_SHA256")
            self.assertTrue(run.parent.name.endswith("f"*12))
            self.assertTrue(inspect_case_manifest(run)["valid"])

    def test_legacy_unhashed_and_existing_short_names_keep_exact_path(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            long_unhashed=create_case_run(root,"MODAL",NAME_A,state="SLS")
            self.assertEqual(long_unhashed.parent.name,NAME_A)
            short=create_case_run(root,"MRSM","X_E0",state="ULS",model_sha256="a"*64)
            self.assertEqual(short.parent.name,"X_E0")
            for run in (long_unhashed,short):
                manifest=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
                data=json.loads(manifest.read_text())
                self.assertEqual(data["case_label_mode"],"EXACT")
                self.assertEqual(data["original_case_id"],run.parent.name)
                self.assertTrue(inspect_case_manifest(run)["valid"])
                data.pop("case_label_mode")
                data.pop("original_case_id")
                data.pop("compact_source_basis",None)
                manifest.write_text(json.dumps(data))
                self.assertTrue(inspect_case_manifest(run)["valid"])

    def test_tampered_original_scope_or_basis_invalidates_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            run=create_case_run(root,"NLTHA",NAME_A,model_sha256="a"*64)
            path=run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            source=json.loads(path.read_text())
            for key,value in (
                ("original_case_id",NAME_B),
                ("model_sha256","c"*64),
                ("compact_source_basis","SOURCE_EDB_SHA256"),
                ("case_label_mode","UNKNOWN"),
            ):
                with self.subTest(key=key):
                    damaged={**source,key:value}
                    path.write_text(json.dumps(damaged),encoding="utf-8")
                    result=inspect_case_manifest(run)
                    self.assertFalse(result["valid"])
                    self.assertIn("COMPACT_CASE_ID_MISMATCH",result["issues"])
                    with self.assertRaisesRegex(ValueError,"invalid case manifest"):
                        record_case_status(run,"RUNNING")
            path.write_text(json.dumps(source))
            self.assertTrue(inspect_case_manifest(run)["valid"])

    def test_invalid_paths_and_hashes_fail_without_output_writes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for unsafe in ("../escape","../../sneak","con",None,True):
                with self.subTest(name=unsafe):
                    with self.assertRaises(ValueError):
                        create_case_run(root,"MODEL",unsafe,model_sha256="a"*64)
            with self.assertRaises(ValueError):
                create_case_run(root,"MODAL",NAME_A,model_sha256="bad hash")
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
