"""New and archived result-reader regression without OpenSees/ETABS binaries."""
import json
import tempfile
import unittest
from pathlib import Path

from components.validation.response_inventory import available_response_rows


class ResultReaderCompatibility(unittest.TestCase):
    def test_gravity_response_from_canonical_and_legacy_once(self):
        with tempfile.TemporaryDirectory() as d:
            export=Path(d)
            modern=export/"02_GRAVITY"/"RUNS"/"ULS"/"run1"
            modern.mkdir(parents=True)
            gravity=modern/"Gravity_Result_V110.json"
            gravity.write_text(json.dumps({
                "nodes":[
                    {"tag":1,"z_m":0.0,"uz_m":0.0},
                    {"tag":2,"z_m":3.5,"uz_m":-0.005}],
                "local_forces":[{"tag":1101,"axial_kN":5.0}]
            }),encoding="utf-8")
            historical=export/"OpenSees_Analysis_Results"
            historical.mkdir()
            deflection=historical/"Deformation_ULS_X_V132.json"
            deflection.write_text(json.dumps({
                "limit_state":"ULS",
                "displacements":{"2":[0.015,-0.012,0,0,0,0]}
            }),encoding="utf-8")
            drift,actions=available_response_rows(export)
            self.assertEqual(len(drift),4)
            self.assertEqual(len(actions),1)
            self.assertEqual({x["limit_state"] for x in drift},{"AS_CONFIGURED","ULS"})
            # Calling with a nested canonical case must not duplicate results.
            drift2,actions2=available_response_rows(modern)
            self.assertEqual(len(drift2),len(drift))
            self.assertEqual(len(actions2),len(actions))
            self.assertTrue(all(x["status"]=="LIMIT REQUIRED" for x in drift))

    def test_snapshots_do_not_masquerade_as_solver_runs(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            snap=root/"02_GRAVITY"/"REVIEW_SNAPSHOTS"/"old"
            snap.mkdir(parents=True)
            (snap/"Gravity_Result_V110.json").write_text(json.dumps({
                "nodes":[{"tag":1,"z_m":0,"uz_m":-1}]
            }))
            drift,actions=available_response_rows(root)
            self.assertEqual(drift,[])
            self.assertEqual(actions,[])


if __name__=="__main__":
    unittest.main()
