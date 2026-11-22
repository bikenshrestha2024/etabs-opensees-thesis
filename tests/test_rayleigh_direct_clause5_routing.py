"""Fail on Rayleigh/ESM adapters that bypass canonical NBC 105 Clause 5.

Pure contract test: no ETABS COM, OpenSees or private EDB needed.
[REF components/nbc105/clause_05_dynamic_characteristics.py §5.1-5.2]
"""
from __future__ import annotations

import ast
import math
import unittest
from pathlib import Path

from components.nbc105.clause_05_dynamic_characteristics import (
    adopted_period_s, amplified_period_s, empirical_period_s,
    rayleigh_period_s, seismic_weight_kN,
)
from components.nbc105.constants import GRAVITY_M_S2
from components.modal.rayleigh_ledger_audit import verify_rayleigh_sum
from components.equivalent_static.calculation_and_gui import resolve_esm_state_periods


ROOT=Path(__file__).resolve().parents[1]


def _function_calls(path, function_name):
    tree=ast.parse((ROOT/path).read_text(encoding="utf8"))
    name=next(node for node in tree.body
              if isinstance(node,ast.FunctionDef) and node.name==function_name)
    return {node.func.id for node in ast.walk(name)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name)}


class RayleighClause5Contract(unittest.TestCase):
    def test_preliminary_rayleigh_uses_all_canonical_clause5_rules(self):
        calls=_function_calls("components/modal/rayleigh.py","run")
        for expected in ("rayleigh_period_s","seismic_weight_kN",
                         "adopted_period_s","require_source_state"):
            with self.subTest(expected=expected):
                self.assertIn(expected,calls)

    def test_saved_ledger_recomputes_via_canonical_rayleigh_function(self):
        calls=_function_calls("components/modal/rayleigh_ledger_audit.py",
                              "verify_rayleigh_sum")
        self.assertIn("rayleigh_period_s",calls)

    def test_esm_cross_state_periods_call_shared_lesser_of(self):
        calls=_function_calls("components/equivalent_static/calculation_and_gui.py",
                              "resolve_esm_state_periods")
        self.assertIn("adopted_period_s",calls)

    def test_nbc_95m_wall_areas_and_clause_5_period_math(self):
        H=95.
        wx=2.073174515235457
        wy=2.203080332409972
        x=amplified_period_s(empirical_period_s(H,"concrete shear-wall",wx))
        y=amplified_period_s(empirical_period_s(H,"concrete shear-wall",wy))
        self.assertAlmostEqual(x,1.981280885026091,places=9)
        self.assertAlmostEqual(y,1.921979776706312,places=9)
        self.assertAlmostEqual(adopted_period_s(x/1.25,1.977548)["adopted_s"],
                               1.977548,places=6)
        self.assertAlmostEqual(adopted_period_s(y/1.25,2.703236)["adopted_s"],
                               y,places=9)
        self.assertAlmostEqual(seismic_weight_kN(100.,10.,20.,90.),112.)

    def test_canonical_rayleigh_matches_saved_ledger_reconstruction(self):
        rows=[{"weight_kN":100., "force_kN":30., "displacement_m":.005},
              {"weight_kN":200., "force_kN":70., "displacement_m":.010}]
        ref=rayleigh_period_s([100,200],[.005,.010],[30,70])
        audit=verify_rayleigh_sum(rows)
        self.assertAlmostEqual(audit["period_s"],ref,places=13)
        self.assertAlmostEqual(ref,2*math.pi*math.sqrt(
            (100*.005**2+200*.010**2)/
            (GRAVITY_M_S2*(30*.005+70*.010))),places=13)


if __name__=="__main__":
    unittest.main()
