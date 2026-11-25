"""Opt-in final relaxed convergence tolerance and failure-report print safety.

Evidence: a 2026-11-24 exploratory run stalled at t=2.386 s with all four
algorithms failing the fixed NormDispIncr 1e-7 test at the deepest subdivision
(final norms from 1.08e-7 upward) while the response was nearly elastic.
These deterministic fake-solver cases do not substitute native OpenSees runs.
[REF docs/source/components/nonlinear_time_history/runner_and_gui.py.md]
"""
import builtins
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from components.nonlinear_time_history import runner_and_gui as reviewed
from components.nonlinear_time_history.runner_and_gui import _advance_nonlinear_interval


class ToleranceSolver:
    """Converges only when the active NormDispIncr tolerance is >= needed."""
    def __init__(self, needed):
        self.needed=needed
        self.tol=None
        self.clock=0.0
        self.tolerances=[]
    def test(self,kind,tol,iters,pflag=0):
        self.tol=tol;self.tolerances.append(tol)
    def algorithm(self,name):pass
    def analyze(self,n,dt):
        if self.tol<self.needed:return -3
        self.clock+=dt
        return 0
    def getTime(self):return self.clock
    def getNodeTags(self):return []
    def getEleTags(self):return []
    def testIter(self):return 7


class RelaxedFinalTolerance(unittest.TestCase):
    def test_shared_default_accepts_the_step_at_1e_6(self):
        solver=ToleranceSolver(needed=1e-6)
        self.assertEqual(_advance_nonlinear_interval(solver,.005,max_depth=0),1)
        self.assertEqual(solver.tolerances,[1e-6])

    def test_relaxed_tolerance_accepts_and_is_counted_not_hidden(self):
        solver=ToleranceSolver(needed=1e-6)
        diag={'convergence_tolerance':1e-7,'final_relaxed_tolerance':1e-6}
        _advance_nonlinear_interval(solver,.005,max_depth=0,diagnostics=diag)
        self.assertEqual(diag['relaxed_tolerance_steps'],1)
        self.assertEqual(solver.tolerances[:4],[1e-7]*4)  # strict tried first
        self.assertEqual(solver.tolerances[-1],1e-6)
        self.assertAlmostEqual(solver.clock,.005)

    def test_relaxed_only_at_deepest_subdivision(self):
        solver=ToleranceSolver(needed=1e-6)
        diag={'convergence_tolerance':1e-7,'final_relaxed_tolerance':1e-6,'efficient_recovery':True}
        _advance_nonlinear_interval(solver,.005,max_depth=1,diagnostics=diag)
        self.assertEqual(diag['relaxed_tolerance_steps'],2)  # two half-steps
        self.assertAlmostEqual(solver.clock,.005)
        self.assertAlmostEqual(diag['minimum_accepted_dt_s'],.0025)

    def test_relaxed_tolerance_that_still_fails_raises(self):
        solver=ToleranceSolver(needed=1e-5)
        with self.assertRaisesRegex(RuntimeError,"Nonlinear step failed"):
            _advance_nonlinear_interval(solver,.005,max_depth=0,
                                         diagnostics={'final_relaxed_tolerance':1e-6})


class ConvergenceSettingValidation(unittest.TestCase):
    def test_validation(self):
        from components.nonlinear_time_history.building_exploratory import validate_convergence_settings as v
        self.assertEqual(v({}),(1e-6,40,None))
        self.assertEqual(v({'convergence_tolerance':1e-7}),(1e-7,40,None))
        self.assertEqual(v({'final_relaxed_tolerance':None}),(1e-6,40,None))
        self.assertEqual(v({'final_relaxed_tolerance':1e-6}),(1e-6,40,None))
        self.assertEqual(v({'convergence_tolerance':1e-7,'final_relaxed_tolerance':1e-6}),(1e-7,40,1e-6))
        for bad in (True,0,-1e-6,1e-7,5e-8,2e-5,'1e-6',float('nan')):
            with self.assertRaises(ValueError,msg=repr(bad)):
                v({'final_relaxed_tolerance':bad})
        with self.assertRaises(ValueError):
            v({'transient_max_iterations':0})


    def test_exploratory_default_accepts_at_nominal_step_and_is_counted(self):
        from components.nonlinear_time_history.building_exploratory import validate_convergence_settings
        tol, iters, final = validate_convergence_settings({})
        diag = dict(convergence_tolerance=tol, convergence_max_iterations=iters,
                    final_relaxed_tolerance=final)
        solver = ToleranceSolver(needed=1e-6)
        self.assertEqual(_advance_nonlinear_interval(solver,.005,max_depth=0,diagnostics=diag),1)
        self.assertEqual(solver.tolerances,[1e-6])
        self.assertEqual(diag['relaxed_tolerance_steps'],1)
        self.assertAlmostEqual(solver.clock,.005)

    def test_strict_opt_in_has_no_relaxed_fallback(self):
        from components.nonlinear_time_history.building_exploratory import validate_convergence_settings
        tol, iters, final = validate_convergence_settings({'convergence_tolerance':1e-7})
        solver = ToleranceSolver(needed=1e-6)
        with self.assertRaisesRegex(RuntimeError,"Nonlinear step failed"):
            _advance_nonlinear_interval(solver,.005,max_depth=0,diagnostics=dict(
                convergence_tolerance=tol, convergence_max_iterations=iters,
                final_relaxed_tolerance=final))
        self.assertEqual(set(solver.tolerances),{1e-7})

    def test_reviewed_runner_accepts_default_and_explicit_strict_tolerances(self):
        from components.nonlinear_time_history.building_exploratory import validate_convergence_settings
        for tolerance in (1e-6,1e-7):
            self.assertEqual(validate_convergence_settings({
                'analysis_intent':'THESIS_NLTHA','convergence_tolerance':tolerance}), (tolerance,40,None))

    def test_reviewed_initial_setup_defaults_to_1e_6(self):
        ops = Mock()
        reviewed._configure_nonlinear_transient(ops)
        ops.test.assert_called_once_with("NormDispIncr", 1e-6, 40, 0)

    def test_reviewed_cli_strict_selection_overrides_the_saved_tolerance(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / 'run.json'
            config.write_text('{"convergence_tolerance": 1e-6}', encoding='utf-8')
            with patch('sys.argv', ['nltha', '--run', str(config), '--strict-tolerance']), \
                    patch.object(reviewed, '_run_analysis') as execute:
                reviewed.main()
            self.assertEqual(execute.call_args.args[0]['convergence_tolerance'], 1e-7)

    def test_invalid_base_tolerances_are_rejected(self):
        from components.nonlinear_time_history.building_exploratory import validate_convergence_settings
        for value in (True,None,0,1e-5,1e-8,'1e-6',float('nan')):
            with self.assertRaises(ValueError,msg=repr(value)):
                validate_convergence_settings({'convergence_tolerance':value})

    def test_thesis_intent_rejects_relaxed_recovery(self):
        from components.nonlinear_time_history.building_exploratory import validate_convergence_settings
        with self.assertRaisesRegex(ValueError, "THESIS_NLTHA"):
            validate_convergence_settings({
                "analysis_intent": "THESIS_NLTHA",
                "final_relaxed_tolerance": 1e-6})
        self.assertEqual(validate_convergence_settings({
            "analysis_intent": "THESIS_NLTHA"}), (1e-6, 40, None))


class FailureReportPrintSafety(unittest.TestCase):
    def test_recovery_logging_failure_does_not_abort_solver(self):
        from unittest.mock import patch
        solver = ToleranceSolver(needed=1e-6)
        diag = {"report_recovery": True, "convergence_tolerance": 1e-7,
                "final_relaxed_tolerance": 1e-6}
        with patch("builtins.print", side_effect=OSError(22, "Invalid argument")):
            accepted = _advance_nonlinear_interval(solver, .005, max_depth=0,
                                                   diagnostics=diag)
        self.assertEqual(accepted, 1)
        self.assertEqual(diag["relaxed_tolerance_steps"], 1)
        self.assertAlmostEqual(solver.clock, .005)


    def test_closed_stdout_must_not_mask_the_real_solver_error(self):
        from components.nonlinear_time_history import building_exploratory as be
        real_print=builtins.print
        def broken(*a,**k):raise OSError(22,'Invalid argument')
        with tempfile.TemporaryDirectory() as d:
            builtins.print=broken
            try:
                try:raise RuntimeError('Nonlinear step failed at t=2.38594s')
                except RuntimeError as exc:
                    target=be._write_failure_report(d,{},exc)
            finally:
                builtins.print=real_print
            report=json.loads(Path(target).read_text(encoding='utf-8'))
        self.assertEqual(report['error_type'],'RuntimeError')
        self.assertIn('2.38594',report['error'])


if __name__=='__main__':
    unittest.main()
