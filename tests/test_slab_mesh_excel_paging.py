"""Synthetic >Excel-row-limit slab path test (limit reduced in test).

No ETABS/OpenSees solver, source EDB or private workbook required.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class MeshExcelPagingTests(unittest.TestCase):
    def test_node_load_paths_are_paged_without_losing_rows(self):
        from openpyxl import Workbook
        from components.gravity.load_path_formulas import add_formula_audit

        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            cells=[]
            for i in range(7):
                cells.append({
                    "category":"FLOOR","object":str(i+1),"area":4.,
                    "nodes":[1,2,3,4],
                    "properties":{"thickness":0.15,"weight":25.}})
            data={"frames":[],"shells":cells,
                  "nodes":{str(i):[float(i),0.,3.] for i in (1,2,3,4)}}
            cfg={"floor_subdivisions":4,
                 "gravity_factors":{"Self Weight":1.0},
                 "mass_factors":{"Self Weight":1.0}}
            (folder/"OpenSees_Load_Conversion_Audit.json").write_text(
                json.dumps({"etabs_load_pattern_self_weight_multipliers":[
                    {"pattern":"Self Weight","multiplier":1.0}]}))
            wb=Workbook()
            # Seven source cells produce 7 surface records and 28 node rows.
            # Force a test-only smaller limit (9 rows including header).
            with patch("openpyxl.xml.constants.MAX_ROW",9):
                add_formula_audit(wb,folder,data=data,cfg=cfg)
            pages=[s for s in wb.worksheets if
                   s.title=="Loaded node path" or s.title.startswith("Loaded node path ")]
            self.assertEqual(len(pages),4)
            self.assertEqual([x.max_row for x in pages],[9,9,9,5])
            self.assertEqual(sum(x.max_row-1 for x in pages),28)
            recorded=[row for sh in pages for row in sh.iter_rows(
                min_row=2,values_only=True)]
            self.assertEqual(len(recorded),28)
            self.assertEqual(
                [x.value for x in wb["Loaded node path index"]["B"][1:]],
                [8,8,8,4])
            for entry in recorded:
                self.assertTrue(str(entry[7]).startswith(
                    "='Surface load formulas'!L"))
            target=folder/"roundtrip.xlsx"
            wb.save(target)
            from openpyxl import load_workbook
            reopened=load_workbook(target,read_only=True)
            self.assertEqual(
                sum(reopened[x.title].max_row-1 for x in pages),28)
            reopened.close()


if __name__=="__main__":
    unittest.main()
