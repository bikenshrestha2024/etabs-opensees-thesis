"""Solver-free mock FVD and BRB response mapping tests."""
import json
import runpy
import sys
import tempfile
import unittest
from types import ModuleType
from pathlib import Path
from unittest.mock import patch
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

    def test_failed_device_steps_return_nonzero_and_keep_report(self):
        launcher=Path(__file__).resolve().parents[1]/"29_NATIVE_DEVICE_BENCHMARK.py"
        openseespy=ModuleType("openseespy")
        ops=ModuleType("openseespy.opensees")
        ops.version=lambda: "synthetic"
        ops.analyze=lambda *_: -4
        ops.__getattr__=lambda name: (lambda *_: None)
        openseespy.opensees=ops
        modules={"openseespy":openseespy,"openseespy.opensees":ops}
        with tempfile.TemporaryDirectory() as d,patch.dict(sys.modules,modules):
            status=runpy.run_path(str(launcher))["main"](["--output",d])
            report=json.loads((Path(d)/"Native_Device_Benchmark_Report.json").read_text())
            self.assertNotEqual(status,0)
            self.assertEqual(report["status"],"FAILED_NATIVE_STEP")
            self.assertEqual([case["return_code"] for case in report["cases"]],[-4,-4])
if __name__=="__main__":unittest.main()
