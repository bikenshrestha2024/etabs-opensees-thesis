"""Contract tests for opt-in vector reaction queries; no native OpenSees needed."""
from __future__ import annotations

import unittest

from components.shared.response_recorders import (
    REACTION_COMPONENTS, append_base_shear, support_resultants
)


class FakeOps:
    def __init__(self, nodes):
        self.nodes = nodes
        self.reactions_calls = 0
        self.vector_calls = 0
        self.scalar_calls = 0

    def reactions(self):
        self.reactions_calls += 1

    def nodeReaction(self, node, dof=None):
        values = self.nodes[node]
        if dof is None:
            self.vector_calls += 1
            return values
        self.scalar_calls += 1
        return values[dof - 1]


class ReactionVectorTests(unittest.TestCase):
    def setUp(self):
        self.nodes = {
            101: (10, -8, 13, 1.2, -2.2, 4.5),
            102: (-3, 2, 8, 3.3, -5.1, 6.7),
        }

    def test_vector_and_scalar_outputs_match(self):
        baseline = FakeOps(self.nodes)
        fast = FakeOps(self.nodes)
        a = support_resultants(baseline, [101, 102])
        b = support_resultants(fast, [101, 102], vectorized=True)
        self.assertEqual(a, b)
        self.assertEqual(list(b), list(REACTION_COMPONENTS))
        self.assertEqual(b['support_reaction_Fx_kN'], 7)
        self.assertEqual(b['support_reaction_Mz_kNm'], 11.2)
        self.assertEqual(baseline.scalar_calls, 12)
        self.assertEqual(fast.vector_calls, 2)
        self.assertEqual(baseline.reactions_calls, 1)
        self.assertEqual(fast.reactions_calls, 1)

    def test_incremental_base_shear_preserves_signs(self):
        baseline = support_resultants(FakeOps(self.nodes), [101, 102])
        shifted = FakeOps({
            101: (12, -9, 13, 1.2, -2.2, 4.5),
            102: (-1, 4, 8, 3.3, -5.1, 6.7),
        })
        sample = append_base_shear({}, shifted, [101, 102], baseline,
                                   vectorized=True)
        self.assertEqual(sample['support_reaction_Fx_kN'], 4)
        self.assertEqual(sample['base_shear_X_kN'], -4)
        self.assertEqual(sample['support_reaction_Fy_kN'], 1)
        self.assertEqual(sample['base_shear_Y_kN'], -1)

    def test_insufficient_dofs_must_fail_explicitly(self):
        short = FakeOps({101: (1, 2, 3)})
        with self.assertRaisesRegex(ValueError, 'six'):
            support_resultants(short, [101], vectorized=True)

    def test_empty_supports_must_fail(self):
        with self.assertRaises(ValueError):
            support_resultants(FakeOps(self.nodes), [], vectorized=True)


if __name__ == '__main__':
    unittest.main()
