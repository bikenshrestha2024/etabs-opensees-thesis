"""Full-model NBC acceptance fails closed on real V10.7-style evidence.

The source V10.7 JSON only attests response-spectrum shear normalization,
not a checked Rayleigh period, matched native ETABS/OpenSees, or 224 NLTHA.
"""
import unittest
from components.nbc105.acceptance import evaluate_project_evidence, MANDATORY_GATES

HASH="c13b95a5f8a1544dd9e82c9f27eb222419489c11164f67e1afec1ffaedddad00"

def v107():
    return {
        "status":"PERIOD_RS_MATCH_PASS__NOT_FULL_CODE_COMPLIANCE",
        "source_sha256":HASH,
        "period_policy":"AMPLIFIED_EMPIRICAL_ONLY__NO_ANALYTICAL_PERIOD_CHECK",
        "adopted_periods":{"X":1.981280885026091,"Y":1.9219797767063125},
        "final_rs":[
            {"case":"RSX P Delta","target_kN":24842.191487,
             "observed_kN":24842.191487,"relative_error":0.0,"status":"PASS"},
            {"case":"RSY P Delta","target_kN":25608.676578,
             "observed_kN":25608.676578,"relative_error":0.0,"status":"PASS"},
        ],
        "openSees_equivalence":"NOT_TESTED__REQUIRES_REACTION_MASS_MODAL_DRIFT_TORSION_COMPARISON"
    }

class ProjectEvidence(unittest.TestCase):
    def test_v107_scaling_passes_but_total_acceptance_blocked(self):
        report=evaluate_project_evidence(v107())
        self.assertEqual(report["overall"],"BLOCKED_NOT_FULL_ENGINEERING_ACCEPTANCE")
        self.assertEqual(report["gates"]["rs_base_shear"]["status"],"NUMERIC_MATCH_REPRODUCED")
        self.assertEqual(report["gates"]["rayleigh_period"]["status"],"OPEN")
        self.assertEqual(report["gates"]["etabs_opensees"]["status"],"OPEN")
        self.assertEqual(report["gates"]["nltha_224"]["status"],"OPEN")
        self.assertTrue(set(MANDATORY_GATES).issubset(report["gates"]))

    def test_cannot_hide_missing_native_by_setting_all_pass(self):
        x=v107()
        x["status"]="PASS"
        x["native_validated"]=True
        x["full_code_compliance"]=True
        report=evaluate_project_evidence(x)
        self.assertEqual(report["overall"],"BLOCKED_NOT_FULL_ENGINEERING_ACCEPTANCE")
        self.assertNotEqual(report["gates"]["rayleigh_period"]["status"],"PASS")

    def test_shear_mismatch_is_not_called_pass(self):
        x=v107()
        x["final_rs"][0]["observed_kN"]*=1.02
        report=evaluate_project_evidence(x)
        self.assertEqual(report["gates"]["rs_base_shear"]["status"],"MISMATCH")

    def test_invalid_or_mixed_provenance_rejected(self):
        x=v107()
        x["source_sha256"]="not-a-sha"
        with self.assertRaises(ValueError):
            evaluate_project_evidence(x)

    def test_duplicate_case_not_sufficient_for_two_directions(self):
        x=v107()
        x["final_rs"][1]["case"]="RSX P Delta"
        report=evaluate_project_evidence(x)
        self.assertNotEqual(report["gates"]["rs_base_shear"]["status"],
                            "NUMERIC_MATCH_REPRODUCED")

if __name__ == "__main__":
    unittest.main()
