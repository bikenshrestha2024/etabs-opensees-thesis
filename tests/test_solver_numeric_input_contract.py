"""Fail-closed numerical input contracts for reusable gravity/transient helpers.

These tests do not import OpenSees or create an ETABS model. They assert that
invalid scalar controls are refused before any solver object is configured.
"""
from __future__ import annotations
import math
import unittest

from components.gravity.solver_stack import (
    configure_nonlinear_static,
    run_gravity_stage,
    run_static_analysis,
    run_transient_analysis,
)


class CallRecorder:
    def __init__(self):
        self.calls=[]

    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            if name == "analyze":
                return 0
            return None
        return call


class NumericalInputGateTests(unittest.TestCase):
    def test_bad_loads_and_tolerances_fail_before_solver_setup(self):
        for bad in (float("nan"), float("inf"), -float("inf"), 0.0, -3.0):
            with self.subTest(load=repr(bad)):
                ops=CallRecorder()
                with self.assertRaisesRegex(ValueError, "total_applied_vertical_load_kN"):
                    run_gravity_stage(ops, [1], bad)
                self.assertEqual(ops.calls, [])
        for bad in (float("nan"), float("inf"), -float("inf"), -0.1):
            with self.subTest(tolerance=repr(bad)):
                ops=CallRecorder()
                with self.assertRaisesRegex(ValueError, "equilibrium_tolerance_percent"):
                    run_gravity_stage(ops, [1], 100.0,
                                      equilibrium_tolerance_percent=bad)
                self.assertEqual(ops.calls, [])

    def test_nonintegral_step_counts_do_not_get_truncated(self):
        for bad in (2.9, 3.25, True, False, None, float("nan"),
                    float("inf"), "2.9", 0, -1):
            with self.subTest(value=repr(bad)):
                for run in (
                    lambda ops: configure_nonlinear_static(ops, nsteps=bad),
                    lambda ops: run_static_analysis(ops, bad),
                    lambda ops: run_transient_analysis(ops, bad, 0.01),
                    lambda ops: run_gravity_stage(ops, [1], 100.0, nsteps=bad),
                ):
                    ops=CallRecorder()
                    with self.assertRaisesRegex(ValueError, "positive integer"):
                        run(ops)
                    self.assertEqual(ops.calls, [])

    def test_invalid_transient_dt_fails_before_configuring_solver(self):
        for bad in (float("nan"), float("inf"), -float("inf"), 0.0, -0.1,
                    None, "not a time", True):
            with self.subTest(value=repr(bad)):
                ops=CallRecorder()
                with self.assertRaisesRegex(ValueError, "dt"):
                    run_transient_analysis(ops, 20, bad)
                self.assertEqual(ops.calls, [])

    def test_nonfinite_reaction_cannot_pass_equilibrium_or_freeze_gravity(self):
        class BadReaction(CallRecorder):
            def __getattr__(self, name):
                if name == "nodeReaction":
                    return lambda *args: float("nan")
                return super().__getattr__(name)
        ops=BadReaction()
        with self.assertRaisesRegex(RuntimeError, "Non-finite gravity support reaction"):
            run_gravity_stage(ops, [1], 100.0, nsteps=1)
        self.assertNotIn("loadConst", [name for name,_,_ in ops.calls])

    def test_nonfinite_displacement_cannot_freeze_gravity(self):
        class BadDisplacement(CallRecorder):
            def __getattr__(self, name):
                if name == "nodeReaction":
                    return lambda *args: 100.0
                if name == "nodeDisp":
                    return lambda *args: float("nan")
                return super().__getattr__(name)
        ops=BadDisplacement()
        with self.assertRaisesRegex(RuntimeError, "Non-finite gravity vertical displacement"):
            run_gravity_stage(ops, [1], 100.0, model_nodes=[1], nsteps=1)
        self.assertNotIn("loadConst", [name for name,_,_ in ops.calls])

    def test_exact_integer_compatibility_and_valid_transient(self):
        for count in (2, "2", 2.0):
            with self.subTest(value=repr(count)):
                ops=CallRecorder()
                self.assertEqual(run_transient_analysis(ops, count, 0.01), 0)
                self.assertEqual(
                    [args for name,args,kwargs in ops.calls if name=="analyze"],
                    [(2,0.01)]
                )
        self.assertEqual(
            [name for name,_,_ in ops.calls if name == "analysis"],
            ["Transient"]
        )


if __name__ == "__main__":
    unittest.main()
