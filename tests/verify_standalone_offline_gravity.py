"""Regression tests for the single-file offline ETABS / OpenSees comparison.

[REF docs/review/GRAVITY_ETABS_COMPARISON.md]
"""
import json
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook, load_workbook
from Offline_ETABS_OpenSees_Gravity_Standalone import compare, read_etabs


class StandaloneOfflineComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.etabs=self.base/"ETABS.xlsx"
        wb=Workbook()
        ws=wb.active
        ws.title="Joint Reactions"
        ws.append(["TABLE: Joint Reactions"])
        ws.append(["Story","Label","Unique Name","Output Case","FZ\nkN"])
        ws.append(["Base",1,560,"1. DL + LL",100.])
        ws.append(["Base",2,264,"1. DL + LL",200.])
        ws.append(["Base",3,725,"1. DL + LL",0.])
        ws.append(["Base",2,264,"2. 1.5(DL + LL)",300.])
        ws.append(["Story1",9,982,"1. DL + LL",500.])
        wb.save(self.etabs)
        self.mapping=self.base/"mapping.json"
        self.mapping.write_text(json.dumps({"node_map":[
            {"etabs_point_name":"560","opensees_node_tag":1},
            {"etabs_point_name":"264","opensees_node_tag":41},
            {"etabs_point_name":"725","opensees_node_tag":9}]}))
        def result(strategy,vals,extra=False):
            nodes=[{"tag":t,"x_m":float(t),"y_m":0,"z_m":0} for t in vals]
            reactions=[{"node_tag":t,"rz_kN":v} for t,v in vals.items()]
            return {"ok":True,"wall_support_strategy":strategy,
                "gravity_profile":"GRAVITY_1.0D_1.0L",
                "report":{"support_vertical_reaction_kN":300.,
                          "applied_vertical_load_kN":300.},
                "nodes":nodes,"reactions":reactions}
        self.src=self.base/"src.json"
        self.cont=self.base/"cont.json"
        self.src.write_text(json.dumps(result("ETABS_SOURCE_SUPPORTS",
            {1:90.,41:170.,9:40.})))
        self.cont.write_text(json.dumps(result("CONTINUOUS_WALL_BASE_FIXED",
            {1:95.,41:150.,9:35.,8751:20.})))
        self.output=self.base/"output"
    def test_original_base_only_and_exact_case(self):
        data=read_etabs(self.etabs)
        self.assertEqual(set(data),{"560","264","725"})
        self.assertEqual(data["725"]["fz"],0)
    def test_three_way_excel_and_point_264(self):
        path=compare(self.etabs,self.mapping,self.src,self.cont,self.output)
        self.assertTrue(path.exists())
        wb=load_workbook(path,read_only=True,data_only=True)
        self.assertEqual(wb["All ETABS Base joints"].max_row,4)
        self.assertEqual(wb["21 extra wall supports"].max_row,2)
        point=[row for row in wb["ETABS 264 OS 41"].values if row[0]=="264"]
        self.assertEqual(len(point),1)
        self.assertEqual(point[0][2],"41")
        self.assertEqual(point[0][9],-30.)
        self.assertEqual(point[0][10],-50.)
        self.assertEqual(point[0][11],-20.)
        critical=list(wb["Critical reaction differences"].values)
        self.assertEqual(critical[1][0],"725")
        self.assertEqual(critical[1][12],40.)
        wb.close()
        data=json.loads((self.output/"ETABS_OpenSees_Comparison_Summary.json").read_text())
        self.assertEqual(data["matched_rows"],3)
        self.assertEqual(data["additional_fixed_nodes"],1)
    def test_missing_mapping_kept_unmatched_not_zero(self):
        self.mapping.write_text(json.dumps({"node_map":[
            {"etabs_point_name":"560","opensees_node_tag":1}]}))
        path=compare(self.etabs,self.mapping,self.src,self.cont,self.output)
        wb=load_workbook(path,read_only=True,data_only=True)
        rows=list(wb["All ETABS Base joints"].values)[1:]
        p=next(row for row in rows if row[0]=="264")
        self.assertEqual(p[14],"UNMAPPED")
        self.assertIsNone(p[7])
        wb.close()
    def test_seismic_preload_refused(self):
        data=json.loads(self.src.read_text())
        data["gravity_profile"]="AS_CONFIGURED"
        self.src.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"Wrong load profile"):
            compare(self.etabs,self.mapping,self.src,self.cont,self.output)


if __name__=="__main__":
    unittest.main()
