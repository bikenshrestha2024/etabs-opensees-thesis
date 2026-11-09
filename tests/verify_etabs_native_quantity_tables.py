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
