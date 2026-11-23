"""Regression: MRSM and NLTHA reactions use actual builder support tags.

No ETABS EDB, solver process, project output or numerical response is needed.
[REF docs/source/components/model/support_case_contract.py.md]
"""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32
import components.model.support_case_contract as shared
from components.nonlinear_time_history.source_model_handoff import (
    solver_reaction_support_tags as nltha_reaction_tags,
)
import components.response_spectrum.model_analysis as mrsm


def report(case, tags):
    return {
        "gravity_base_support_tags": list(tags),
        "support_case_evidence": {"profile": case},
    }


class SolverSupportRecoveryTests(unittest.TestCase):
    def test_shared_owner_returns_only_physical32_even_with_source_76(self):
        self.assertTrue(hasattr(shared, "solver_reaction_support_tags"),
                        "The source support profile has no shared runtime reaction selector")
        raw_export = {str(n): [1, 1, 1, 1, 1, 1] for n in range(1, 77)}
        self.assertEqual(len(raw_export), 76)
        actual=sorted(PROJECT_PRIMARY_32)
        chosen=shared.solver_reaction_support_tags(
            report("PHYSICAL_32", reversed(actual)), "PHYSICAL_32")
        self.assertEqual(chosen, actual)
        self.assertEqual(len(chosen), 32)
        self.assertEqual(len(raw_export), 76)

    def test_76_and_97_diagnostic_recorder_profiles(self):
        self.assertTrue(hasattr(shared, "solver_reaction_support_tags"))
        for case, count in (("SOURCE_76", 76), ("WALL_BASE_97", 97)):
            with self.subTest(case=case):
                actual = list(range(1001, 1001 + count))
                self.assertEqual(shared.solver_reaction_support_tags(
                    report(case, reversed(actual)), case), actual)

    def test_duplicate_boolean_and_invalid_runtime_tags_fail_closed(self):
        self.assertTrue(hasattr(shared, "solver_reaction_support_tags"))
        tags=list(PROJECT_PRIMARY_32)
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            shared.solver_reaction_support_tags(
                report("PHYSICAL_32", tags+[tags[0]]), "PHYSICAL_32")
        with self.assertRaisesRegex(ValueError,"Boolean"):
            shared.solver_reaction_support_tags(
                report("PHYSICAL_32", tags[:-1]+[True]), "PHYSICAL_32")
        with self.assertRaisesRegex(ValueError,"invalid|Invalid"):
            shared.solver_reaction_support_tags(
                report("PHYSICAL_32", tags[:-1]+["invalid"]), "PHYSICAL_32")
        with self.assertRaisesRegex(ValueError,"PHYSICAL_32"):
            shared.solver_reaction_support_tags(
                report("SOURCE_76", list(range(1,77))), "PHYSICAL_32")

    def test_nltha_public_import_remains_compatible(self):
        report32=report("PHYSICAL_32", PROJECT_PRIMARY_32)
        self.assertEqual(nltha_reaction_tags(report32), sorted(PROJECT_PRIMARY_32))

    def test_mrsm_reaction_export_uses_verified_built_tags_not_source_map(self):
        path=Path(mrsm.__file__)
        code=ast.parse(path.read_text(encoding="utf-8"))
        fn=next(item for item in code.body if isinstance(item,ast.FunctionDef)
                and item.name=="run_model_spectrum")
        selections=[
            item.value for item in ast.walk(fn)
            if isinstance(item,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=="support_tags"
                    for t in item.targets)
        ]
        self.assertEqual(len(selections),1,"Exactly one actual-solver reaction support tag source")
        selection=selections[0]
        self.assertIsInstance(selection,ast.Call)
        self.assertIsInstance(selection.func,ast.Name)
        self.assertEqual(selection.func.id,"solver_reaction_support_tags")
        self.assertEqual([arg.id if isinstance(arg,ast.Name) else ""
                          for arg in selection.args],["built","selected_support"])


if __name__=="__main__":
    unittest.main()
