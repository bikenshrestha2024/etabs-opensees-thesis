"""Synthetic ESM solver evidence gate; no native ETABS or OpenSees required."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.equivalent_static.calculation_and_gui import verify_generated_esm_result


class ESMEvidenceGateTests(unittest.TestCase):
    def build_case(self,root,case="ULS_X+_E0"):
        model=root/"OpenSees_Complete_Model_Data_V118.json"
        model.write_text('{"nodes":{}}',encoding="utf-8")
        digest=hashlib.sha256(model.read_bytes()).hexdigest()
        script=root/("OpenSees_NBC105_ESM_Load_And_Static_Analysis_"+case+"_V111.py")
        script.write_text("# synthetic generated runner; not executed\n")
        (root/("NBC105_ESM_Calculation_"+case+"_V111.json")).write_text(json.dumps({
            "direction_case":case,"limit_state":case[:3],
            "stories":[{"height_m":3.8}]
        }))
        (root/("NBC105_ESM_OpenSees_Response_META_"+case+".json")).write_text(json.dumps({
            "model_sha256":digest,"limit_state":case[:3],"axis":case[4],
            "response_case":case
        }))
        (root/("NBC105_ESM_OpenSees_Response_"+case+".json")).write_text(json.dumps([{
            "height_m":3.8,"response_case":case,"U_elastic_m":0.003,
            "U_design_m":0.004,"design_drift_ratio":0.001
        }]))
        (root/("Response_Recorder_Index_"+case+".json")).write_text(json.dumps({
            "analysis":"equivalent_static","files":[{"name":"test.csv"}]
        }))
        with (root/("NBC105_ESM_Support_Reactions_"+case+".csv")).open(
                "w",encoding="utf-8",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=("node_tag","Fx_kN"))
            writer.writeheader()
            writer.writerow({"node_tag":1,"Fx_kN":-100})
        return script

    def test_complete_saved_evidence_and_source_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            script=self.build_case(root)
            evidence=verify_generated_esm_result(script,root)
            self.assertEqual(evidence["status"],"COMPLETE_SAVED_RESPONSE_ONLY")
            self.assertEqual(evidence["stories"],1)
            self.assertEqual(evidence["support_count"],1)
            self.assertEqual(evidence["engineering_acceptance"],"NOT_VERIFIED")
            (root/"OpenSees_Complete_Model_Data_V118.json").write_text("changed")
            with self.assertRaisesRegex(ValueError,"metadata differs"):
                verify_generated_esm_result(script,root)

    def test_primary32_saved_response_cannot_claim_76_reaction_nodes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            script=self.build_case(root)
            case="ULS_X+_E0"
            calculation=root/("NBC105_ESM_Calculation_"+case+"_V111.json")
            metadata=json.loads(calculation.read_text())
            metadata["support_case"]="PHYSICAL_32"
            calculation.write_text(json.dumps(metadata))
            reaction=root/("NBC105_ESM_Support_Reactions_"+case+".csv")
            with reaction.open("w",encoding="utf-8",newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=("node_tag","Fx_kN"))
                writer.writeheader()
                writer.writerows({"node_tag":i+1,"Fx_kN":-100/76} for i in range(76))
            with self.assertRaisesRegex(ValueError,"support reaction"):
                verify_generated_esm_result(script,root)

    def test_missing_or_mismatched_production_output_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            script=self.build_case(root,case="SLS_Y+_E0")
            response=root/"NBC105_ESM_OpenSees_Response_SLS_Y+_E0.json"
            response.unlink()
            with self.assertRaisesRegex(ValueError,"missing/empty"):
                verify_generated_esm_result(script,root)
            response.write_text(json.dumps([{
                "height_m":3.8,"response_case":"SLS_X+_E0","U_elastic_m":0,
                "U_design_m":0,"design_drift_ratio":0
            }]))
            with self.assertRaisesRegex(ValueError,"case mismatch"):
                verify_generated_esm_result(script,root)
            data=json.loads(response.read_text())
            data[0]["response_case"]="SLS_Y+_E0"
            data[0]["design_drift_ratio"]=float("nan")
            response.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,"nonfinite"):
                verify_generated_esm_result(script,root)


if __name__=="__main__":
    unittest.main()
