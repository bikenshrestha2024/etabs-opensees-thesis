"""NBC 105:2025 shared constants and clause 5 shim. [REF NBC105-2025 notation list, printed p. 7]

Unit tests only; no ETABS/OpenSees/tkinter.
"""
import ast
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from components.nbc105 import clause_05_dynamic_characteristics as new  # noqa: E402
from components.nbc105 import constants  # noqa: E402
from components.modal import nbc105_clause5 as shim  # noqa: E402

# Files that convert between weight and mass with g (same physical conversion).
# Acc(g) record conversions are a different conversion and are not scanned.
GRAVITY_FILES = [
    "components/modal/rayleigh.py",
    "components/modal/rayleigh_ledger_audit.py",
    "components/modal/rayleigh_mass_audit.py",
    "components/model/assembly.py",
    "components/sections/area_elements.py",
    "components/gravity/load_path_formulas.py",
    "components/validation/irregularity_review.py",
    "components/nbc105/clause_05_dynamic_characteristics.py",
    "components/modal/nbc105_clause5.py",
]
LITERAL = re.compile(r"(?<![\d.])9\.81(?!\d)|(?<![\d.])9\.80665(?!\d)")


class ConstantValues(unittest.TestCase):
    def test_values(self):
        self.assertEqual(constants.GRAVITY_M_S2, 9.81)
        self.assertEqual(constants.NBC_NOTATION_GRAVITY_M_S2, 9.81)
        self.assertEqual(constants.GRAVITY_M_S2, constants.NBC_NOTATION_GRAVITY_M_S2)
        self.assertEqual(constants.PRINTED_PAGE_OFFSET, 21)

    def test_superseded_value_is_history_only(self):
        # (9.81 - 9.80665) / 9.81 = 0.00335 / 9.81 = 3.4149e-4 = 0.0341 %
        self.assertEqual(constants.SUPERSEDED_GRAVITY_M_S2, 9.80665)
        diff = (1 - constants.SUPERSEDED_GRAVITY_M_S2 / constants.GRAVITY_M_S2) * 100
        self.assertAlmostEqual(diff, 0.0341, places=4)
        # mass = W / g: 9.81 -> mass is 0.0341 % lower than with 9.80665 reversed
        # (ratio 9.80665 / 9.81 = 0.999659)
        self.assertAlmostEqual(9.80665 / 9.81, 0.999659, places=6)

    def test_rayleigh_default_g_is_shared_constant(self):
        # Single DOF: W = 100 kN, F = 10 kN, d = 0.05 m -> T = 2 pi sqrt(W d^2 / (g F d))
        t = new.rayleigh_period_s([100.0], [0.05], [10.0])
        import math
        self.assertAlmostEqual(t, 2 * math.pi * math.sqrt(100.0 * 0.05 / (constants.GRAVITY_M_S2 * 10.0)), places=12)


class GravityLiteralScan(unittest.TestCase):
    def test_gravity_literals_only_in_constants(self):
        # Numeric literals found by AST (docstrings and comments may still cite 9.81).
        offenders = []
        for rel in GRAVITY_FILES:
            tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, float) \
                        and node.value in (9.81, 9.80665):
                    offenders.append((rel, node.lineno))
                if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                        and LITERAL.search(node.value) and len(node.value) < 200 and node.value.startswith("="):
                    offenders.append((rel, node.lineno))  # Excel formula text
        self.assertEqual(offenders, [])

    def test_constants_file_is_the_only_definition(self):
        text = (ROOT / "components/nbc105/constants.py").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^GRAVITY_M_S2: float = 9\.81\b", text, re.M)), 1)


class SupersededLiteralScan(unittest.TestCase):
    """No 9.80665 (or its mm-s form 9806.65) is left in code under components/ or tools/."""

    def test_no_superseded_gravity_literal(self):
        offenders = []
        for base in ("components", "tools"):
            for path in (ROOT / base).rglob("*.py"):
                if path == ROOT / "components/nbc105/constants.py":
                    continue
                text = path.read_text(encoding="utf-8")
                if re.search(r"9\.80665|9806\.65", text):
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(offenders, [])

    def test_standalone_tools_copy_matches_constant(self):
        # Single-file tools cannot import components; their literal must equal the constant.
        pattern = re.compile(r"^(?:GRAVITY|G)\s*=\s*([0-9.]+)", re.M)
        for rel in ("tools/verification_studio/ETABS_OpenSees_Verification_Studio.py",
                    "tools/verification_studio/ETABS_OpenSees_Verification_Studio_ALL_IN_ONE.py",
                    "tools/verification_studio/expanded_benchmarks.py"):
            values = {float(v) for v in pattern.findall((ROOT / rel).read_text(encoding="utf-8"))}
            self.assertEqual(values, {constants.GRAVITY_M_S2}, rel)

    def test_reconcile_uses_shared_constant(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("reconcile_g", ROOT / "tools/etabs_period_review/reconcile.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.G, constants.GRAVITY_M_S2)


class ShimIdentity(unittest.TestCase):
    def test_same_all(self):
        self.assertEqual(list(shim.__all__), list(new.__all__))

    def test_every_public_name_is_the_same_object(self):
        public = [n for n in dir(new) if not n.startswith("_")
                  and (callable(getattr(new, n)) or n.isupper()) and n in new.__all__]
        self.assertIn("storey_index_for_elevation", public)
        self.assertIn("KT_BY_SYSTEM", public)
        for name in new.__all__:
            self.assertIs(getattr(shim, name), getattr(new, name), name)

    def test_all_covers_every_public_function_and_constant(self):
        import types
        found = {n for n, v in vars(new).items()
                 if not n.startswith("_") and (isinstance(v, types.FunctionType) and v.__module__ == new.__name__
                                               or (n.isupper() and n != "GRAVITY_M_S2"))}
        self.assertEqual(found, set(new.__all__))


if __name__ == "__main__":
    unittest.main()
