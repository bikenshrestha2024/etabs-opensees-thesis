"""Synthetic conservation and no-double-deduction tests; NOT native ETABS validation."""
import json
import tempfile
import unittest
from pathlib import Path

from components.gravity.joint_weight_reconciliation import (
    reconcile_joint_weight_scenarios)


class QuantityReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root/"export"
        self.src.mkdir()
        self.out = self.root/"gravity"
        self.ledger = {
            "schema": "joint-volume-ownership-v1",
            "policy": "AUDIT_ONLY", "geometry_verified": False,
            "gross_RCC_weight_kN": 150,
            "net_RCC_weight_kN": 145,
            "potentially_duplicated_RCC_weight_kN": 5,
            "overlap_pair_weight_kN": {"BEAM_OVERLAPS_COLUMN": 5},
            "rows": [
                dict(category="COLUMN", object="C1", kind="frame", gross_weight_kN=40,
                     net_weight_kN=40, removed_weight_kN=0),
                dict(category="SHEAR WALL", object="W1", kind="shell", gross_weight_kN=30,
                     net_weight_kN=30, removed_weight_kN=0),
                dict(category="FLOOR", object="S1", kind="shell", gross_weight_kN=30,
                     net_weight_kN=30, removed_weight_kN=0),
                dict(category="BEAM", object="B1", kind="frame", gross_weight_kN=50,
                     net_weight_kN=45, removed_weight_kN=5),
            ],
            "unsupported_items": [
                {"kind": "frame", "object": "BR1",
                 "reason": "brace not modeled as rectangular RCC solid"}
            ],
        }
        self.beam = {
            "schema": "beam-self-weight-end-offset-v1",
            "policy": "GROSS_SECTION_LENGTH", "beam_count": 1,
            "rows": [{"etabs_object": "B1", "gross_weight_kN": 50.0}],
            "gross_beam_weight_kN": 50,
            "selected_beam_weight_kN": 50,
            "potential_offset_reduction_kN": 10,
        }
        self.write("OpenSees_Joint_Volume_Ownership_Audit.json", self.ledger)
        self.write("ETABS_OpenSees_Beam_Weight_Reconciliation.json", self.beam)
        self.write("Gravity_Slab_Self_Weight_Audit.json",
                   {"gross_slab_self_weight_kN": 30})
        self.write("OpenSees_Complete_Model_Config_V118.json", {
            "joint_volume_weight_policy": "AUDIT_ONLY",
            "etabs_beam_weight_policy": "GROSS_SECTION_LENGTH"})

    def write(self, name, payload):
        (self.src/name).write_text(json.dumps(payload), encoding="utf-8")

    def run_audit(self):
        return reconcile_joint_weight_scenarios(
            self.src, self.out, 200, 190,
            by_component={"self_weight_brace": 7})

    def test_exclusive_scenarios_and_no_model_modifications(self):
        result = self.run_audit()
        alternatives = result["scenarios_EXCLUSIVE_NOT_APPLIED"]
        self.assertEqual([r["total_kN"] for r in alternatives],
                         [200, 190, 195])
        self.assertEqual(alternatives[1]["scenario_minus_etabs_kN"], 0)
        self.assertTrue(alternatives[0]["applied"])
        self.assertFalse(alternatives[1]["applied"])
        self.assertFalse(alternatives[2]["applied"])
        self.assertEqual(result["automatic_gravity_correction_kN"], 0)
        self.assertEqual(result["original_beam_objects"], 1)
        self.assertEqual(result["original_RCC_source_objects"], 4)
        self.assertTrue((self.out/"Gravity_Original_ETABS_Object_Quantities.csv").is_file())
        self.assertEqual(result["beam_finite_element_segments"], 1)
        self.assertEqual(result["applied_gravity_components_kN"]["self_weight_brace"], 7)
        for filename in ("Gravity_Joint_Weight_Reconciliation.json",
                         "Gravity_Joint_Weight_Scenarios.csv",
                         "Gravity_Joint_Weight_By_Solid.csv"):
            self.assertTrue((self.out/filename).is_file(), filename)

    def test_rejects_invalid_union_ownership(self):
        self.ledger["overlap_pair_weight_kN"]["BEAM_OVERLAPS_COLUMN"] = 7
        self.write("OpenSees_Joint_Volume_Ownership_Audit.json", self.ledger)
        with self.assertRaisesRegex(ValueError, "union attribution"):
            self.run_audit()

    def test_rejects_source_policy_mismatch(self):
        self.ledger["policy"] = "VERIFIED_SINGLE_OWNER"
        self.write("OpenSees_Joint_Volume_Ownership_Audit.json", self.ledger)
        with self.assertRaisesRegex(ValueError, "policy differ"):
            self.run_audit()

    def test_rejects_duplicate_beam_objects(self):
        self.beam["beam_count"] = 2
        self.write("ETABS_OpenSees_Beam_Weight_Reconciliation.json", self.beam)
        with self.assertRaisesRegex(ValueError, "beam count"):
            self.run_audit()


if __name__ == "__main__":
    unittest.main()
