"""Solver-free, file-bound readiness dashboard regression tests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from components.model.readiness_dashboard import GROUPS, audit, export_report, discover_project_model

class ReadinessTests(unittest.TestCase):
    def test_discover_unique_nonlin_builder_for_inspection_only(self):
        with tempfile.TemporaryDirectory() as d:
            model = Path(d, "OpenSees_Complete_Nonlinear_Model.py")
            model.write_text("pass\\n")
            discovered, status = discover_project_model(d)
            self.assertEqual(discovered, model.resolve())
            self.assertIn("UNREVIEWED", status)
            result = audit(d, discovered)
            self.assertFalse(result["approved_for_nltha"])
            self.assertEqual(result["readiness_level"], "DIAGNOSTIC_ONLY")
            self.assertEqual(len(result["model_sha256"]), 64)

    def test_gravity_builder_never_substitutes_for_nonlin_model(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "OpenSees_Complete_Gravity_Model.py").write_text("pass\\n")
            discovered, status = discover_project_model(d)
            self.assertIsNone(discovered)
            self.assertEqual(status, "NO_PROJECT_NONLINEAR_BUILDER_FOUND")

    def test_missing_model_no_automatic_approval(self):
        with tempfile.TemporaryDirectory() as d:
            result = audit(d)
            self.assertEqual(result["readiness_level"], "DIAGNOSTIC_ONLY")
            self.assertFalse(result["approved_for_nltha"])
            self.assertEqual(len(result["groups"]), len(GROUPS))
            self.assertGreater(result["counts"]["MISSING_EVIDENCE"], 0)

    def test_file_presence_is_not_physical_pass(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "OpenSees_Complete_Model_Data_V118.json").write_text("{}")
            result = audit(d)
            group = next(g for g in result["groups"] if g["id"] == "model")
            self.assertEqual(group["status"], "EVIDENCE_FOUND_REVIEW_REQUIRED")
            self.assertFalse(group["review_claim_present"])
            self.assertEqual(len(group["evidence"][0]["sha256"]), 64)

    def test_signed_draft_cannot_override_different_model_hash(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            model = root / "model.py"
            model.write_text("print('original')\n")
            draft = root / "OpenSees_Model_Readiness_Draft_model_V134.json"
            draft.write_text(json.dumps(dict(
                model_script=str(model),
                model_script_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                approved_for_nltha=True, checks={"key": True}, evidence={"key": "review"})))
            model.write_text("print('changed')\n")
            result = audit(root, model)
            self.assertEqual(result["draft_state"], "MODEL_SHA_MISMATCH")
            self.assertFalse(result["approved_for_nltha"])

    def test_signed_claim_is_not_experimental_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            model = root / "model.py"
            model.write_text("pass\n")
            required = set(k for group in GROUPS for k in
                __import__("components.model.readiness_dashboard",
                           fromlist=["REVIEW_KEYS"]).REVIEW_KEYS.get(group[0],()))
            draft = root / "OpenSees_Model_Readiness_Draft_model_V134.json"
            draft.write_text(json.dumps(dict(
                model_script=str(model),
                model_script_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                approved_for_nltha=True, checks={k: True for k in required},
                evidence={k: "Reviewed source file/path by engineer" for k in required})))
            result = audit(root, model)
            self.assertTrue(result["approved_for_nltha"])
            self.assertEqual(result["readiness_level"],
                "MODEL_BOUND_SIGNOFF_RECORDED_NOT_AUTOMATICALLY_VERIFIED")

    def test_checkbox_without_real_evidence_is_not_signoff(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            model = root / "model.py"
            model.write_text("pass\\n")
            draft = root / "OpenSees_Model_Readiness_Draft_model_V134.json"
            draft.write_text(json.dumps(dict(
                model_script=str(model),
                model_script_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                approved_for_nltha=True, checks={"frame_concrete_and_rebar_materials_reviewed": True},
                evidence={"frame_concrete_and_rebar_materials_reviewed":
                          "AVAILABLE FOR REVIEW: example material file"})))
            result = audit(root, model)
            self.assertFalse(result["approved_for_nltha"])
            self.assertEqual(result["readiness_level"], "DIAGNOSTIC_ONLY")

    def test_export_does_not_write_to_original_model(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = audit(root)
            paths = export_report(result, root / "output")
            self.assertTrue(all(path.is_file() for path in paths))
            loaded = json.loads(paths[0].read_text(encoding="utf-8"))
            self.assertFalse(loaded["approved_for_nltha"])
            self.assertIn("## Evidence detail", paths[1].read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
