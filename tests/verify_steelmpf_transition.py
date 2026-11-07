import unittest

from components.nonlinear_time_history.research_building_materials import (
    _steelmpf_transition,
)


class SteelMPFTransitionTests(unittest.TestCase):
    def test_documented_transition_retains_peer_cR2(self):
        transition = _steelmpf_transition("OPENSEES_DOCUMENTED")
        self.assertEqual(transition["R0"], 20.0)
        self.assertEqual(transition["cR1"], 0.925)
        self.assertEqual(transition["cR2"], 0.0015)
        self.assertIn("author-documented", transition["basis"])

    def test_peer_appendix_transition_is_available_exactly(self):
        transition = _steelmpf_transition("PEER_APPENDIX_EXACT")
        self.assertEqual(transition["R0"], 20.0)
        # 2026-11-07: printed a1=18.5 is the absolute Menegotto-Pinto term;
        # OpenSees uses R=R0*(1-cR1*xi/(cR2+xi)), so cR1=a1/R0. 18.5 gave NaN.
        self.assertAlmostEqual(transition["cR1"], 18.5 / 20.0)
        self.assertEqual(transition["cR2"], 0.0015)
        self.assertIn("printed a1=18.5 converted", transition["basis"])

    def test_unconverted_a1_is_nonfinite_in_opensees(self):
        try:
            import openseespy.opensees as ops
        except Exception:
            self.skipTest("OpenSeesPy not installed: native check NOT run")
        import math
        def first_bad(cr1):
            ops.wipe()
            ops.uniaxialMaterial("SteelMPF", 1, 402724.8, 402724.8, 199947961.5, .02, .02, 20., cr1, .0015, 0., 1., 0., 1.)
            path = ([1e-5 * i for i in range(1, 101)] + [1e-3 - 1e-5 * i for i in range(1, 201)]
                    + [-1e-3 + 1e-5 * i for i in range(1, 201)])  # two reversals
            for e in path:
                ops.testUniaxialMaterial(1)  # same sequence as the 2026-11-07 native probe
                ops.setStrain(e)
                if not math.isfinite(ops.getStress()):
                    return e
            return None
        self.assertIsNone(first_bad(0.925))
        self.assertIsNotNone(first_bad(18.5))

    def test_unknown_transition_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError, "Unknown SteelMPF transition"):
            _steelmpf_transition("UNRECOGNIZED")


if __name__ == "__main__":
    unittest.main()
