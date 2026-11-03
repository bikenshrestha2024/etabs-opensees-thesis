"""Solver-free mock FVD and BRB response mapping tests."""
import json
import tempfile
import unittest
from pathlib import Path
from components.nonlinear_time_history.device_recording import (
active_device_catalog,baseline_axial_projection,device_sample,summarize_device_demands)
class Ops:
    def nodeDisp(self,n):return [0.1 if n==2 else 0.,0,0]
    def nodeVel(self,n):return [.02 if n==2 else 0.,0,0]
    def eleResponse(self,tag,response):return [25.]
    def getTime(self):return .005
class Tests(unittest.TestCase):
    def test_mapping(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,"OpenSees_Element_Overrides_V125.json").write_text(json.dumps(
                dict(active=True,assignments={"FRAME:B1":{"target":"FVD_MAXWELL"}})))
            out=active_device_catalog(d,[dict(object="B1",nodes=[1,2])])
            self.assertEqual(out[0]["tag"],100001)
    def test_sampler(self):
        d=dict(tag=100001,node_i=1,node_j=2,source_frame="B1",kind="FVD")
        nodes={"1":[0,0,0],"2":[1,0,0]}
        self.assertAlmostEqual(baseline_axial_projection(Ops(),d,nodes),.1)
        r=device_sample(Ops(),d,nodes,0)
        self.assertAlmostEqual(r["relative_velocity_m_s"],.02)
        self.assertFalse(summarize_device_demands([r])[0]["energy_sign_approved"])
    def test_missing_force_blocks(self):
        class Bad(Ops):
            def eleResponse(self,tag,response):return []
        with self.assertRaisesRegex(ValueError,"expected scalar"):
            device_sample(Bad(),dict(tag=1,node_i=1,node_j=2,source_frame="B1",kind="FVD"),
                          {"1":[0,0,0],"2":[1,0,0]},0)
if __name__=="__main__":unittest.main()
