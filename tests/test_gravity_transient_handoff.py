"""No-native-solver contract tests for NBC gravity freeze helper."""
import unittest
from components.shared.gravity_transient_handoff import freeze_verified_gravity


class FakeOps:
    def __init__(self, nodes=(1, 2), before=1.0, reset=True):
        self.nodes = nodes
        self.time = before
        self.reset = reset
        self.calls = []

    def getNodeTags(self):
        return self.nodes

    def getTime(self):
        return self.time

    def loadConst(self, *args):
        self.calls.append(("loadConst", args))
        if self.reset:
            self.time = 0.0


class GravityTransientHandoffTests(unittest.TestCase):
    def test_existing_equilibrium_is_frozen_without_wiping_domain(self):
        ops = FakeOps()
        out = freeze_verified_gravity(
            ops, case="ULS_KOBE_XY", builder_gravity_converged=True
        )
        self.assertEqual(ops.calls, [("loadConst", ("-time", 0.0))])
        self.assertEqual(out["initial_state"], "GRAVITY_EQUILIBRIUM_FROZEN")
        self.assertEqual(out["static_seismic_el_carried_over"], "NOT_INDEPENDENTLY_CHECKED")

    def test_unverified_gravity_fails_closed(self):
        ops = FakeOps()
        with self.assertRaisesRegex(RuntimeError, "gravity not independently"):
            freeze_verified_gravity(
                ops, case="ULS_KOBE_XY", builder_gravity_converged=False
            )
        self.assertEqual(ops.calls, [])

    def test_empty_model_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "empty"):
            freeze_verified_gravity(
                FakeOps(nodes=()), case="ULS_KOBE_XY",
                builder_gravity_converged=True
            )

    def test_no_time_reset_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "did not reset"):
            freeze_verified_gravity(
                FakeOps(reset=False), case="ULS_KOBE_XY",
                builder_gravity_converged=True
            )


if __name__ == "__main__":
    unittest.main()
