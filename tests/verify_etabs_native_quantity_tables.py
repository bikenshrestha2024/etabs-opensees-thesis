"""Pure fake-CSI tests for native quantity table extraction and fail closed."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from components.validation.etabs_native_quantity_tables import (
    export_native_quantity_tables)


class FakeDatabase:
    def GetAvailableTables(self):
        return (2, ["Material List by Object Type", "Unrelated"],
                ["Material List by Object Type", "Other"], [0, 0], 0)

    def GetTableForDisplayArray(self, key, field_keys, group, version,
                                fields, count, data):
        if key != "Material List by Object Type":
            raise RuntimeError("Unexpected table requested")
        # Exact six-element OUT tuple captured from user's ETABS v23 OAPI:
        # FieldKeyList, TableVersion, FieldsKeysIncluded,
        # NumberRecords, TableData, retcode.
        return ((), 1, ("Object", "Weight"), 2,
                ("B1", "50.0", "S1", "30.0"), 0)


class FakeSap:
    DatabaseTables=FakeDatabase()


class EtabsNativeQuantityTests(unittest.TestCase):
    def test_capture_actual_fields_and_data(self):
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(FakeSap(),root)
            self.assertEqual(result["available_table_count"],2)
            self.assertEqual(result["selected_table_count"],1)
            row=result["table_exports"][0]
            self.assertEqual(row["status"],"EXPORTED_RAW_NOT_NORMALIZED")
            path=Path(root)/row["file"]
            with path.open(encoding="utf-8-sig",newline="") as stream:
                records=list(csv.reader(stream))
            self.assertEqual(records,
                             [["Object","Weight"],["B1","50.0"],["S1","30.0"]])
            self.assertTrue((Path(root)/"ETABS_NATIVE_QUANTITY_MANIFEST.json").is_file())

    def test_gravity_selection_and_all_evidence_families(self):
        class Native(FakeDatabase):
            cases=["EQX"]
            combos=["Old"]
            def GetLoadCasesSelectedForDisplay(self):
                return (len(self.cases),self.cases,0)
            def GetLoadCombinationsSelectedForDisplay(self):
                return (len(self.combos),self.combos,0)
            def SetLoadCasesSelectedForDisplay(self,values):
                self.cases=list(values);return 0
            def SetLoadCombinationsSelectedForDisplay(self,values):
                self.combos=list(values);return 0
            def GetAvailableTables(self):
                names=["Element Connectivity - Shells","Joint Assignments - Constraints",
                       "Section Cut Forces","Element Joint Forces - Frames",
                       "Joint Reactions","Other"]
                return (len(names),names,names,[0]*len(names),0)
            def GetTableForDisplayArray(self,key,*args):
                if self.cases or self.combos!=["1. DL + LL"]:
                    raise AssertionError("wrong display selection")
                if key=="Section Cut Forces":
                    return ((),1,("OutputCase",),0,(),0)
                return ((),1,("OutputCase",),1,("1. DL + LL",),0)
        sap=FakeSap();sap.DatabaseTables=Native()
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(sap,root,gravity_combo="1. DL + LL")
            self.assertEqual(result["selected_table_count"],5)
            self.assertEqual(result["display_selection_status"],"GRAVITY_COMBO_READBACK_VERIFIED")
            self.assertEqual(result["engineering_evidence_coverage"]["analytical_mesh"]["status"],
                             "RAW_NONEMPTY_CANDIDATES_REQUIRE_REVIEW")
            self.assertEqual(result["engineering_evidence_coverage"]["beam_end_offsets"]["status"],
                             "NO_CATALOG_CANDIDATES")
            cut=next(row for row in result["table_exports"] if row["table_key"]=="Section Cut Forces")
            self.assertEqual(cut["records"],0)
            self.assertNotIn("Section Cut Forces",result["engineering_evidence_coverage"]["foundation_section_cuts"]["nonempty_tables"])
            self.assertEqual(sap.DatabaseTables.cases,["EQX"])
            self.assertEqual(sap.DatabaseTables.combos,["Old"])

    def test_gravity_selection_unavailable_does_not_claim_scope(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(AttributeError):
                export_native_quantity_tables(FakeSap(),root,gravity_combo="1. DL + LL")
            self.assertFalse((Path(root)/"ETABS_NATIVE_QUANTITY_MANIFEST.json").exists())

    def test_rejects_nonzero_native_return(self):
        class Failed(FakeDatabase):
            def GetTableForDisplayArray(self,*args):
                return ((),1,("Object","Weight"),1,("B1","50"),1)
        sap=FakeSap();sap.DatabaseTables=Failed()
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(sap,root)
            self.assertEqual(result["table_exports"][0]["status"],
                             "UNAVAILABLE_OR_API_ERROR")
            self.assertIn("retcode=1",result["table_exports"][0]["error"])

    def test_malformed_native_data_is_reported_not_fabricated(self):
        class Broken(FakeDatabase):
            def GetTableForDisplayArray(self,*args):
                return ((),1,("Object","Weight"),2,("B1","50"),0)
        instance=FakeSap()
        instance.DatabaseTables=Broken()
        with tempfile.TemporaryDirectory() as root:
            result=export_native_quantity_tables(instance,root)
            self.assertEqual(result["table_exports"][0]["status"],
                             "UNAVAILABLE_OR_API_ERROR")
            self.assertEqual(result["table_exports"][0].get("records"),None)


if __name__=="__main__":
    unittest.main()
