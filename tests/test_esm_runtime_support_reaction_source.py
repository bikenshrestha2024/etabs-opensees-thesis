"""ESM reaction nodes must come from the assembled solver, not source restraints.

Synthetic, no ETABS or OpenSees execution.
[REF docs/source/components/equivalent_static/calculation_and_gui.py.md]
"""
import inspect
import unittest
from components.equivalent_static.calculation_and_gui import write_outputs
from components.model.support_case_contract import solver_reaction_support_tags
from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32


class ESMRuntimeReactionSupportTests(unittest.TestCase):
    def test_esm_generated_runner_uses_actual_solver_supports(self):
        generated_source=inspect.getsource(write_outputs)
        self.assertIn("solver_reaction_support_tags(",generated_source)
        self.assertNotIn("MODEL_DATA['supports'].items()",generated_source)
        self.assertIn("SUPPORT_CASE_VERIFICATION",generated_source)

    def test_actual_32_is_not_exported_76(self):
        foundation=sorted(int(x) for x in PROJECT_PRIMARY_32)
        self.assertEqual(len(foundation),32)
        extra=[i for i in range(10001,10045)]
        report={"gravity_base_support_tags":foundation,
                "support_case_evidence":{"profile":"PHYSICAL_32"}}
        selection=solver_reaction_support_tags(report,"PHYSICAL_32")
        self.assertEqual(selection,foundation)
        self.assertEqual(len(selection),32)
        self.assertEqual(len(foundation+extra),76)

    def test_missing_runtime_supports_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"Actual solver support"):
            solver_reaction_support_tags(
                {"support_case_evidence":{"profile":"PHYSICAL_32"}},
                "PHYSICAL_32")


if __name__=="__main__":
    unittest.main()
