"""Synthetic tests of six-DOF common-origin reaction accounting.

Do not confuse these with a source EDB comparison or native solver evidence.
"""
import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from components.validation.reaction_common_cut import (
    compare_common_cut, compare_ablation, export_report
)


def fixture():
    source = {
        "edb_sha256": "a"*64, "model_sha256": "b"*64,
        "case": "1. DL + LL", "force_unit": "kN", "length_unit": "m",
        "coordinate_system": "GLOBAL", "reaction_level": "OBJECT_JOINT",
        "native_restraints_verified": False
    }
    e, o, mapping = [], [], []
    for i in range(76):
        group = "PRIMARY_32" if i < 32 else "WALL_TRANSFER_44"
        x = float(i%8)
        xyz = [x, float(i//8), 0.]
        reaction = [1.,2.,100.,3.,4.,5.]
        e.append({"id":f"E{i}", "xyz_m":xyz[:],"reaction":reaction[:]})
        o.append({"id":f"O{i}", "xyz_m":xyz[:],"reaction":reaction[:]})
        mapping.append({"etabs":f"E{i}","opensees":f"O{i}","group":group})
    return {"source":source,"origin_m":[0.,0.,0.],
            "etabs":e,"opensees":o,"map":mapping}


class CommonCutTests(unittest.TestCase):
    def test_equal_vectors_are_diagnostic_not_approved(self):
        result=compare_common_cut(fixture())
        self.assertEqual(result["groups"]["PRIMARY_32"]["count"],32)
        self.assertEqual(result["groups"]["WALL_TRANSFER_44"]["count"],44)
        self.assertEqual(result["groups"]["ALL_MAPPED"]["count"],76)
        self.assertEqual(result["groups"]["ALL_MAPPED"]["difference"],[0.]*6)
        self.assertIn("NOT_STRUCTURAL_ACCEPTANCE",result["status"])
        self.assertTrue(any("OBJECT_JOINT" in x for x in result["unresolved"]))

    def test_transferred_vertical_force_produces_origin_moment(self):
        d=fixture()
        # At (x,y,0), +10 kN FZ creates (+10*y,-10*x) kN*m
        d["opensees"][2]["reaction"][2]+=10
        r=compare_common_cut(d)
        x,y,_=d["opensees"][2]["xyz_m"]
        self.assertAlmostEqual(r["groups"]["PRIMARY_32"]["difference"][2],10)
        self.assertAlmostEqual(r["groups"]["PRIMARY_32"]["difference"][3],10*y)
        self.assertAlmostEqual(r["groups"]["PRIMARY_32"]["difference"][4],-10*x)
        self.assertAlmostEqual(r["groups"]["PRIMARY_32"]["sum_abs_local_delta"][2],10)

    def test_new_origin_preserves_force_and_adjusts_both_reference_moments(self):
        d=fixture()
        d["opensees"][0]["reaction"][2]+=10
        origin0=compare_common_cut(d)["groups"]["ALL_MAPPED"]["difference"]
        d["origin_m"]=[1,2,0]
        origin1=compare_common_cut(d)["groups"]["ALL_MAPPED"]["difference"]
        self.assertAlmostEqual(origin1[2],origin0[2])
        self.assertAlmostEqual(origin1[3]-origin0[3],-20)
        self.assertAlmostEqual(origin1[4]-origin0[4],+10)

    def test_reject_missing_native_node_instead_of_zero(self):
        d=fixture()
        d["opensees"].pop()
        with self.assertRaisesRegex(ValueError,"cannot become zero"):
            compare_common_cut(d)

    def test_reject_duplicate_map_and_wrong_location(self):
        d=fixture()
        d["map"][1]["opensees"]=d["map"][0]["opensees"]
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            compare_common_cut(d)
        d=fixture()
        d["opensees"][0]["xyz_m"][0]+=0.5
        with self.assertRaisesRegex(ValueError,"coordinates differ"):
            compare_common_cut(d)

    def test_reject_fake_hash_boolean_unsafe_units(self):
        for key,val in (("edb_sha256","abc"),("force_unit","N"),
                        ("coordinate_system","LOCAL"),
                        ("native_restraints_verified",None)):
            d=fixture()
            d["source"][key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):
                compare_common_cut(d)

    def test_six_dof_sign_and_file_provenance(self):
        d=fixture()
        d["opensees"][0]["reaction"][5]-=2.5
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"input.json"
            source.write_text(json.dumps(d),encoding="utf-8")
            result=export_report(source,Path(tmp)/"out")
            self.assertAlmostEqual(
                result["groups"]["PRIMARY_32"]["difference"][5],-2.5)
            self.assertTrue((Path(tmp)/"out"/"Reaction_Six_DOF_Common_Cut.csv").is_file())
            self.assertEqual(len(result["input_sha256"]),64)



    def test_four_case_ablation_reports_worsening_without_picking_winner(self):
        scenarios={}
        for name,hash_char,error in (
            ("baseline","b",10),
            ("wall_mesh_only","c",15),
            ("end_zones_only","d",18),
            ("combined","e",25)):
            d=fixture()
            d["source"]["model_sha256"]=hash_char*64
            d["opensees"][0]["reaction"][2]+=error
            scenarios[name]=d
        r=compare_ablation(scenarios)
        self.assertEqual(r["scenarios"]["baseline"]["l1_primary_FZ_kN"],10)
        self.assertEqual(r["scenarios"]["combined"]["l1_primary_FZ_kN"],25)
        self.assertTrue(r["scenarios"]["wall_mesh_only"]["worsens_primary_l1"])
        self.assertTrue(r["scenarios"]["end_zones_only"]["worsens_primary_l1"])
        self.assertIn("PHYSICAL_CAUSE_UNVERIFIED",r["status"])

    def test_four_case_requires_distinct_model_and_identical_reference(self):
        scenarios={}
        for name,index in zip(
            ("baseline","wall_mesh_only","end_zones_only","combined"),"bcde"):
            d=fixture()
            d["source"]["model_sha256"]=index*64
            scenarios[name]=d
        invalid=copy.deepcopy(scenarios)
        invalid["combined"]["source"]["model_sha256"]="b"*64
        with self.assertRaisesRegex(ValueError,"reuse assembled-model"):
            compare_ablation(invalid)
        invalid=copy.deepcopy(scenarios)
        invalid["combined"]["etabs"][0]["reaction"][2]+=1
        with self.assertRaisesRegex(ValueError,"identical ETABS reference"):
            compare_ablation(invalid)
        invalid=copy.deepcopy(scenarios)
        invalid.pop("wall_mesh_only")
        with self.assertRaisesRegex(ValueError,"four explicit"):
            compare_ablation(invalid)


if __name__=="__main__":
    unittest.main()
