"""Selected-export settings audit must not assert native wall or slab EI."""
import json
import tempfile
import unittest
from pathlib import Path

from components.validation.settings_audit import audit
from components.ui.nbc105_settings_panel import build_analysis_settings_review


class SettingsSourceTruthTests(unittest.TestCase):
    def test_missing_config_stays_not_verified(self):
        with tempfile.TemporaryDirectory() as td:
            report=audit(td)
            self.assertEqual(report["overall"],
                             "REVIEW REQUIRED - not a compliance certificate")
            wall=next(r for r in report["rows"]
                      if r["item"]=="Elastic wall effective stiffness")
            self.assertEqual(wall["status"],"ACTION REQUIRED")
            self.assertIn("NOT EXTRACTED",wall["value"])
            slab=next(r for r in report["rows"]
                      if r["item"]=="Conventional slab bending factors")
            self.assertEqual(slab["status"],"CONFIG VALUE MISSING / INVALID")
            self.assertTrue(any(r["item"]=="Current selected export configuration"
                                for r in report["rows"]))

    def test_matched_slabs_are_only_config_matches_not_native_proof(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            cfg=root/"OpenSees_Complete_Model_Config_V118.json"
            cfg.write_text(json.dumps({
                "slab_bending_factor":0.25,
                "slab_bending_factor_sls":0.35,
                "slab_stiffness_source":"IS 16700:2023 Table 5"
            }))
            report=audit(root)
            slab=next(r for r in report["rows"]
                      if r["item"]=="Conventional slab bending factors")
            self.assertEqual(slab["status"],
                             "VERIFY GENERATED ETABS AND OPENSEES SHELL SECTION")
            self.assertIn("CONFIG MATCHES ADOPTED VALUE",slab["basis"])
            wrong=json.loads(cfg.read_text())
            wrong["slab_bending_factor_sls"]=0.50
            cfg.write_text(json.dumps(wrong))
            changed=audit(root)
            slab=next(r for r in changed["rows"]
                      if r["item"]=="Conventional slab bending factors")
            self.assertEqual(slab["status"],
                             "CONFIG FACTOR DISAGREES WITH PROJECT ADOPTION")

    def test_invalid_null_nan_and_missing_source_are_safe(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            cfg=root/"OpenSees_Complete_Model_Config_V118.json"
            cfg.write_text(json.dumps({
                "slab_bending_factor":float("nan"),
                "slab_bending_factor_sls":None,
                "slab_stiffness_source":None
            }))
            report=audit(root)
            slab=next(r for r in report["rows"]
                      if r["item"]=="Conventional slab bending factors")
            self.assertEqual(slab["status"],"CONFIG VALUE MISSING / INVALID")
            self.assertIn("NOT RECORDED",slab["basis"])
            viewed=build_analysis_settings_review(root)
            self.assertTrue(any("not finite" in w for w in viewed["warnings"]))
            self.assertTrue(any("not a valid number" in w
                                for w in viewed["warnings"]))
            cfg.write_text("{broken")
            broken=audit(root)
            self.assertTrue(any(r["status"]=="NOT VERIFIED"
                                for r in broken["rows"]))


if __name__=="__main__":
    unittest.main()
