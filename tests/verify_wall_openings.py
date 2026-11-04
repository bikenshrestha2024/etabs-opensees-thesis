"""Wall opening occupancy tests — isolated geometry, no OpenSeesPy."""
import unittest
from components.nonlinear_time_history.wall_topology import (validate_openings, verify_project_opening_manifest_required)
def panel(x0,x1,z0,z1,obj):
    return dict(object=obj,category="SHEAR WALL",
                nodes=[obj*10+i for i in range(4)],properties={"thickness":.4})
def sample(filled=False):
    nodes={}
    shells=[]
    cells=[(0,1,0,3,1),(2,3,0,3,2)]
    if filled:cells.append((1,2,0,3,3))
    for x0,x1,z0,z1,obj in cells:
        tags=[obj*10+i for i in range(4)]
        for tag,p in zip(tags,[(x0,0,z0),(x1,0,z0),(x1,0,z1),(x0,0,z1)]):
            nodes[str(tag)]=p
        shells.append(dict(object=obj,category="SHEAR WALL",nodes=tags))
    return dict(nodes=nodes,shells=shells)
def opening():
    return dict(id="O1",plane="XZ",constant_m=0.0,
                horizontal_min_m=1,horizontal_max_m=2,z_min_m=0,z_max_m=3,
                source="ETABS opening audit")
class OpeningTests(unittest.TestCase):
    def test_actual_void_screen(self):
        r=validate_openings(sample(),[opening()])
        self.assertEqual(r["status"],"GEOMETRY_SCREEN_PASSED")
    def test_detect_filled_opening(self):
        r=validate_openings(sample(True),[opening()])
        self.assertEqual(r["status"],"BLOCKED")
        self.assertEqual(r["openings"][0]["overlapping_wall_objects"],["3"])
    def test_thesis_cannot_skip_core_opening_declarations(self):
        with self.assertRaisesRegex(ValueError,"wall_openings_manifest"):
            verify_project_opening_manifest_required({"analysis_intent":"THESIS_NLTHA"})
    def test_exploratory_does_not_claim_approved_openings(self):
        self.assertEqual(verify_project_opening_manifest_required({
            "analysis_intent":"RESEARCH_DIAGNOSTIC"})["status"],
            "EXPLORATORY_MANIFEST_OPTIONAL")
    def test_empty_thesis_opening_manifest_is_rejected(self):
        import tempfile, json
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"openings.json"
            p.write_text(json.dumps({"wall_openings":[]}))
            with self.assertRaisesRegex(ValueError,"nonempty"):
                verify_project_opening_manifest_required({
                    "analysis_intent":"THESIS_NLTHA","wall_openings_manifest":str(p)})

    def test_reject_bad_geometry(self):
        o=opening();o["z_max_m"]=0
        with self.assertRaisesRegex(ValueError,"invalid coordinates"):
            validate_openings(sample(),[o])
if __name__=="__main__":unittest.main()
