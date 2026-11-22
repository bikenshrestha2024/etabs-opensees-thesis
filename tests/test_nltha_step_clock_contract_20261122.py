"""Safety regression for NLTHA accepted/retried steps (reference-framework review).

No native ETABS/OpenSees is substituted by these deterministic fake-solver cases.
[REF docs/source/components/nonlinear_time_history/full_record_gate.py.md]
"""
import unittest

from components.nonlinear_time_history.full_record_gate import (
    verify_committed_transient_increment,
)
from components.nonlinear_time_history.first_step_transition import (
    require_accepted_focused_step,
)
from components.nonlinear_time_history.runner_and_gui import (
    _advance_nonlinear_interval,
)


class TinySolver:
    def __init__(self, code_time):
        self.answers=iter(code_time)
        self.clock=0.0
        self.calls=[]
    def test(self,*args):pass
    def algorithm(self,name):self.calls.append(name)
    def analyze(self,n,dt):
        code,advance=next(self.answers)
        self.clock+=advance
        return code
    def getTime(self):return self.clock
    def getNodeTags(self):return []
    def getEleTags(self):return []
    def testIter(self):return 2


class AcceptedTransientStepContract(unittest.TestCase):
    def test_pure_clock_validator_rejects_false_zero_return_without_progress(self):
        with self.assertRaisesRegex(RuntimeError,"did not advance|advance.*time"):
            verify_committed_transient_increment(0.,0.,.005)
    def test_pure_clock_validator_rejects_overshoot_and_nonfinite(self):
        with self.assertRaisesRegex(RuntimeError,"requested"):
            verify_committed_transient_increment(0.,.01,.005)
        with self.assertRaisesRegex(ValueError,"finite"):
            verify_committed_transient_increment(0.,float('nan'),.005)
    def test_pure_clock_validator_records_precise_subdivision(self):
        observed=verify_committed_transient_increment(.005,.0075,.0025)
        self.assertAlmostEqual(observed['accepted_dt_s'],.0025)
        self.assertAlmostEqual(observed['end_time_s'],.0075)
    def test_solver_zero_without_time_advance_fails_without_recording_success(self):
        solver=TinySolver([(0,0.)])
        diag={}
        with self.assertRaisesRegex(RuntimeError,"did not advance|advance.*time"):
            _advance_nonlinear_interval(solver,.005,max_depth=0,
                                         on_accept=lambda:self.fail("recorded false success"),
                                         diagnostics=diag)
        self.assertNotIn('minimum_accepted_dt_s',diag)
    def test_failed_solver_advancing_trial_clock_must_not_retry_contaminated_state(self):
        solver=TinySolver([(-3,.005)])
        with self.assertRaisesRegex(RuntimeError,"failed.*advanced|advanced.*failed"):
            _advance_nonlinear_interval(solver,.005,max_depth=5)
        self.assertEqual(solver.calls,['Newton'])
    def test_fallback_progress_and_diagnostics_are_independently_audited(self):
        solver=TinySolver([(-3,0.),(0,.005)])
        diag={}
        captured=[]
        n=_advance_nonlinear_interval(
            solver,.005,max_depth=0,
            on_accept=lambda:captured.append(solver.getTime()),
            diagnostics=diag)
        self.assertEqual(n,1)
        self.assertEqual(captured,[.005])
        self.assertEqual(diag['failed_attempts'],1)
        self.assertEqual(diag['accepted_steps'],1)
        self.assertEqual(diag['first_accepted_step']['algorithm'],'NewtonLineSearch')
        self.assertAlmostEqual(diag['first_accepted_step']['accepted_dt_s'],.005)
    def test_callback_failure_is_never_counted_as_accepted_step(self):
        solver=TinySolver([(0,.005)])
        diag={}
        def bad_callback():
            raise RuntimeError("response recorder nonfinite")
        with self.assertRaisesRegex(RuntimeError,"response recorder nonfinite"):
            _advance_nonlinear_interval(solver,.005,max_depth=0,
                                         on_accept=bad_callback,diagnostics=diag)
        self.assertNotIn('accepted_steps',diag)
        self.assertNotIn('minimum_accepted_dt_s',diag)



class AcceptedWallFocusGate(unittest.TestCase):
    def test_reported_nonfinite_wall_after_zero_return_cannot_be_accepted(self):
        payload={"stage":"FIRST_ACCEPTED_STEP",
                 "status":"NONFINITE_FOCUSED_RESPONSE",
                 "elements":[{"tag":110280,"responses":{
                   "localForce":{"status":"NONFINITE"}}}],
                 "source_model_sha256":"a"*64}
        with self.assertRaisesRegex(RuntimeError,"nonfinite|NONFINITE"):
            require_accepted_focused_step(payload)
    def test_unmapped_requested_wall_does_not_count_as_valid_focus(self):
        payload={"stage":"FIRST_ACCEPTED_STEP",
                 "status":"FOCUSED_ELEMENT_ABSENT",
                 "missing_tags":[110280]}
        with self.assertRaisesRegex(RuntimeError,"110280"):
            require_accepted_focused_step(payload)
    def test_finite_focused_snapshot_preserves_limited_evidence(self):
        source={"stage":"FIRST_ACCEPTED_STEP",
                "status":"FINITE_WITH_UNSUPPORTED_CHANNELS",
                "diagnostic_limitations":["not a validated model"]}
        self.assertIs(require_accepted_focused_step(source),source)
    def test_wrong_stage_must_not_be_mislabeled_accepted(self):
        with self.assertRaisesRegex(ValueError,"FIRST_ACCEPTED_STEP"):
            require_accepted_focused_step({
                "stage":"BEFORE_EXCITATION",
                "status":"FINITE_WITH_UNSUPPORTED_CHANNELS"})


if __name__=='__main__':
    unittest.main()
