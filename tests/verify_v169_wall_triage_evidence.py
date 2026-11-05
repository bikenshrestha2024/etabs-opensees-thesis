"""V169 first-step diagnostics: isolation provenance, bounded wall snapshots.

No native OpenSees or private EDB is used. These tests do not identify the
physical cause of the t=0.005 s transient failure.
"""
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from components.nonlinear_time_history.thesis_quality import (
    generate_isolation_configs,review_isolation_runs)
from components.nonlinear_time_history.failure_evidence import (
    snapshot_selected_state,snapshot_failed_step)


class FakeOps:
    def getTime(self):return 0.0
    def getEleTags(self):return [110280,112778,100001]
    def getNodeTags(self):return [11,12,13]
    def eleNodes(self,tag):return [11,12] if tag==110280 else [12,13]
    def nodeCoord(self,node):return [6.,6.,3.8]
    def nodeDisp(self,node):return [0.,0.,0.,0.,0.,0.]
    def nodeVel(self,node):return [0.]*6
    def nodeAccel(self,node):return [0.]*6
    def eleResponse(self,tag,*args):
        if args==("localForce",):return [math.nan] if tag==110280 else [0.]
        if args==("ShearDef",):raise RuntimeError("unsupported wall response")
        return []


def source(root,state="ULS",dt=.005):
    model=root/"actual_model";model.mkdir()
    (model/"OpenSees_Complete_Model_Data_V118.json").write_text('{"nodes":{}}')
    a=root/"kobe_A.txt";b=root/"kobe_B.txt"
    a.write_text("0.0\\n0.01");b.write_text("0.0\\n-0.01")
    return dict(model_folder=str(model),x_path=str(a),y_path=str(b),
                limit_state=state,dt_s=dt,analysis_intent="RESEARCH_DIAGNOSTIC",
                orientations=["XY"],nonlinear_walls=True)


class TriageEvidence(unittest.TestCase):
    def test_probe_generation_preserves_service_and_actual_time(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);c=source(root,"SLS",.0025)
            before=dict(c)
            files=generate_isolation_configs(c,root/"diagnostics")
            self.assertEqual(c,before)
            self.assertEqual(len(files),4)
            manifest=json.loads((root/"diagnostics"/"00_Probe_Evidence_Manifest.json").read_text())
            self.assertEqual(manifest["dt_s"],.0025)
            self.assertEqual(manifest["limit_state"],"SLS")
            self.assertEqual(len(manifest["input_fingerprints"]["record_A_sha256"]),64)
            for file in files:
                r=json.loads(Path(file).read_text())
                self.assertEqual(r["limit_state"],"SLS")
                self.assertEqual(r["duration_s"],.0025)
                self.assertEqual(r["diagnostic_suspect_tags"],[110280,112778])
                self.assertTrue(r["diagnostic_zero_damping"])
            with self.assertRaises(FileExistsError):
                generate_isolation_configs(c,root/"diagnostics")

    def test_production_intent_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);c=source(root)
            c["analysis_intent"]="THESIS_NLTHA"
            with self.assertRaisesRegex(ValueError,"RESEARCH_DIAGNOSTIC"):
                generate_isolation_configs(c,root/"diagnostics")

    def test_missing_source_records_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);c=source(root)
            Path(c["x_path"]).unlink()
            with self.assertRaises(FileNotFoundError):
                generate_isolation_configs(c,root/"diagnostics")

    def test_review_cannot_pass_wrong_model_or_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);c=source(root)
            generate_isolation_configs(c,root/"diagnostics")
            summary=root/"diagnostics"/"ZERO"/"XY"/"Case_Summary.json"
            summary.parent.mkdir(parents=True)
            summary.write_text(json.dumps(dict(status="COMPLETED_TRUNCATED_TRIAL",
                physical_time_s=.005,full_record_duration_s=45.,
                limit_state="ULS",diagnostic_excitation="X",
                model_sha256="incorrect")),encoding="utf8")
            r=review_isolation_runs(root/"diagnostics")
            self.assertEqual(r["probe_results"][0]["status"],"INCOMPLETE")

    def test_focused_last_accepted_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/"committed.json"
            r=snapshot_selected_state(FakeOps(),file,suspect_tags=[110280,999999])
            self.assertEqual(r["status"],"LAST_ACCEPTED_COMMITTED")
            self.assertEqual(r["missing_tags"],[999999])
            self.assertEqual(r["elements"][0]["responses"]["ShearDef"]["status"],"UNSUPPORTED_OR_ERROR")
            self.assertEqual(r["elements"][0]["responses"]["localForce"]["status"],"NONFINITE")
            self.assertTrue(file.exists())

    def test_focused_failure_does_not_sweep_every_node_and_element(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/"failure.json"
            r=snapshot_failed_step(FakeOps(),file,algorithm="Newton",
                dt=.005,return_code=-3,suspect_tags=[110280])
            self.assertEqual(r["nodes_scanned"],0)
            self.assertEqual(r["elements_scanned"],1)
            self.assertEqual(r["nonfinite_elements"][0]["tag"],110280)
            self.assertEqual(r["focused_element_tags"],[110280])


if __name__=="__main__":
    unittest.main(verbosity=2)
