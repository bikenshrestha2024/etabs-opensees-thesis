"""Tests for physically paired floor ends and source-state isolation."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from components.validation.floor_end_extraction import map_floor_ends,write_outputs

def node(tag,x,y,storey="25",boundary=True):
    return dict(node_id=str(tag),storey=storey,x_m=x,y_m=y,z_m=95,
                is_perimeter="true" if boundary else "false")

def record(tag,ux,uy=0,*,axis="X",state="ULS",case="X_CENTERED",step="FINAL",
           centered="true",basis="signed_centered_linear_increment"):
    return dict(node_id=str(tag),storey="25",limit_state=state,case=case,
                axis=axis,step=step,ux_m=ux,uy_m=uy,
                centered_cm_load=centered,response_basis=basis)

class FloorEndTests(unittest.TestCase):
    def geometry(self):
        # Irregular L-shaped floor: Y=20 end only at X=0, not at X=10.
        return [node("A",0,0),node("B",0,20),node("C",10,0),
                node("D",10,10),node("O",5,10,boundary=False)]

    def test_perimeter_pair_with_matching_longitudinal_coordinate(self):
        rows=[record("A",.01),record("B",.030),record("C",.003),
              record("D",.002),record("O",.1)]
        pairs,governing=map_floor_ends(self.geometry(),rows,
            limit_state="ULS",source="ETABS")
        self.assertEqual(len(pairs),1)
        self.assertEqual({pairs[0]["node_a"],pairs[0]["node_b"]},{"A","B"})
        self.assertAlmostEqual(governing[0]["ratio"],3.0)
        self.assertEqual(governing[0]["status"],"EXTREME TORSION")

    def test_directional_not_resultant(self):
        rows=[record("A",.01,100.),record("B",.02,0.)]
        pairs,_=map_floor_ends(self.geometry(),rows,limit_state="ULS",source="OPENSEES")
        self.assertAlmostEqual(pairs[0]["ratio"],2.)

    def test_y_uses_x_ends_not_x_translation(self):
        rows=[record("A",100.,.01,axis="Y",case="Y_CENTERED"),
              record("C",1.,.025,axis="Y",case="Y_CENTERED")]
        pairs,governing=map_floor_ends(self.geometry(),rows,limit_state="ULS",source="ETABS")
        self.assertEqual(len(pairs),1)
        self.assertAlmostEqual(governing[0]["ratio"],2.5)
        self.assertEqual(governing[0]["status"],"TORSIONAL IRREGULARITY")

    def test_no_longitudinal_alignment_reports_pending(self):
        g=[node("A",0,0),node("B",5,20),node("C",10,0)]
        rows=[record("A",.01),record("B",.03)]
        pairs,governing=map_floor_ends(g,rows,limit_state="ULS",source="ETABS")
        self.assertEqual(pairs,[])
        self.assertEqual(governing[0]["status"],"NOT EVALUATED")

    def test_rejects_mixed_steps_before_peak_picking(self):
        rows=[record("A",.01,step="0.1"),record("B",.03,step="0.2")]
        with self.assertRaisesRegex(ValueError,"More than one response step"):
            map_floor_ends(self.geometry(),rows,limit_state="ULS",source="OPENSEES")

    def test_rejects_uls_sls_and_off_center(self):
        with self.assertRaisesRegex(ValueError,"Cross-state"):
            map_floor_ends(self.geometry(),[record("A",.01,state="SLS")],
                           limit_state="ULS",source="ETABS")
        with self.assertRaisesRegex(ValueError,"centered-CM"):
            map_floor_ends(self.geometry(),[record("A",.01,centered="false")],
                           limit_state="ULS",source="ETABS")
        with self.assertRaisesRegex(ValueError,"response basis"):
            map_floor_ends(self.geometry(),[record("A",.01,basis="CQC_envelope")],
                           limit_state="ULS",source="ETABS")

    def test_output_and_source_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            geometry=root/"g.csv";response=root/"r.csv"
            gs=[node("A",0,0),node("B",0,20)]
            rs=[record("A",.01),record("B",.03)]
            for path,rows in ((geometry,gs),(response,rs)):
                with path.open("w",newline="",encoding="utf8") as stream:
                    w=csv.DictWriter(stream,fieldnames=list(rows[0]))
                    w.writeheader();w.writerows(rows)
            pairs,gov,manifest=write_outputs(root/"out",geometry,response,
                                               limit_state="ULS",source="OPENSEES")
            self.assertEqual(len(gov),1)
            self.assertEqual(manifest["n_pairs"],1)
            self.assertTrue((root/"out"/"Floor_End_Governing.csv").exists())
            self.assertEqual(manifest["limit_state"],"ULS")

    def test_missing_end_response_is_not_passed(self):
        _,governing=map_floor_ends(self.geometry(),[record("A",.01)],
                                  limit_state="ULS",source="ETABS")
        self.assertEqual(governing[0]["status"],"NOT EVALUATED")
        self.assertTrue(governing[0]["design_acceptance_blocked"])

if __name__=="__main__":
    unittest.main(verbosity=2)
