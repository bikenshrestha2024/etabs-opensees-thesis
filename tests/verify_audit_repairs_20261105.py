"""Regression tests for high-impact audit fixes; synthetic only."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.validation.etabs_comparison import collect, FIELDS
from components.validation.etabs_equivalence_report import evaluate
from components.validation.floor_end_extraction import map_floor_ends


def geom(node,story,z,x,y):
    return dict(node_id=node,storey=story,z_m=z,x_m=x,y_m=y,is_perimeter="true")


def response(node,story,step="FINAL"):
    return dict(node_id=node,storey=story,limit_state="ULS",case="X_E0",
        axis="X",step=step,ux_m=".01" if node.endswith("A") else ".02",
        uy_m="0",centered_cm_load="true",
        response_basis="signed_centered_linear_increment")


class FixedAuditFindings(unittest.TestCase):
    def test_wrong_basis_is_not_also_missing_opensees(self):
        base=dict(method="MRSM",limit_state="ULS",case="X_E0",axis="X",
            location="25",metric="drift_ratio",unit="ratio")
        ours=[dict(base,basis="CQC_design_unscaled_by_7_5",value=.001)]
        refs=[dict(base,basis="ETABS_displacement_unverified",value=.001)]
        result=evaluate(ours,refs,FIELDS,{"assumptions_verified":True})
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]["status"],"NOT_COMPARABLE")

    def test_string_approval_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"boolean"):
            evaluate([],[],FIELDS,{"assumptions_verified":"false"})

    def test_reject_cross_floor_mixed_step(self):
        nodes=[geom("1A","1",3.,0.,0.),geom("1B","1",3.,0.,20.),
               geom("2A","2",7.,0.,0.),geom("2B","2",7.,0.,20.)]
        rows=[response("1A","1"),response("1B","1"),
              response("2A","2","LATER"),response("2B","2","LATER")]
        with self.assertRaisesRegex(ValueError,"response step across floors"):
            map_floor_ends(nodes,rows,limit_state="ULS",source="OPENSEES")

    def test_reject_inconsistent_floor_elevation(self):
        nodes=[geom("1A","1",3.,0.,0.),geom("1B","1",3.2,0.,20.)]
        with self.assertRaisesRegex(ValueError,"elevation mismatch"):
            map_floor_ends(nodes,[response("1A","1"),response("1B","1")],
                           limit_state="ULS",source="ETABS")

    def test_current_hash_only_and_no_opposite_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb":"D:/Structures/ULTIMATE LOAD - NEPAL.EDB"}))
            model=root/"OpenSees_Complete_Model_Data_V118.json"
            model.write_text('{"dummy":true}',encoding="utf8")
            signature=hashlib.sha256(model.read_bytes()).hexdigest()
            resultroot=root/"OpenSees_Analysis_Results"
            results=resultroot/"MRSM_ULS";results.mkdir(parents=True)
            usable={"X_E0":{"limit_state":"ULS","axis":"X",
                    "model_sha256":signature,"scaled_modal_base_shear_kN":100.,
                    "stories":[dict(story_number=1,scaled_story_shear_kN=100.,
                                    design_displacement_m=.01,design_drift_ratio=.003)]}}
            stale={"Y_E0":{**usable["X_E0"],"axis":"Y",
                    "model_sha256":"bad"}}
            wrong={"X_E0":{**usable["X_E0"],"limit_state":"SLS"}}
            (results/"MRSM_Results_V132.json").write_text(json.dumps(usable))
            for name,doc in (("old",stale),("cross_state",wrong)):
                path=resultroot/name;path.mkdir()
                (path/"MRSM_Results_V132.json").write_text(json.dumps(doc))
            issues=[]
            rows=collect(root,issues)
            self.assertEqual({r["case"] for r in rows},{"X_E0"})
            self.assertTrue(any("mismatched" in x for x in issues))
            self.assertTrue(any("opposite-state" in x for x in issues))

    def test_old_unfingerprinted_results_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"OpenSees_Element_Connectivity.json").write_text(
                json.dumps({"source_edb":"D:/Structures/SERVICE MODEL.EDB"}))
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text("{}")
            resultdir=root/"OpenSees_Analysis_Results"/"old";resultdir.mkdir(parents=True)
            (resultdir/"MRSM_Results_V132.json").write_text(json.dumps(
                {"X_E0":{"axis":"X","limit_state":"SLS","stories":[],
                         "scaled_modal_base_shear_kN":123.}}))
            audit=[]
            self.assertEqual(collect(root,audit),[])
            self.assertTrue(any("mismatched" in x for x in audit))


if __name__=="__main__":
    unittest.main(verbosity=2)
