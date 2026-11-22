"""ETABS table registration: one canonical current-source registry, no file copies."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from openpyxl import Workbook

from components.inputs.etabs_table_bundle import register_current_etabs_tables
from components.inputs.project_workbooks import registered_project_source


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

    def test_missing_native_source_blocks_creation(self):
        with patch("components.inputs.project_workbooks._source_edb_path",
                   return_value=None):
            with self.assertRaisesRegex(FileNotFoundError,"source EDB"):
                register_current_etabs_tables(self.root,self.books[0],self.books[1:])
        self.assertFalse((self.root/"01_ETABS_EXPORT").exists())


if __name__=="__main__":
    unittest.main()
