"""Regression: one manifest records the exact source-script SHA for Modal/LTHA/NLTHA.

Synthetic files only; no native ETABS/OpenSees solver or EDB data.
[REF docs/source/components/inputs/output_contract.py.md]
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.inputs.output_contract import (
    compact_case_id, create_case_run, inspect_case_manifest, prepare_history_run,
    record_case_status,
)
from components.inputs.project_workbooks import analysis_output_folder
from components.modal.gui_and_reports import prepare_canonical_modal_run


class ModalSourceCaseIdentityTests(unittest.TestCase):
    def test_modal_long_label_is_compact_and_exact_source_script_sha_is_declared(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)/("PROJECT_BELT_TRUSS_OUTRIGGER_CAP_" * 3)
            root.mkdir()
            source = root/"OpenSees_Complete_Linear_Model.py"
            source.write_text("one = 1\n", encoding="utf-8")
            original = analysis_output_folder(root, "ULS").name
            self.assertGreater(len(original), 48)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            a = prepare_canonical_modal_run(root, "ULS", source)
            b = prepare_canonical_modal_run(root, "ULS", source)
            self.assertNotEqual(a, b)
            self.assertEqual(a.parent, b.parent)
            self.assertEqual(a.parent.name, compact_case_id("MODAL", original, digest))
            self.assertLessEqual(len(a.parent.name), 48)
            manifest = json.loads((a/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
            evidence = json.loads((a/"00_INPUT_SOURCE"/"MODAL_INPUT_PROVENANCE.json").read_text())
            self.assertEqual(manifest["source_script_sha256"], digest)
            self.assertEqual(manifest["original_case_id"], original)
            self.assertEqual(manifest["compact_source_basis"], "SOURCE_SCRIPT_SHA256")
            self.assertEqual(evidence["model_script_sha256"], digest)
            self.assertIsNone(manifest["model_sha256"])
            self.assertIsNone(manifest["source_edb_sha256"])
            self.assertIsNone(evidence["assembled_model_sha256"])
            self.assertTrue(inspect_case_manifest(a, expected_stage="MODAL")["valid"])
            self.assertEqual(inspect_case_manifest(a)["engineering_acceptance"], "NOT_VERIFIED")
            record_case_status(a, "COMPLETED_SOLVER_ONLY")
            self.assertEqual(inspect_case_manifest(a)["engineering_acceptance"], "NOT_VERIFIED")
            self.assertEqual(source.read_text(encoding="utf-8"), "one = 1\n")

    def test_changed_script_produces_new_case_not_renamed_old_results(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)/("LONG_MODAL_MODEL_" * 5)
            root.mkdir()
            source = root/"Model.py"
            source.write_text("x = 1\n", encoding="utf-8")
            a = prepare_canonical_modal_run(root, "SLS", source)
            old_digest = hashlib.sha256(source.read_bytes()).hexdigest()
            source.write_text("x = 2\n", encoding="utf-8")
            b = prepare_canonical_modal_run(root, "SLS", source)
            self.assertNotEqual(a.parent, b.parent)
            self.assertTrue(a.is_dir())
            self.assertTrue(inspect_case_manifest(a)["valid"])
            self.assertTrue(inspect_case_manifest(b)["valid"])
            self.assertEqual(json.loads((a/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())["source_script_sha256"], old_digest)

    def test_compact_script_hash_or_basis_mutation_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            long_name="ULS_Floor_3_"+"X_OUTRIGGER_CAP_"*6
            a=create_case_run(root,"MODAL",long_name,source_script_sha256="a"*64,state="ULS")
            manifest=a/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            saved=json.loads(manifest.read_text())
            for key,value in (("source_script_sha256","b"*64),
                              ("compact_source_basis","MODEL_SHA256"),
                              ("original_case_id",long_name+"X")):
                with self.subTest(field=key):
                    manifest.write_text(json.dumps({**saved,key:value}),encoding="utf-8")
                    inspected=inspect_case_manifest(a)
                    self.assertFalse(inspected["valid"])
                    self.assertIn("COMPACT_CASE_ID_MISMATCH",inspected["issues"])
                    with self.assertRaisesRegex(ValueError,"invalid case manifest"):
                        record_case_status(a,"RUNNING")
            manifest.write_text(json.dumps(saved),encoding="utf-8")
            self.assertTrue(inspect_case_manifest(a)["valid"])

    def test_bad_source_script_hash_rejected_without_directory_write(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for bad in ("not-a-sha","g"*64,1,False):
                with self.subTest(value=bad):
                    with self.assertRaises(ValueError):
                        create_case_run(root,"MODAL","LONG_"*18,
                                        state="ULS",source_script_sha256=bad)
            self.assertEqual(list(root.iterdir()),[])

    def test_model_sha_precedence_keeps_existing_compact_names(self):
        with tempfile.TemporaryDirectory() as td:
            a=create_case_run(td,"MRSM","LONG_"*20,state="ULS",
                              model_sha256="a"*64,source_edb_sha256="b"*64,
                              source_script_sha256="c"*64)
            manifest=json.loads((a/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
            self.assertEqual(manifest["compact_source_basis"],"MODEL_SHA256")
            self.assertTrue(inspect_case_manifest(a)["valid"])
            old=dict(manifest)
            for k in ("source_script_sha256","original_case_id",
                      "compact_source_basis","case_label_mode"):
                old.pop(k,None)
            f=a/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
            f.write_text(json.dumps(old),encoding="utf-8")
            self.assertTrue(inspect_case_manifest(a)["valid"])

    def test_history_manifest_records_same_script_hash_as_source_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"Model.py"
            source.write_text("model_data = 3\n",encoding="utf-8")
            for stage in ("LTHA","NLTHA"):
                run=prepare_history_run(source,stage,"ULS","X_E0",
                                        model_length_unit="m")
                manifest=json.loads((run/"00_INPUT_SOURCE"/"CASE_MANIFEST.json").read_text())
                evidence=json.loads((run/"00_INPUT_SOURCE"/"HISTORY_INPUT_PROVENANCE.json").read_text())
                self.assertEqual(manifest["source_script_sha256"],evidence["model_script_sha256"])
                self.assertIsNone(manifest["model_sha256"])
                self.assertIsNone(manifest["source_edb_sha256"])
                self.assertTrue(inspect_case_manifest(run)["valid"])


if __name__=="__main__":
    unittest.main()
