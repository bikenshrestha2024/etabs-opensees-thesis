"""Per-run joint-overlap evidence must remain audit-only unless source export
explicitly used a separately verified single-owner policy."""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from components.gravity.source_load_reconciliation import source_load_audit


class GravityJointOverlapIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "source"
        self.out = self.root / "run"
        self.src.mkdir()
        self.data = {
            "load_provenance": [
                {"pattern": "Live", "component": "point_load",
                 "source": "ETABS:PT1", "node": 1, "downward_kN": 10.0}
            ],
            "total_downward_load_kN": 10.0,
            "gravity_by_pattern_kN": {"Live": 10.0},
        }
        self.config = {"joint_volume_weight_policy": "AUDIT_ONLY",
                       "etabs_beam_weight_policy": "GROSS_SECTION_LENGTH"}
        self.joint = {
            "schema": "joint-volume-ownership-v1",
            "policy": "AUDIT_ONLY",
            "geometry_verified": False,
            "potentially_duplicated_RCC_weight_kN": 5.0,
            "rows": [
                dict(kind="frame", index=0, object="C-1",
                     category="COLUMN", gross_weight_kN=24.2,
                     removed_weight_kN=0.0, net_weight_kN=24.2,
                     unit_weight_kN_m3=25.0, retained_ratio=1.0),
                dict(kind="shell", index=0, object="W-1",
                     category="SHEAR WALL", gross_weight_kN=7.2,
                     removed_weight_kN=5.0, net_weight_kN=2.2,
                     unit_weight_kN_m3=25.0, retained_ratio=2.2 / 7.2,
                     overlap_with_COLUMN_m3=0.2),
            ],
        }
        self.write("OpenSees_Complete_Model_Data_V118.json", self.data)
        self.write("OpenSees_Complete_Model_Config_V118.json", self.config)
        self.write("OpenSees_Source_Model_Metadata_V118.json", {})
        self.write("OpenSees_Load_Conversion_Audit.json", {})
        self.write("ETABS_OpenSees_Beam_Weight_Reconciliation.json",
                   {"potential_offset_reduction_kN": 3.0,
                    "gross_beam_weight_kN": 8.0})
        self.write("OpenSees_Joint_Volume_Ownership_Audit.json", self.joint)

    def write(self, filename, data):
        (self.src / filename).write_text(json.dumps(data), encoding="utf-8")

    def audit(self):
        mock_module = types.ModuleType("OpenSees_Complete_Export_V118")
        mock_module.apply_gravity_profile = (
            lambda data, cfg, profile, types: {"factors": {"Live": 1.0}})
        with patch.dict(sys.modules, {"OpenSees_Complete_Export_V118": mock_module}):
            return source_load_audit(self.src, "GRAVITY_1.0D_1.0L",
                                     self.out, etabs_total_kN=9.0)

    def test_per_run_overlap_is_saved_not_subtracted(self):
        result = self.audit()
        evidence = result["joint_overlap_run_evidence"]
        self.assertEqual(evidence["status"],
                         "SOURCE_LEDGER_GEOMETRY_AUDITED_NOT_ETABS_VERIFIED")
        self.assertEqual(evidence["potential_overlap_kN"], 5.0)
        self.assertEqual(evidence["applied_gravity_correction_kN"], 0.0)
        self.assertEqual(result["applied_total_kN"], 10.0)
        self.assertEqual(result["source_to_etabs_difference_kN"], 1.0)
        for item in evidence["files"]:
            self.assertTrue(Path(item).is_file(), item)
        self.assertTrue((self.out / "Gravity_Source_Components_Audit.xlsx").is_file())

    def test_policy_mismatch_fails_closed(self):
        self.config["joint_volume_weight_policy"] = "VERIFIED_SINGLE_OWNER"
        self.write("OpenSees_Complete_Model_Config_V118.json", self.config)
        with self.assertRaisesRegex(ValueError, "policy differs"):
            self.audit()

    def test_missing_optional_ledger_is_explicit(self):
        (self.src / "OpenSees_Joint_Volume_Ownership_Audit.json").unlink()
        result = self.audit()
        self.assertEqual(result["joint_overlap_run_evidence"]["status"],
                         "MISSING_SOURCE_LEDGER_NOT_APPLIED")
        self.assertEqual(result["applied_total_kN"], 10.0)


if __name__ == "__main__":
    unittest.main()
