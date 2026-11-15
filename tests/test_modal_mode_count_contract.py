"""Exact modal-count input checks without native OpenSees or SciPy.

The real helper and call sites are parsed from source; only the helper is
executed to keep this CI regression independent of optional native packages.
"""
import ast
import math
import numbers
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


def load_mode_validator():
    source=ROOT/"components/shared/eigen_solver.py"
    parsed=ast.parse(source.read_text(encoding="utf-8"))
    node=next(n for n in parsed.body
              if isinstance(n,ast.FunctionDef) and n.name=="validated_mode_count")
    module=ast.Module(body=[node],type_ignores=[])
    namespace={"math":math,"numbers":numbers}
    exec(compile(module,str(source),"exec"),namespace)
    return namespace["validated_mode_count"]


class ExactModalCountContractTests(unittest.TestCase):
    def test_fractional_invalid_nonfinite_and_boolean_requests_rejected(self):
        check=load_mode_validator()
        for value in (1.5,2.9,"2.9",True,False,0,-1,0.0,
                      float("nan"),float("inf"),-float("inf"),None):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError,"positive exact integer"):
                    check(value)

    def test_integer_compatible_values_preserved_exactly(self):
        check=load_mode_validator()
        for value,expected in ((1,1),(40,40),("40",40),(2.0,2),
                               (9007199254740993,9007199254740993)):
            with self.subTest(value=repr(value)):
                self.assertEqual(check(value),expected)
        self.assertEqual(check(3,name="fundamental_mode_X"),3)

    def test_modal_and_mrsm_callers_cannot_truncate_count_before_validator(self):
        modal=(ROOT/"components/modal/analysis.py").read_text(encoding="utf-8")
        mrsm=(ROOT/"components/response_spectrum/model_analysis.py").read_text(encoding="utf-8")
        eig=(ROOT/"components/shared/eigen_solver.py").read_text(encoding="utf-8")
        self.assertIn('nmodes = validated_mode_count(nmodes, name="nmodes")',modal)
        self.assertIn('validated_mode_count(selected, name=f"fundamental_mode_{axis}")',modal)
        self.assertIn("requested_modes = validated_mode_count(config.get('nmodes',40), name='nmodes')",mrsm)
        self.assertIn("nmodes=requested_modes",mrsm)
        self.assertIn("modes=validated_mode_count(modes)",eig)
        self.assertNotIn("nmodes=int(config.get('nmodes',40))",mrsm)


if __name__=="__main__":
    unittest.main()
