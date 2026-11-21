"""Parity of production copies with the clause 1 module.

[REF NBC105-2025 §1, printed pp. 1-9] Reference: ``components.nbc105.
clause_01_scope_definitions`` (transcribed from the printed pages). Production
code is called with its real signature. A mismatch is a finding, not a
tolerance to widen. Unit tests only; no native ETABS/OpenSees.
"""
import itertools
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "etabs_period_review"))

from components.nbc105 import clause_01_scope_definitions as c1
from components.nbc105 import constants

import reconcile  # noqa: E402


class GravityParity(unittest.TestCase):
    def test_single_g_equals_printed_notation(self):
        self.assertEqual(constants.GRAVITY_M_S2, c1.printed_gravity_m_s2())
        self.assertEqual(constants.NBC_NOTATION_GRAVITY_M_S2, c1.notation("g").printed_value)

    def test_reconcile_uses_printed_g(self):
        self.assertEqual(reconcile.G, c1.printed_gravity_m_s2())

    def test_rayleigh_and_assembly_route_through_constant(self):
        # Weight-to-mass sites must import the single constant, not carry a literal g.
        for rel in ("components/model/assembly.py", "components/modal/rayleigh.py"):
            text = (ROOT / rel).read_text(encoding="utf-8-sig")
            self.assertIn("GRAVITY_M_S2", text, rel)
            self.assertIsNone(re.search(r"\b9\.80665\b|\b9806\.65\b", text), rel)


class SoftStoryParity(unittest.TestCase):
    """components.validation.response_checks.irregularity implements 5.4.1.2 with 0.7 / 0.8."""

    @classmethod
    def setUpClass(cls):
        from components.validation import response_checks
        cls.rc = response_checks

    def _production_soft(self, k, ku, three):
        rows = [{"story_number": 1, "story_stiffness_kN_per_m": k},
                {"story_number": 2, "story_stiffness_kN_per_m": ku}]
        rows += [{"story_number": 3 + i, "story_stiffness_kN_per_m": v} for i, v in enumerate(three[1:])]
        # rows[1:4] must be (ku, three[1], three[2]) so the three stories above are ku, a, b
        out = self.rc.irregularity({"diaphragms": [], "nodes": {}, "base_z_m": 0.0}, story_rows=rows)
        checks = [c for c in out["checks"] if c["storey"] == 1 and c["check"].startswith("Soft story")]
        return any(c["status"] == "IRREGULAR" for c in checks), {c["check"] for c in checks}

    def test_grid_matches_clause_definition(self):
        ks = (60.0, 69.999999, 70.0, 70.000001, 79.0, 80.0, 87.0, 88.0, 88.000001, 95.0, 120.0)
        kus = (100.0,)
        pairs = ((100.0, 100.0), (110.0, 120.0), (90.0, 80.0))
        n = 0
        for k, ku, (a, b) in itertools.product(ks, kus, pairs):
            prod, kinds = self._production_soft(k, ku, (ku, a, b))
            self.assertEqual(kinds, {"Soft story adjacent above", "Soft story three above"})
            ref = c1.is_soft_story(k, ku, three_above=(ku, a, b))
            self.assertEqual(prod, ref, (k, ku, a, b))
            n += 1
        self.assertEqual(n, 33)

    def test_production_thresholds_equal_clause_constants(self):
        text = (ROOT / "components/validation/response_checks.py").read_text(encoding="utf-8-sig")
        self.assertIn("k<.7*ku", text)
        self.assertIn("k<.8*sum(vals)/3", text)
        self.assertEqual((c1.SOFT_STORY_ADJACENT_RATIO, c1.SOFT_STORY_THREE_ABOVE_RATIO), (0.7, 0.8))


class DefinitionThresholdProductionAbsence(unittest.TestCase):
    """No production copy exists for these definition thresholds (audit result)."""

    def test_no_production_flexible_diaphragm_or_dual_share_check(self):
        pat = re.compile(r"flexible[ _]diaphragm|dual[ _]share|frame[ _]share", re.I)
        hits = []
        for base in ("components", "tools"):
            for path in (ROOT / base).rglob("*.py"):
                if "nbc105" in path.parts:
                    continue
                if pat.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
                    hits.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
