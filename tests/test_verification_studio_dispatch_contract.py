"""Verify both standalone benchmark launchers keep B01–B04 and B05–B12 dispatch.

[REF docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md]
Self-test exercises program registry and closed-form formulas only.
It does NOT assert ETABS or OpenSees native numerical equivalence.
"""
import ast
import subprocess
import sys
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
PROGRAMS=(
    REPO/"tools/verification_studio/ETABS_OpenSees_Verification_Studio.py",
    REPO/"tools/verification_studio/ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py",
)


class BenchmarkDispatchContractTests(unittest.TestCase):
    def test_no_shadowed_benchmark_dispatch_definitions(self):
        for path in PROGRAMS:
            with self.subTest(program=path.name):
                tree=ast.parse(path.read_text(encoding="utf-8-sig"))
                symbols=[node.name for node in tree.body
                         if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))]
                self.assertEqual(symbols.count("_run_case"),1)
                self.assertEqual(symbols.count("_run_legacy_case"),1)
                self.assertNotIn("_run_legacy_case = _run_case",
                                 path.read_text(encoding="utf-8-sig"))

    def test_both_benchmark_programs_still_pass_their_internal_self_test(self):
        for path in PROGRAMS:
            with self.subTest(program=path.name):
                completed=subprocess.run(
                    [sys.executable,str(path),"--self-test"],
                    cwd=str(REPO),capture_output=True,text=True,timeout=30)
                self.assertEqual(completed.returncode,0,
                    completed.stdout+"\n"+completed.stderr)
                self.assertIn("SELF-TEST PASS",completed.stdout)


if __name__=="__main__":
    unittest.main()
