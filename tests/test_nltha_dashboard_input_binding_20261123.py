"""NLTHA dashboard must share the existing run-gate source-binding contract.

All paths/data are synthetic; no native EDB, project workbook or OpenSees solve.
[REF docs/source/components/model/readiness_dashboard.py.md]
"""
import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from components.model.readiness import BINDING_FIELDS, record_binding
from components.model.readiness_dashboard import audit, REVIEW_KEYS


def signed_synthetic_project(tmp):
    root=Path(tmp)
    model=root/"OpenSees_Complete_Nonlinear_Model.py"
    model.write_text("print('synthetic nonlinear builder')\n",encoding="utf-8")
    material=root/"calibrated_synthetic_materials.json"
    material.write_text('{"synthetic":true,"material":1}',encoding="utf-8")
    config=root/"OpenSees_Complete_Model_Config_V118.json"
    config.write_text(json.dumps({
        "nonlinear_materials_file":material.name,
        "nonlinear_wall_fsam_tags":{"W1":{"tag":101}},
        "nonlinear_parameters_reviewed":True,
    }),encoding="utf-8")
    review_keys={key for group_keys in REVIEW_KEYS.values() for key in group_keys}
    data={
        "model_script":str(model.resolve()),
        "model_script_sha256":hashlib.sha256(model.read_bytes()).hexdigest(),
        "approved_for_nltha":True,
        "checks":{key:True for key in review_keys},
        "evidence":{key:"Synthetic reviewer statement (NOT physics acceptance)"
                    for key in review_keys},
    }
    record_binding(data,model)
    draft=root/("OpenSees_Model_Readiness_Draft_"+model.stem+"_V134.json")
    draft.write_text(json.dumps(data,indent=2),encoding="utf-8")
    return root, model, material, config, draft


class NLTHADashboardBindingTests(unittest.TestCase):
    def test_unchanged_bound_claim_is_a_claim_not_physics_approval(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"MODEL_BOUND_DRAFT_LOADED")
            self.assertTrue(report["approved_for_nltha"])
            self.assertEqual(report["readiness_level"],
                             "MODEL_BOUND_SIGNOFF_RECORDED_NOT_AUTOMATICALLY_VERIFIED")

    def test_legacy_signed_draft_without_all_three_bindings_cannot_claim_current_readiness(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            data=json.loads(draft.read_text(encoding="utf-8"))
            data.pop("model_config_sha256")
            draft.write_text(json.dumps(data),encoding="utf-8")
            before=draft.read_bytes()
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"INPUT_BINDING_NOT_RECORDED")
            self.assertFalse(report["approved_for_nltha"])
            self.assertEqual(report["readiness_level"],"DIAGNOSTIC_ONLY")
            self.assertFalse(any(g["review_claim_present"] for g in report["groups"]))
            self.assertEqual(draft.read_bytes(),before)

    def test_model_config_changed_after_signoff_invalidates_dashboard_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            data=json.loads(config.read_text(encoding="utf-8"))
            data["nonlinear_parameters_reviewed"]=False
            config.write_text(json.dumps(data),encoding="utf-8")
            before=draft.read_bytes()
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"INPUT_BINDING_MISMATCH")
            self.assertFalse(report["approved_for_nltha"])
            self.assertEqual(draft.read_bytes(),before)

    def test_material_file_changed_after_signoff_invalidates_dashboard_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            material.write_text('{"synthetic":true,"material":2}',encoding="utf-8")
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"INPUT_BINDING_MISMATCH")
            self.assertFalse(report["approved_for_nltha"])

    def test_wall_fsam_mapping_changed_after_signoff_invalidates_dashboard_claim(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            data=json.loads(config.read_text(encoding="utf-8"))
            data["nonlinear_wall_fsam_tags"]={"W1":{"tag":202}}
            config.write_text(json.dumps(data),encoding="utf-8")
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"INPUT_BINDING_MISMATCH")
            self.assertFalse(report["approved_for_nltha"])

    def test_removed_material_cannot_reuse_saved_file_fingerprint(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            material.unlink()
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"INPUT_BINDING_MISMATCH")
            self.assertFalse(report["approved_for_nltha"])

    def test_missing_material_at_signoff_is_not_approvable_even_with_none_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root,model,material,config,draft=signed_synthetic_project(td)
            material.unlink()
            data=json.loads(draft.read_text(encoding="utf-8"))
            record_binding(data,model)
            self.assertTrue(all(key in data for key in BINDING_FIELDS))
            draft.write_text(json.dumps(data),encoding="utf-8")
            report=audit(root,model)
            self.assertEqual(report["draft_state"],"INPUT_BINDING_INCOMPLETE")
            self.assertFalse(report["approved_for_nltha"])


if __name__=="__main__":
    unittest.main()
