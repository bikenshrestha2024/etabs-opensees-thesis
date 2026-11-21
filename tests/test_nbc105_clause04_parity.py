"""Parity of every existing clause 4 implementation with the clause module.

[REF NBC105-2025 §4.1-§4.3, printed pp. 22-27] The reference is
``components.nbc105.clause_04_seismic_hazard`` (transcribed from the printed
pages). Each existing implementation is called with its own real signature.
A mismatch here is a finding, not a tolerance to widen. Unit tests only; no
native ETABS/OpenSees; not an engineering acceptance statement.
"""
import importlib
import math
import re
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

from components.nbc105 import clause_04_seismic_hazard as c4
from components.equivalent_static import code_basis, legacy_code_basis
from components.response_spectrum import nbc105_dual_target as dual

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "etabs_period_review"))
import reconcile  # noqa: E402

ESM, DYN = "equivalent_static", "dynamic"
SOILS = "ABCD"
BASE_GRID = (0.0, 0.05, 0.1, 0.25, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0)


def _grid():
    values = set(BASE_GRID)
    for p in c4.TABLE_4_1.values():
        for key in ("Ta", "Tc", "Td"):
            for d in (-1e-9, 0.0, 1e-9):
                values.add(p[key] + d)
    return sorted(v for v in values if 0.0 <= v <= 6.0)


GRID = _grid()


def _load_site_spectrum_module():
    """Import the tkinter-based module with an inert tkinter stand-in."""
    fake_tk = types.ModuleType("tkinter")
    for name in ("filedialog", "messagebox", "ttk"):
        setattr(fake_tk, name, types.ModuleType("tkinter." + name))
    stubs = {"tkinter": fake_tk, "tkinter.filedialog": fake_tk.filedialog,
             "tkinter.messagebox": fake_tk.messagebox, "tkinter.ttk": fake_tk.ttk}
    name = "components.response_spectrum.site_spectrum_and_scaling"
    sys.modules.pop(name, None)
    with mock.patch.dict(sys.modules, stubs):
        module = importlib.import_module(name)
    sys.modules.pop(name, None)
    return module


SITE = _load_site_spectrum_module()


class ShapeFactorParity(unittest.TestCase):
    def test_grid_contains_every_corner(self):
        for corner in (0.0, 0.1, 0.5, 0.7, 1.0, 2.0, 4.0, 5.0, 6.0):
            self.assertIn(corner, GRID)
        self.assertGreater(len(GRID), 25)

    def test_esm_code_basis_and_legacy(self):
        for fn in (code_basis.esm_spectral_shape_factor,
                   legacy_code_basis.esm_spectral_shape_factor):
            for soil in SOILS:
                for t in GRID:
                    self.assertAlmostEqual(
                        fn(t, soil), c4.spectral_shape_factor(t, soil, method=ESM),
                        places=12, msg=(fn.__module__, soil, t))

    def test_esm_ch_at_zero_is_alpha_for_all_soils(self):
        for soil in SOILS:
            self.assertEqual(code_basis.esm_spectral_shape_factor(0.0, soil),
                             c4.TABLE_4_1[soil]["alpha"])

    def test_esm_period_above_six_seconds_rejected(self):
        # Eq. 4.1(2) is printed for T <= 6 s (p. 23); no extrapolation.
        for fn in (code_basis.esm_spectral_shape_factor,
                   legacy_code_basis.esm_spectral_shape_factor):
            for t in (6.0 + 1e-9, 6.5, 10.0, 100.0):
                with self.assertRaises(ValueError, msg=(fn.__module__, t)):
                    fn(t, "C")
                with self.assertRaises(ValueError):
                    c4.spectral_shape_factor(t, "C", method=ESM)
            self.assertAlmostEqual(fn(6.0, "C"),
                                   c4.spectral_shape_factor(6.0, "C", method=ESM))

    def test_esm_negative_and_nan_period_rejected(self):
        for fn in (code_basis.esm_spectral_shape_factor,
                   legacy_code_basis.esm_spectral_shape_factor):
            for t in (-1e-9, -1.0, float("nan"), float("inf")):
                with self.assertRaises(ValueError, msg=(fn.__module__, t)):
                    fn(t, "B")

    def test_esm_unknown_soil_rejected(self):
        for fn in (code_basis.esm_spectral_shape_factor,
                   legacy_code_basis.esm_spectral_shape_factor):
            with self.assertRaises(ValueError):
                fn(1.0, "E")

    def test_site_spectrum_both_methods(self):
        for method, variant in (("esm", ESM), ("dynamic", DYN)):
            for soil in SOILS:
                for t in GRID:
                    self.assertAlmostEqual(
                        SITE.spectral_shape_ch(t, soil, method),
                        c4.spectral_shape_factor(t, soil, method=variant),
                        places=12, msg=(method, soil, t))

    def test_site_spectrum_rejections(self):
        for t in (-1e-9, 6.0 + 1e-9, float("nan"), float("inf")):
            for method in ("esm", "dynamic"):
                with self.assertRaises(ValueError, msg=(t, method)):
                    SITE.spectral_shape_ch(t, "C", method)
        with self.assertRaises(ValueError):
            SITE.spectral_shape_ch(1.0, "C", "static")

    def test_site_spectrum_table_matches_table_4_1(self):
        self.assertEqual(SITE.NBC105_SOIL_PARAMETERS, c4.TABLE_4_1)
        for soil, p in c4.TABLE_4_1.items():
            esm = code_basis.NBC105_ESM_SOIL_PARAMETERS[soil]
            self.assertEqual(esm, legacy_code_basis.NBC105_ESM_SOIL_PARAMETERS[soil])
            self.assertEqual((esm["Ta_s"], esm["Tc_s"], esm["Td_s"], esm["alpha"]),
                             (0.0, p["Tc"], p["Td"], p["alpha"]))

    def test_modal_nltha_soil_c_and_d(self):
        for soil in "CD":
            for t in GRID:
                self.assertAlmostEqual(
                    dual.ch_modal_nltha(t, soil),
                    c4.spectral_shape_factor(t, soil, method=DYN),
                    places=12, msg=(soil, t))

    def test_modal_nltha_scope_and_rejections(self):
        # Scope: only soils C and D are served; A and B are refused, not guessed.
        for soil in "AB":
            with self.assertRaises(ValueError):
                dual.ch_modal_nltha(1.0, soil)
        for t in (-1e-9, 6.0 + 1e-9, float("nan"), float("inf")):
            with self.assertRaises(ValueError, msg=t):
                dual.ch_modal_nltha(t, "C")
        self.assertEqual(dual.SOIL["C"], c4.TABLE_4_1["C"])
        self.assertEqual(dual.SOIL["D"], c4.TABLE_4_1["D"])

    def test_reconcile_soil_c_helpers(self):
        for t in GRID:
            self.assertAlmostEqual(reconcile.soil_c_modal_ch(t),
                                   c4.spectral_shape_factor(t, "C", method=DYN),
                                   places=12, msg=t)
            if t > 0:
                self.assertAlmostEqual(reconcile.soil_c_static_ch(t),
                                       c4.spectral_shape_factor(t, "C", method=ESM),
                                       places=12, msg=t)
        for t in (-1e-9, 6.0 + 1e-9, float("nan")):
            with self.assertRaises(ValueError, msg=t):
                reconcile.soil_c_modal_ch(t)
            with self.assertRaises(ValueError, msg=t):
                reconcile.soil_c_static_ch(t)


class SpectrumAssemblyParity(unittest.TestCase):
    Z, I = 0.35, 1.25

    def test_elastic_site_spectrum_g(self):
        periods = [0.0, 0.3, 1.0, 2.5, 6.0]
        for soil in SOILS:
            for method, variant in (("esm", ESM), ("dynamic", DYN)):
                got = SITE.elastic_site_spectrum_g(periods, soil, self.Z, self.I, method)
                want = [c4.elastic_site_spectrum(t, soil, self.Z, self.I, method=variant)
                        for t in periods]
                np.testing.assert_allclose(got, want, rtol=0, atol=1e-12)

    def test_target_nltha_g_is_c_over_omega_u(self):
        for soil in "CD":
            for t in (0.0, 0.5, 1.5, 3.0, 6.0):
                want = c4.elastic_site_spectrum(t, soil, self.Z, self.I, method=DYN) / 1.4
                self.assertAlmostEqual(
                    dual.target_nltha_g(t, soil, zoning_Z=self.Z, importance_I=self.I),
                    want, places=12)

    def test_calculate_esm_uls_and_sls_spectrum(self):
        stories = [{"height_m": 3.0, "dead_load_kN": 1000.0},
                   {"height_m": 6.0, "dead_load_kN": 1000.0}]
        for module in (code_basis, legacy_code_basis):
            for soil in SOILS:
                for t in (0.2, 0.8, 1.7, 3.0, 5.0):
                    elastic = c4.elastic_site_spectrum(t, soil, self.Z, self.I, method=ESM)
                    uls = module.calculate_esm(
                        stories, period_s=t, soil_type=soil, zoning_factor_z=self.Z,
                        importance_factor_i=self.I, limit_state="ULS", r_mu=4.0,
                        omega_u=1.5)
                    self.assertAlmostEqual(uls["elastic_spectrum_C_k"], elastic, places=12)
                    self.assertAlmostEqual(uls["design_coefficient_Cd"],
                                           elastic / (4.0 * 1.5), places=12)
                    sls = module.calculate_esm(
                        stories, period_s=t, soil_type=soil, zoning_factor_z=self.Z,
                        importance_factor_i=self.I, limit_state="SLS", omega_s=1.25)
                    self.assertAlmostEqual(
                        sls["design_coefficient_Cd"],
                        c4.serviceability_spectrum(t, soil, self.Z, self.I, method=ESM) / 1.25,
                        places=12)
                    self.assertAlmostEqual(sls["design_coefficient_Cd"] * 1.25 * 5.0,
                                           elastic, places=12)

    def test_reconcile_serviceability_uses_020(self):
        z, i = reconcile.Z, reconcile.IMPORTANCE
        for t in (0.3, 0.9, 1.4, 3.0):
            got = reconcile.static_parameters(t, 1000.0)
            self.assertAlmostEqual(
                got["cd_sls"],
                c4.serviceability_spectrum(t, "C", z, i, method=ESM) / reconcile.OMEGA_S,
                places=12)
            self.assertAlmostEqual(
                got["cd_uls"],
                c4.elastic_site_spectrum(t, "C", z, i, method=ESM)
                / (reconcile.R_MU * reconcile.OMEGA_U), places=12)


class SoilClassifierParity(unittest.TestCase):
    VS30 = (149.999, 150.0, 150.001, 350.0, 350.001, 800.0, 800.001)
    NSPT = (9.9, 10.0, 50.0, 50.1)

    def test_vs30_boundaries(self):
        expected = dict(zip(self.VS30, "DDCCBBA"))
        for v, soil in expected.items():
            self.assertEqual(c4.soil_type_from_vs30(v), soil, v)
            self.assertEqual(code_basis.soil_type_from_vs30(v), soil, v)

    def test_n_spt_boundaries(self):
        expected = dict(zip(self.NSPT, "DCCB"))
        for n, soil in expected.items():
            self.assertEqual(c4.soil_type_from_n_spt(n), soil, n)
            self.assertEqual(code_basis.soil_type_from_n_spt(n), soil, n)

    def test_classifier_rejections_agree(self):
        for fn in (code_basis.soil_type_from_vs30, c4.soil_type_from_vs30):
            for bad in (0.0, -1.0, float("nan"), float("inf")):
                with self.assertRaises(ValueError, msg=(fn.__module__, bad)):
                    fn(bad)

    def test_legacy_module_has_no_classifiers(self):
        # legacy_code_basis (V108) is a frozen predecessor of code_basis (V109).
        self.assertFalse(hasattr(legacy_code_basis, "soil_type_from_vs30"))
        self.assertFalse(hasattr(legacy_code_basis, "soil_type_from_n_spt"))

    def test_calculate_esm_height_over_40m_without_vs30_not_verified(self):
        stories = [{"height_m": 20.0, "dead_load_kN": 1000.0},
                   {"height_m": 45.0, "dead_load_kN": 1000.0}]
        result = code_basis.calculate_esm(
            stories, period_s=1.0, soil_type="C", zoning_factor_z=0.35,
            importance_factor_i=1.0, diagnostic_reference=True, n_spt_blow_30cm=30)
        self.assertFalse(result["site_subsoil_verified"])
        self.assertIn("4.1.3.1", result["site_subsoil_status"])
        issues = c4.select_soil_type(height_m=45.0, n_spt=30)
        self.assertIsNone(issues["soil"])


class ConstantScanTests(unittest.TestCase):
    """Behaviour of the remaining Z / I / 0.20 / 2/3 constants found with rg."""

    def _python_files(self):
        for base in ("components", "tools"):
            for path in (ROOT / base).rglob("*.py"):
                if "nbc105" in path.parts and path.parent.name == "nbc105":
                    continue
                yield path

    def test_no_production_code_applies_vertical_two_thirds_z(self):
        pattern = re.compile(r"(2\.?0?\s*/\s*3\.?0?|0\.66+7?)\s*\*\s*\(?\s*(z|zoning)",
                             re.IGNORECASE)
        hits = [str(p.relative_to(ROOT)) for p in self._python_files()
                if pattern.search(p.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(hits, [], "vertical 2/3 Z use must be reviewed against §4.3")

    def test_serviceability_020_only_in_reviewed_locations(self):
        pattern = re.compile(r"\b0\.20?\s*\*\s*(ch\b|elastic_spectrum|C\()")
        hits = sorted(str(p.relative_to(ROOT)).replace("\\", "/")
                      for p in self._python_files()
                      if pattern.search(p.read_text(encoding="utf-8", errors="replace")))
        self.assertEqual(hits, ["components/equivalent_static/code_basis.py",
                                "components/equivalent_static/legacy_code_basis.py",
                                "tools/etabs_period_review/reconcile.py"])
        self.assertAlmostEqual(0.20, 0.2)
        self.assertAlmostEqual(c4.serviceability_spectrum(0.0, "C", 0.35, 1.0, method=ESM),
                               0.20 * 2.5 * 0.35)

    def test_vertical_review_triggers_match_clause_4_3(self):
        source = (ROOT / "components" / "nonlinear_time_history"
                  / "nbc105_horizontal_input.py").read_text(encoding="utf-8")
        match = re.search(r"TRIGGERS=\((.*?)\n\)", source, re.S)
        self.assertIsNotNone(match)
        keys = re.findall(r'\("([a-z_0-9]+)"', match.group(1))
        self.assertEqual(keys, ["unsupported_horizontal_span_ge_20m",
                                "horizontal_cantilever_gt_5m",
                                "prestressed_horizontal_component",
                                "beam_supporting_column", "base_isolation"])
        self.assertEqual(len(keys), len(c4.VERTICAL_LOADING_CASES))
        self.assertAlmostEqual(c4.vertical_spectrum_coefficient(0.3), 0.2)

    def test_importance_factor_values_supplied_by_user_not_validated(self):
        # code_basis.calculate_esm takes I as an input and does not enforce
        # Table 4-4 (the project/user supplies it); the clause module is the
        # only Table 4-4 source.
        self.assertEqual([c4.importance_factor(1), c4.importance_factor(2),
                          c4.importance_factor(3)], [1.0, 1.25, 1.5])
        self.assertEqual(c4.importance_factor(2, disaster_shelter=True), 1.5)


if __name__ == "__main__":
    unittest.main()
