"""Offline ETABS exported-table joint reaction validation tests."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from openpyxl import Workbook
from components.validation.gravity_etabs_offline import (
    read_etabs_joint_reactions,compare_etabs_export,export_offline_comparison
)

class OfflineEtabsGravityTests(unittest.TestCase):
    def setUp(self):
        self.ctx=tempfile.TemporaryDirectory()
        self.addCleanup(self.ctx.cleanup)
        self.root=Path(self.ctx.name)
        self.xlsx=self.root/"etabs.xlsx"
        self.csv=self.root/"joint.csv"
        rows=[
          ["TABLE: Joint Reactions"],
          ["Story","Label","Unique Name","Output Case","Case Type","Step Type","Step Number",
           "FX","FY","FZ","MX","MY","MZ"],
          ["","","","","","","","kN","kN","kN","kN-m","kN-m","kN-m"],
          ["Base",1,560,"1. DL + LL","Combination",None,None,0,0,100,0,0,0],
          ["Base",2,1,"1. DL + LL","Combination",None,None,0,0,200,0,0,0],
          ["Base",1,560,"MODAL","LinModRitz","Mode",1,0,0,-5,0,0,0],
          ["Story1",3,22,"1. DL + LL","Combination",None,None,0,0,17,0,0,0]]
        wb=Workbook();ws=wb.active;ws.title="Joint Reactions"
        for row in rows:ws.append(row)
        wb.save(self.xlsx)
        with self.csv.open("w",newline="",encoding="utf8") as f:csv.writer(f).writerows(rows)
        (self.root/"mapping.json").write_text(json.dumps(dict(node_map=[
            dict(etabs_point_name="560",opensees_node_tag=10),
            dict(etabs_point_name="1",opensees_node_tag=11)])))
        def gravity(mode,rs):
            return dict(ok=True,wall_support_strategy=mode,
                gravity_profile="GRAVITY_1.0D_1.0L",
                report=dict(support_vertical_reaction_kN=300.,
                            applied_vertical_load_kN=300.),
                nodes=[dict(tag=10,x_m=0,y_m=0,z_m=0),
                       dict(tag=11,x_m=6,y_m=0,z_m=0)],
                reactions=[dict(node_tag=10,rz_kN=rs[0]),
                           dict(node_tag=11,rz_kN=rs[1])])
        self.a=self.root/"source.json";self.b=self.root/"continuous.json"
        self.a.write_text(json.dumps(gravity("ETABS_SOURCE_SUPPORTS",[130,170])))
        self.b.write_text(json.dumps(gravity("CONTINUOUS_WALL_BASE_FIXED",[120,180])))
    def test_exact_case_base_filter_and_unique_map_from_xlsx(self):
        audit=compare_etabs_export(self.xlsx,self.root/"mapping.json",self.a,self.b)
        self.assertEqual(audit["etabs_joint_records"],2)
        self.assertEqual(audit["matched_source_nodes"],2)
        self.assertEqual(audit["sum_etabs_base_joint_FZ_kN"],300.)
        self.assertEqual(audit["difference_opensees_minus_etabs_kN"],0.)
        self.assertEqual(audit["rows"][0]["etabs_unique_name"],"560")
        self.assertEqual(audit["rows"][0]["delta_source_minus_etabs_kN"],30.)
        out=export_offline_comparison(audit,self.root/"output")
        self.assertTrue((out/"ETABS_Offline_Gravity_Comparison.xlsx").exists())
    def test_csv_fallback_handles_large_etabs_export(self):
        data=read_etabs_joint_reactions(self.csv)
        self.assertEqual(len(data),2)
        self.assertEqual(data["560"]["etabs_FZ_kN"],100.)
    def test_missing_mapping_is_not_a_silent_zero(self):
        (self.root/"mapping.json").write_text(json.dumps(dict(node_map=[])))
        audit=compare_etabs_export(self.csv,self.root/"mapping.json",self.a)
        self.assertEqual(audit["matched_source_nodes"],0)
        self.assertEqual(audit["unmapped_or_missing_reactions"],2)
        self.assertIsNone(audit["rows"][0]["delta_source_minus_etabs_kN"])
    def test_does_not_mix_seismic_preload(self):
        data=json.loads(self.a.read_text());data["gravity_profile"]="AS_CONFIGURED"
        self.a.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"not full"):
            compare_etabs_export(self.csv,self.root/"mapping.json",self.a)

if __name__=="__main__":
    unittest.main()
