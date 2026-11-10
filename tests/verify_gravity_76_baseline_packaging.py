"""Synthetic regression: true 76-source-support audit is never replaced by 32-node reactions.

[REF components/gravity/comparison_bundle.py export_bundle]
This test checks evidence selection and manifest integrity, NOT native engineering validation.
"""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from components.gravity.comparison_bundle import export_bundle


class Original76SupportEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/"source";self.source.mkdir()
        self.root_out=self.root/"results";self.root_out.mkdir()
        self.diag=self.root_out/"Gravity_Reaction_Diagnostic"/"one"
        self.diag.mkdir(parents=True)
        self.dual=self.root_out/"Gravity_Wall_Base_Comparison"/"one"
        self.case76=self.dual/"ETABS_SOURCE_SUPPORTS"
        self.case76.mkdir(parents=True)
        self.case97=self.dual/"CONTINUOUS_WALL_BASE_FIXED"
        self.case97.mkdir()
        self.script=str(self.source/"OpenSees_Complete_Gravity_Model.py")
        Path(self.script).write_text("pass",encoding="utf8")
        nodes=[dict(tag=i,x_m=float(i),y_m=0.,z_m=0.,
                    ux_m=0.,uy_m=0.,uz_m=0.,
                    rx_rad=0.,ry_rad=0.,rz_rad=0.)
               for i in range(1,77)]
        topology={"node_map":[dict(opensees_node_tag=i,
                    etabs_point_name=str(1000+i),
                    coordinates_m=[float(i),0.,0.])
                    for i in range(1,77)]}
        (self.source/"OpenSees_Element_Connectivity.json").write_text(
            json.dumps(topology),encoding="utf8")
        (self.source/"OpenSees_Complete_Model_Data_V118.json").write_text(
            json.dumps({"nodes":{},"unfactored_patterns":{}}),encoding="utf8")
        base={"ok":True,"nodes":nodes,"local_forces":[{"tag":12,"N_i_kN":0.}],
              "model_script":self.script,"gravity_profile":"GRAVITY_1.0D_1.0L",
              "report":{"applied_vertical_load_kN":76.}}
        orig=dict(base,wall_support_strategy="ETABS_SOURCE_SUPPORTS",
            reactions=[dict(node_tag=i,rx_kN=0.,ry_kN=0.,rz_kN=1.)
                       for i in range(1,77)])
        diag=dict(base,wall_support_strategy="ETABS_NONZERO_REACTION_DIAGNOSTIC",
            reactions=[dict(node_tag=i,rx_kN=0.,ry_kN=0.,rz_kN=76./32.)
                       for i in range(1,33)])
        cont=dict(orig,wall_support_strategy="CONTINUOUS_WALL_BASE_FIXED")
        for folder,obj in ((self.diag,diag),(self.case76,orig),
                           (self.case97,cont)):
            (folder/"Gravity_Result_V110.json").write_text(
                json.dumps(obj),encoding="utf8")
        for name in ("Gravity_Wall_Base_Strategy_Comparison.json",
                     "Gravity_Wall_Base_Strategy_Comparison.xlsx",
                     "Gravity_Wall_Base_Nodal_Reaction_Differences.csv"):
            (self.dual/name).write_text("{}",encoding="utf8")
        source_etabs={"joint_reactions":[dict(point=str(1000+i),
                      rz_global_kN=1.,x_m=float(i),y_m=0.,z_m=0.,
                      global_z_basis="GLOBAL_Z_VERIFIED_DEFAULT_AXES")
                      for i in range(1,77)]}
        self.etabs=self.root/"source_etabs.json"
        self.etabs.write_text(json.dumps(source_etabs),encoding="utf8")

    def test_real_76_support_baseline_completes_node_inventory(self):
        manifest,archive=export_bundle(
            self.source,self.diag,self.root/"upload",
            dual_run_dir=self.dual,comparison_root=self.root_out,
            etabs_json=self.etabs)
        self.assertFalse(any("node_audit_76/ETABS_REACTION_MATCHES"==
                             item["file"] for item in manifest["missing"]))
        self.assertEqual(manifest["missing_required_count"],0)
        with zipfile.ZipFile(archive) as zipf:
            name=next(n for n in zipf.namelist()
                      if n.endswith("node_audit_76/Gravity_76_Source_Support_Reactions.json"))
            record=json.loads(zipf.read(name))
            self.assertEqual(record["matched_count"],76)
            self.assertEqual(record["missing_or_unverified"],0)
            self.assertTrue(all(x["opensees_Rz_kN"]==1.
                                for x in record["rows"]))
            self.assertTrue(any(n.endswith("node_audit_76/BASELINE_PROVENANCE.json")
                                for n in zipf.namelist()))
            self.assertTrue(any(n.endswith("wall_base_complete/ETABS_SOURCE_SUPPORTS/Gravity_Result_V110.json")
                                for n in zipf.namelist()))

    def test_different_gravity_model_is_never_used_as_76_baseline(self):
        bad=json.loads((self.case76/"Gravity_Result_V110.json").read_text())
        bad["model_script"]="C:/unrelated/other_model.py"
        (self.case76/"Gravity_Result_V110.json").write_text(json.dumps(bad))
        manifest,_=export_bundle(
            self.source,self.diag,self.root/"invalid",
            dual_run_dir=self.dual,comparison_root=self.root_out,
            etabs_json=self.etabs)
        self.assertTrue(any(item["file"]==
            "node_audit_76/Gravity_76_Source_Support_Reactions.csv"
            and item["required"] for item in manifest["missing"]))


if __name__=="__main__":
    unittest.main()
