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
    def test_continuous_only_support_is_not_falsely_mapped_to_etabs(self):
        data=json.loads(self.b.read_text())
        data["nodes"].append(dict(tag=8751,x_m=3,y_m=0,z_m=0))
        data["reactions"].append(dict(node_tag=8751,rz_kN=15.))
        self.b.write_text(json.dumps(data))
        report=compare_etabs_export(self.xlsx,self.root/"mapping.json",self.a,self.b)
        self.assertEqual(len(report["continuous_only_nodes"]),1)
        self.assertEqual(report["continuous_only_nodes"][0]["opensees_node_tag"],"8751")
        out=export_offline_comparison(report,self.root/"output_21")
        from openpyxl import load_workbook
        wb=load_workbook(out/"ETABS_Offline_Gravity_Comparison.xlsx",read_only=True)
        try:
            self.assertIn("Critical source nodes",wb.sheetnames)
            self.assertIn("Additional fixed wall nodes",wb.sheetnames)
            self.assertIn("Evidence gates",wb.sheetnames)
            self.assertEqual(wb["Additional fixed wall nodes"].max_row,2)
        finally:wb.close()
    def test_current_primary_32_diagnostic_is_compared_without_faking_zero_nodes(self):
        data=json.loads(self.a.read_text())
        data["wall_support_strategy"]="ETABS_NONZERO_REACTION_DIAGNOSTIC"
        # Only one of two ETABS-mapped points is an actual restrained
        # reaction in this synthetic 32-style case.
        data["reactions"]=data["reactions"][:1]
        data["report"]["support_vertical_reaction_kN"]=130.0
        data["report"]["applied_vertical_load_kN"]=130.0
        primary=self.root/"primary.json"
        primary.write_text(json.dumps(data))
        report=compare_etabs_export(
            self.xlsx,self.root/"mapping.json",primary,self.b,
            source_strategy="ETABS_NONZERO_REACTION_DIAGNOSTIC")
        self.assertEqual(report["source_strategy"],"ETABS_NONZERO_REACTION_DIAGNOSTIC")
        self.assertEqual(report["matched_source_nodes"],1)
        self.assertEqual(report["unmapped_or_missing_reactions"],1)
        missing=[r for r in report["rows"] if r["etabs_unique_name"]=="1"][0]
        self.assertIsNone(missing["opensees_source_Rz_kN"])
        self.assertEqual(missing["status"],"NO_OPENSEES_REACTION_AT_MAPPED_NODE")

    def test_registry_driven_current_32_76_97_offline_workbooks(self):
        import hashlib
        from components.validation.gravity_etabs_latest import run
        model=self.root/"OpenSees_Complete_Gravity_Model.py"
        model.write_text("# immutable synthetic source for provenance test\\n",encoding="utf-8")
        modelhash=hashlib.sha256(model.read_bytes()).hexdigest()
        # The source model's mapping is the existing fixture.
        reg={}
        for mode,count in (("ETABS_NONZERO_REACTION_DIAGNOSTIC",32),
                           ("ETABS_SOURCE_SUPPORTS",76),
                           ("CONTINUOUS_WALL_BASE_FIXED",97)):
            result=self.root/(mode+".json")
            nodes=[dict(tag=i,x_m=float(i),y_m=0.,z_m=0.) for i in range(1,count+1)]
            reactions=[dict(node_tag=i,rz_kN=(100. if i==10 else
                             200. if i==11 else 0.)) for i in range(1,count+1)]
            result.write_text(json.dumps(dict(
                ok=True,gravity_profile="GRAVITY_1.0D_1.0L",
                wall_support_strategy=mode,nodes=nodes,reactions=reactions,
                report=dict(applied_vertical_load_kN=300.,
                            support_vertical_reaction_kN=300.))))
            reg[mode+"|GRAVITY_1.0D_1.0L"]=dict(
                scenario=mode,profile="GRAVITY_1.0D_1.0L",
                status="SOLVED_REACTIONS_NOT_ETABS_VALIDATED",
                support_tags=list(range(1,count+1)),
                model_path=str(model),model_sha256=modelhash,
                input_sha256={"OpenSees_Complete_Gravity_Model.py":modelhash},
                result_path=str(result))
        registry=self.root/"Gravity_Case_Reaction_Index.json"
        registry.write_text(json.dumps(reg))
        # Set mapping node tags 10/11 exactly as used by both source cases.
        out=run(self.xlsx,self.root/"mapping.json",registry,self.root/"offline_current")
        self.assertTrue((out/"PRIMARY_32"/"ETABS_Offline_Gravity_Comparison.xlsx").is_file())
        self.assertTrue((out/"ETABS_NODE_POSITION_76"/"ETABS_Offline_Gravity_Comparison.xlsx").is_file())
        manifest=json.loads((out/"OFFLINE_GRAVITY_32_76_97_INDEX.json").read_text())
        self.assertEqual(manifest["results"]["PRIMARY_32"]["difference_kN"],0.)
        self.assertEqual(manifest["results"]["ETABS_NODE_POSITION_76"]["difference_kN"],0.)
        reg["ETABS_SOURCE_SUPPORTS|GRAVITY_1.0D_1.0L"]["model_sha256"]="stale"
        registry.write_text(json.dumps(reg))
        with self.assertRaisesRegex(ValueError,"model SHA256"):
            run(self.xlsx,self.root/"mapping.json",registry,self.root/"stale")

    def test_etabs_header_with_embedded_newline_units(self):
        wb=Workbook();ws=wb.active;ws.title="Joint Reactions"
        ws.append(["Story","Label","Unique Name","Output Case","FZ\nkN"])
        ws.append(["Base",1,560,"1. DL + LL",100])
        alt=self.root/"inline_unit_header.xlsx";wb.save(alt)
        report=read_etabs_joint_reactions(alt)
        self.assertEqual(report["560"]["etabs_FZ_kN"],100.)

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
