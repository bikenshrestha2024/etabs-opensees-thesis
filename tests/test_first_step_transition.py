"""First-step NLTHA transition evidence, read-only and solver independent.

No material, element, damping, integration or load pattern changes.
"""
import json
import math
import tempfile
import unittest
from pathlib import Path

from components.nonlinear_time_history.first_step_transition import (
    capture_transition, compare_first_step_stages, diagnostic_focus_tags
)


class FakeWallOps:
    def __init__(self):
        self.clock=0.
        self.mass=(80.,100.,120.)
        self.force=(1.,2.,3.)
        self.missing=False
        self.bad_force=False
        self.calls=[]

    def getEleTags(self): return [] if self.missing else [110280]
    def getNodeTags(self): return [10,11]
    def getTime(self): return self.clock
    def eleNodes(self,tag): return [10,11]
    def nodeCoord(self,tag): return [0.,0.,3.8]
    def nodeDisp(self,tag): return [0.,0.,0.]
    def nodeVel(self,tag): return [0.,0.,0.]
    def nodeAccel(self,tag): return [0.,0.,0.]
    def nodeMass(self,tag,dof):
        self.calls.append(("nodeMass",tag,dof))
        return self.mass[dof-1]
    def eleResponse(self,tag,*args):
        if args[0]=="localForce":
            return [float("nan")] if self.bad_force else self.force
        return []


class FirstStepTransitionTests(unittest.TestCase):
    def test_read_only_stages_capture_wall_and_mass_and_hash(self):
        with tempfile.TemporaryDirectory() as td:
            ops=FakeWallOps()
            path=Path(td)/"case"/"gravity.json"
            evidence=capture_transition(
                ops,path,stage="GRAVITY_FROZEN",focus_tags=[110280],
                source_model_sha256="a"*64)
            self.assertEqual(evidence["status"],"FINITE_WITH_UNSUPPORTED_CHANNELS")
            self.assertEqual(evidence["source_model_sha256"],"a"*64)
            self.assertEqual(evidence["elements"][0]["tag"],110280)
            self.assertEqual(evidence["mass_audit"]["10"]["status"],"FINITE")
            self.assertTrue(path.exists())
            self.assertEqual(evidence["solver_state_modified"],False)
            self.assertEqual(ops.calls.count(("nodeMass",10,1)),1)

    def test_missing_wall_tag_must_not_claim_pass(self):
        with tempfile.TemporaryDirectory() as td:
            ops=FakeWallOps()
            ops.missing=True
            evidence=capture_transition(ops,Path(td)/"missing.json",
                                        stage="BEFORE_EXCITATION",
                                        focus_tags=[110280])
            self.assertEqual(evidence["status"],"FOCUSED_ELEMENT_ABSENT")
            self.assertEqual(evidence["missing_tags"],[110280])

    def test_nonfinite_wall_is_classified_without_fabricating_root_cause(self):
        with tempfile.TemporaryDirectory() as td:
            ops=FakeWallOps()
            ops.bad_force=True
            evidence=capture_transition(ops,Path(td)/"bad.json",
                                        stage="FIRST_ACCEPTED_STEP",
                                        focus_tags=[110280])
            self.assertEqual(evidence["status"],"NONFINITE_FOCUSED_RESPONSE")
            self.assertNotIn("root_cause",evidence)
            self.assertEqual(
                evidence["elements"][0]["responses"]["localForce"]["status"],
                "NONFINITE")

    def test_optional_unsupported_mass_is_not_assumed_zero(self):
        with tempfile.TemporaryDirectory() as td:
            ops=FakeWallOps()
            ops.nodeMass=lambda *args: (_ for _ in ()).throw(RuntimeError("unsupported"))
            evidence=capture_transition(ops,Path(td)/"unsupported.json",
                                        stage="AFTER_EIGEN",
                                        focus_tags=[110280])
            self.assertEqual(evidence["mass_audit"]["10"]["status"],
                             "UNSUPPORTED_OR_ERROR")
            self.assertNotIn("values",evidence["mass_audit"]["10"])

    def test_stage_comparison_reports_onset_not_causation(self):
        with tempfile.TemporaryDirectory() as td:
            ops=FakeWallOps()
            root=Path(td)
            capture_transition(ops,root/"gravity.json",stage="GRAVITY_FROZEN",
                               focus_tags=[110280])
            ops.bad_force=True
            capture_transition(ops,root/"pre.json",stage="BEFORE_EXCITATION",
                               focus_tags=[110280])
            report=compare_first_step_stages(
                [root/"gravity.json",root/"pre.json"],
                root/"comparison.json")
            self.assertEqual(report["status"],"ONSET_BRACKET_REQUIRES_NATIVE_REVIEW")
            self.assertEqual(report["first_nonfinite_stage"],"BEFORE_EXCITATION")
            self.assertFalse(report["engineering_root_cause_proven"])
            self.assertEqual(report["last_finite_stage"],"GRAVITY_FROZEN")

    def test_stage_comparison_rejects_mixed_source_model_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            good={"status":"FINITE_WITH_UNSUPPORTED_CHANNELS",
                  "stage":"GRAVITY_FROZEN",
                  "source_model_sha256":"a"*64}
            wrong={**good,"stage":"AFTER_EIGEN",
                   "source_model_sha256":"b"*64}
            (root/"one.json").write_text(json.dumps(good))
            (root/"two.json").write_text(json.dumps(wrong))
            with self.assertRaisesRegex(ValueError,"source model"):
                compare_first_step_stages(
                    [root/"one.json",root/"two.json"],root/"comparison.json")
            wrong["source_model_sha256"]=None
            (root/"two.json").write_text(json.dumps(wrong))
            with self.assertRaisesRegex(ValueError,"source model"):
                compare_first_step_stages(
                    [root/"one.json",root/"two.json"],root/"comparison.json")
            self.assertFalse((root/"comparison.json").exists())

    def test_stage_comparison_requires_strict_chronological_stages(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            first={"status":"FINITE_WITH_UNSUPPORTED_CHANNELS",
                   "stage":"BEFORE_EXCITATION",
                   "source_model_sha256":"a"*64}
            later={**first,"stage":"GRAVITY_FROZEN"}
            (root/"a.json").write_text(json.dumps(first))
            (root/"b.json").write_text(json.dumps(later))
            with self.assertRaisesRegex(ValueError,"chronological"):
                compare_first_step_stages(
                    [root/"a.json",root/"b.json"],root/"comparison.json")
            later["stage"]="BEFORE_EXCITATION"
            (root/"b.json").write_text(json.dumps(later))
            with self.assertRaisesRegex(ValueError,"chronological"):
                compare_first_step_stages(
                    [root/"a.json",root/"b.json"],root/"comparison.json")

    def test_do_not_use_boolean_or_fractional_tags(self):
        for value in (True,0,-1,110280.5,"110280.5"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    diagnostic_focus_tags({"first_step_focus_tags":[value]})

    def test_default_watched_wall_and_explicit_enable(self):
        self.assertEqual(diagnostic_focus_tags({}),[110280])
        self.assertEqual(diagnostic_focus_tags(
            {"first_step_focus_tags":[110280,"110281"]}),[110280,110281])

    def test_recovered_first_step_retains_failed_attempt_in_diagnostic_mode(self):
        from components.nonlinear_time_history.runner_and_gui import (
            _advance_nonlinear_interval)
        class FakeAnalyser:
            def __init__(self):self.clock=0.;self.attempts=0
            def test(self,*args): pass
            def algorithm(self,*args): pass
            def getTime(self):return self.clock
            def getNodeTags(self):return []
            def getEleTags(self):return []
            def testIter(self):return 3
            def analyze(self,*args):
                self.attempts+=1
                if self.attempts==1:return -3
                self.clock+=args[-1]
                return 0
        with tempfile.TemporaryDirectory() as td:
            evidence=Path(td)/"failed_attempt.json"
            ops=FakeAnalyser()
            observed=[]
            diagnostics={
                "evidence_output_path":str(evidence),
                "preserve_first_step_failure_evidence":True}
            accepted=_advance_nonlinear_interval(
                ops,.005,on_accept=lambda:observed.append(ops.getTime()),
                diagnostics=diagnostics)
            self.assertEqual(accepted,1)
            self.assertEqual(ops.attempts,2)
            self.assertEqual(observed,[.005])
            self.assertTrue(evidence.is_file())
            payload=json.loads(evidence.read_text())
            self.assertEqual(payload["return_code"],-3)
            self.assertEqual(diagnostics["failed_attempts"],1)

    def test_default_success_removes_only_same_case_stale_failure_evidence(self):
        from components.nonlinear_time_history.runner_and_gui import (
            _advance_nonlinear_interval)
        class Success:
            def test(self,*args):pass
            def algorithm(self,*args):pass
            def analyze(self,*args):return 0
            def getTime(self):return .005
            def testIter(self):return 1
        with tempfile.TemporaryDirectory() as td:
            evidence=Path(td)/"prior.json"
            evidence.write_text('{"previous_failure":true}')
            result=_advance_nonlinear_interval(
                Success(),.005,diagnostics={"evidence_output_path":str(evidence)})
            self.assertEqual(result,1)
            self.assertFalse(evidence.exists())

    def test_invalid_stage_and_source_hash_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                capture_transition(FakeWallOps(),Path(td)/"x.json",
                                   stage="PHYSICS_VERIFIED",focus_tags=[110280])
            with self.assertRaises(ValueError):
                capture_transition(FakeWallOps(),Path(td)/"x.json",
                                   stage="AFTER_EIGEN",focus_tags=[110280],
                                   source_model_sha256="not-sha")

if __name__=="__main__":
    unittest.main()
