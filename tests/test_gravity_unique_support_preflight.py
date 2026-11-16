"""Fail-closed reaction-node selection: engineering integrity guard, no solver."""
import unittest
from unittest.mock import Mock
from components.gravity.solver_stack import _validated_support_tags, run_gravity_stage


class SupportIdentityTests(unittest.TestCase):
    def test_correct_32_supports_pass_without_reordering(self):
        nodes=list(range(32,0,-1))
        self.assertEqual(_validated_support_tags(nodes),nodes)

    def test_string_tags_supported_only_when_exact(self):
        self.assertEqual(_validated_support_tags(["3","04"]),[3,4])

    def test_duplicates_rejected_before_solver_runs(self):
        for tags in ([1,2,1], ["1",1], [1,"01"], [31]*32):
            with self.subTest(tags=tags):
                mock_ops=Mock()
                with self.assertRaisesRegex(ValueError,"Duplicate support"):
                    run_gravity_stage(mock_ops,tags,300.)
                mock_ops.assert_not_called()
                self.assertFalse(mock_ops.analyze.called)
                self.assertFalse(mock_ops.reactions.called)

    def test_invalid_tags_rejected(self):
        for tags in ([],[0],[-1],[1.5],[float("nan")],
                     [float("inf")], [True],["1.0"],["1e2"],"123",None):
            with self.subTest(tags=tags):
                with self.assertRaises(ValueError):
                    _validated_support_tags(tags)

    def test_bad_applied_load_still_blocks_solver(self):
        ops=Mock()
        with self.assertRaisesRegex(ValueError,"finite"):
            run_gravity_stage(ops,[1,2],float("nan"))
        self.assertFalse(ops.analyze.called)


if __name__=="__main__":
    unittest.main(verbosity=2)
