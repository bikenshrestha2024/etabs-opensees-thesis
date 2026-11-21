"""Hand-computed tests for NBC 105:2025 clause 1 (printed pp. 1-9).

[REF NBC105-2025 §1, printed pp. 1-9] Every expected value below was read from
the printed page images (PDF pages 22-30) and written out literally. Unit tests
only; no native ETABS/OpenSees; a pass is not engineering acceptance.
"""
import math
import unittest

from components.nbc105 import clause_01_scope_definitions as c1
from components.nbc105 import constants

# Printed order of the notation list, literally from pp. 6-9.
PRINTED_SYMBOLS = {
    6: ["ap", "Aw", "b", "CQC", "C(T)", "Cd(T)", "Cd(T1)", "Ch(T)", "Cs(T)",
        "Cv(T)", "Cd(Ti)", "DL", "d*", "det*", "di", "dy*", "E", "ESM", "ec"],
    7: ["ed", "Ec", "Ex", "Ey", "F*", "Fi", "Fp", "Fy*", "g", "H", "hi", "hp",
        "i", "I", "Ip", "Ig", "LL", "m*", "MRSM", "n", "PGA", "RC"],
    8: ["Rs", "Rmu", "Sep", "Sgw", "Sice", "Slp", "Spnd", "Sso", "SDOF", "SRSS",
        "T*", "T1", "Tc", "Ti", "T", "V", "VR", "W", "Wi", "Wp", "wj"],
    9: ["Z", "Omega_s", "Omega_u", "alpha", "mu_p", "phi_ji"],
}


class NotationTableTests(unittest.TestCase):
    def test_per_page_symbols_in_printed_order(self):
        for page, symbols in PRINTED_SYMBOLS.items():
            got = [n.symbol for n in c1.NOTATIONS if n.page == page]
            self.assertEqual(got, symbols, "printed p. %d" % page)

    def test_counts(self):
        self.assertEqual(c1.notation_page_counts(), {6: 19, 7: 22, 8: 21, 9: 6})
        self.assertEqual(len(c1.NOTATIONS), 68)
        symbols = [n.symbol for n in c1.NOTATIONS]
        self.assertEqual(len(symbols), len(set(symbols)))

    def test_gravity_printed_p7(self):
        g = c1.notation("g")
        self.assertEqual(g.page, 7)
        self.assertEqual(g.printed_value, 9.81)
        self.assertEqual(g.unit, "m/s^2")
        self.assertEqual(g.unit_basis, "PRINTED")
        self.assertEqual(c1.printed_gravity_m_s2(), 9.81)
        self.assertEqual([n.symbol for n in c1.NOTATIONS if n.printed_value is not None], ["g"])

    def test_height_unit_printed(self):
        h = c1.notation("H")
        self.assertEqual((h.page, h.unit, h.unit_basis), (7, "m", "PRINTED"))
        self.assertEqual(h.meaning, "Height from the base to the top of the main portion "
                         "of the building or the eaves of the building (m)")

    def test_selected_meanings(self):
        m = {s: c1.notation(s).meaning for s in
             ["Aw", "Ch(T)", "Cd(T1)", "Ec", "Ig", "T1", "Tc", "Ti", "V", "VR", "W", "Wi",
              "Rmu", "Rs", "alpha", "Omega_u", "Omega_s", "Z", "I", "wj"]}
        self.assertEqual(m["Aw"], "Area of Web")
        self.assertEqual(m["Ch(T)"], "Spectral Shape Factor")
        self.assertEqual(m["Cd(T1)"], "Horizontal Base Shear Coefficient")
        self.assertEqual(m["Ec"], "Modulus of Elasticity of Concrete")
        self.assertEqual(m["Ig"], "Section moment of inertia calculated using the gross "
                         "cross sectional area of concrete")
        self.assertEqual(m["T1"], "Approximate Fundamental Period of Vibration")
        self.assertEqual(m["Tc"], "Corner period corresponding to the end of constant "
                         "spectral acceleration range")
        self.assertEqual(m["Ti"], "Fundamental Translation Period of ith mode of vibration")
        self.assertEqual(m["V"], "Horizontal seismic base shear obtained from equivalent static method")
        self.assertEqual(m["VR"], "Combined base shear obtained from modal response spectrum method")
        self.assertEqual(m["W"], "Seismic weight of the structure")
        self.assertEqual(m["Wi"], "Seismic weight at level I;")
        self.assertEqual(m["Rmu"], "Ductility Factor for Ultimate Limit State")
        self.assertEqual(m["Rs"], "Ductility Factor for Serviceability Limit State")
        self.assertEqual(m["alpha"], "Peak spectral acceleration normalized by PGA")
        self.assertEqual(m["Omega_u"], "Overstrength factor for ultimate limit state")
        self.assertEqual(m["Omega_s"], "Overstrength factor for serviceability limit state")
        self.assertEqual(m["Z"], "Seismic zoning factor")
        self.assertEqual(m["I"], "Importance factor for the building")
        self.assertEqual(m["wj"], "portion of gravity load at story level j")

    def test_unit_basis_vocabulary_and_si_derivation(self):
        allowed = {"PRINTED", "SI_DERIVED", "DIMENSIONLESS", "NOT_STATED", "NOT_APPLICABLE"}
        self.assertTrue({n.unit_basis for n in c1.NOTATIONS} <= allowed)
        # Only g and H print a unit in the notation list itself.
        self.assertEqual(sorted(n.symbol for n in c1.NOTATIONS if n.unit_basis == "PRINTED"),
                         ["H", "g"])
        # Clause 1.5 SI (kg, m, s, Pa, N) derivations, no printed unit.
        self.assertEqual((c1.notation("m*").unit, c1.notation("m*").unit_basis), ("kg", "SI_DERIVED"))
        self.assertEqual(c1.notation("W").unit, "N")
        self.assertEqual(c1.notation("Ec").unit, "Pa")
        self.assertEqual(c1.notation("Ig").unit, "m^4")
        self.assertEqual(c1.notation("Aw").unit, "m^2")
        self.assertEqual(c1.notation("T1").unit, "s")
        self.assertEqual(c1.notation("Z").unit_basis, "DIMENSIONLESS")
        self.assertEqual(c1.notation("CQC").unit_basis, "NOT_APPLICABLE")
        self.assertEqual(c1.notation("DL").unit_basis, "NOT_STATED")

    def test_unknown_symbol_rejected(self):
        with self.assertRaises(KeyError):
            c1.notation("Ta")  # Ta appears in Table 4-1 but not in the notation list
        with self.assertRaises(KeyError):
            c1.notation("")
        with self.assertRaises(KeyError):
            c1.notation(None)

    def test_page_offset(self):
        self.assertEqual(constants.PRINTED_PAGE_OFFSET, 21)
        self.assertEqual([c1.pdf_page_for_printed(p) for p in (1, 6, 7, 8, 9)],
                         [22, 27, 28, 29, 30])
        for bad in (0, 10, -1, 1.5, True, "1"):
            with self.assertRaises(ValueError):
                c1.pdf_page_for_printed(bad)

    def test_constants_follow_printed_gravity(self):
        self.assertEqual(constants.GRAVITY_M_S2, c1.printed_gravity_m_s2())
        self.assertEqual(constants.NBC_NOTATION_GRAVITY_M_S2, c1.printed_gravity_m_s2())
        self.assertNotEqual(constants.SUPERSEDED_GRAVITY_M_S2, c1.printed_gravity_m_s2())


class ScopeTests(unittest.TestCase):
    def test_printed_scope_lists(self):
        self.assertEqual(c1.SCOPE_MATERIALS, (
            "reinforced concrete", "structural steel", "steel concrete composite",
            "timber", "masonry"))
        self.assertEqual(c1.SPECIALIST_LITERATURE_SYSTEMS, ("base-isolated", "structural control"))
        self.assertIsNone(c1.SCOPE_HEIGHT_LIMIT_M)  # "all buildings, low to high rise"
        self.assertEqual(c1.EARLIER_VERSION, "NBC 105: 1994 Seismic Design of Buildings in Nepal")

    def test_in_scope_any_height(self):
        for mat in c1.SCOPE_MATERIALS:
            r = c1.scope_check(mat, height_m=95.0)
            self.assertEqual(r["status"], "IN_SCOPE")
            self.assertIsNone(r["height_limit_m"])
        self.assertEqual(c1.scope_check("RC")["status"], "IN_SCOPE")
        self.assertEqual(c1.scope_check("  Reinforced-Concrete ")["status"], "IN_SCOPE")
        self.assertEqual(c1.scope_check("steel_concrete_composite")["status"], "IN_SCOPE")
        self.assertEqual(c1.scope_check("Steel-Concrete Composite")["status"], "IN_SCOPE")

    def test_specialist_systems(self):
        self.assertEqual(c1.scope_check("reinforced concrete", base_isolated=True)["status"],
                         "SPECIALIST_LITERATURE")
        self.assertEqual(c1.scope_check("structural steel", structural_control=True)["status"],
                         "SPECIALIST_LITERATURE")

    def test_material_not_listed_is_not_an_error(self):
        r = c1.scope_check("bamboo")
        self.assertEqual(r["status"], "MATERIAL_NOT_LISTED")

    def test_rejections(self):
        for bad in ("", "   ", None, 3):
            with self.assertRaises(ValueError):
                c1.scope_check(bad)
        for h in (-1.0, 0.0, float("nan"), float("inf"), True, "10"):
            with self.assertRaises(ValueError):
                c1.scope_check("RC", height_m=h)
        for flag in (1, "yes", None):
            with self.assertRaises(ValueError):
                c1.scope_check("RC", base_isolated=flag)
            with self.assertRaises(ValueError):
                c1.scope_check("RC", structural_control=flag)


class DefinitionThresholdTests(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(c1.DUAL_SYSTEM_MIN_FRAME_SHARE, 0.25)
        self.assertEqual(c1.SOFT_STORY_ADJACENT_RATIO, 0.70)
        self.assertEqual(c1.SOFT_STORY_THREE_ABOVE_RATIO, 0.80)
        self.assertEqual(c1.FLEXIBLE_DIAPHRAGM_DEFORMATION_RATIO, 2.0)
        self.assertAlmostEqual(c1.DESIGN_BASIS_EARTHQUAKE_MCE_FRACTION, 2.0 / 3.0)
        self.assertEqual(c1.RESPONSE_SPECTRUM_COMMON_DAMPING_RATIO, 0.05)

    def test_soft_story_adjacent(self):
        # 69 < 0.7*100 = 70 -> soft; exactly 70 is not "less than 70 per cent".
        self.assertTrue(c1.is_soft_story(69.0, 100.0))
        self.assertFalse(c1.is_soft_story(70.0, 100.0))
        self.assertFalse(c1.is_soft_story(71.0, 100.0))

    def test_soft_story_three_above(self):
        # Adjacent ratio fine (80/100 = 0.8 > 0.7) but 80 < 0.8 * mean(100,110,120)=88 -> soft.
        self.assertTrue(c1.is_soft_story(80.0, 100.0, three_above=(100.0, 110.0, 120.0)))
        # k = 88 = 0.8 * 110 mean of (100,110,120)=110 -> 0.8*110 = 88: boundary, not soft.
        self.assertFalse(c1.is_soft_story(88.0, 100.0, three_above=(100.0, 110.0, 120.0)))
        self.assertFalse(c1.is_soft_story(89.0, 100.0, three_above=(100.0, 110.0, 120.0)))
        # Without the three-above data only the 70 per cent rule can be applied.
        self.assertFalse(c1.is_soft_story(80.0, 100.0))

    def test_soft_story_rejections(self):
        for args in ((0.0, 1.0), (-1.0, 1.0), (1.0, 0.0), (float("nan"), 1.0), (1.0, float("inf")), (True, 1.0)):
            with self.assertRaises(ValueError):
                c1.is_soft_story(*args)
        for bad in ((1.0, 2.0), (1.0, 2.0, 3.0, 4.0), (1.0, 2.0, 0.0), (1.0, 2.0, float("nan"))):
            with self.assertRaises(ValueError):
                c1.is_soft_story(50.0, 100.0, three_above=bad)

    def test_flexible_diaphragm(self):
        # "more than two times the average story drift"
        self.assertTrue(c1.is_flexible_diaphragm(2.01, 1.0))
        self.assertFalse(c1.is_flexible_diaphragm(2.0, 1.0))
        self.assertFalse(c1.is_flexible_diaphragm(1.5, 1.0))
        for args in ((1.0, 0.0), (-1.0, 1.0), (float("nan"), 1.0), (1.0, float("inf"))):
            with self.assertRaises(ValueError):
                c1.is_flexible_diaphragm(*args)

    def test_dual_system_frame_share(self):
        # frames must independently resist at least 25 % of the design base shear
        self.assertTrue(c1.dual_system_frame_share_ok(250.0, 1000.0))
        self.assertTrue(c1.dual_system_frame_share_ok(300.0, 1000.0))
        self.assertFalse(c1.dual_system_frame_share_ok(249.0, 1000.0))
        self.assertAlmostEqual(c1.dual_system_frame_share(300.0, 1200.0), 0.25)
        for args in ((-1.0, 100.0), (10.0, 0.0), (float("nan"), 100.0)):
            with self.assertRaises(ValueError):
                c1.dual_system_frame_share_ok(*args)

    def test_design_basis_earthquake(self):
        self.assertAlmostEqual(c1.design_basis_earthquake_from_mce(0.6), 0.4)
        self.assertAlmostEqual(c1.design_basis_earthquake_from_mce(1.5), 1.0)
        for bad in (0.0, -1.0, float("nan")):
            with self.assertRaises(ValueError):
                c1.design_basis_earthquake_from_mce(bad)

    def test_ductility_and_overstrength_ratios(self):
        # ductility factor = ultimate / yield displacement demand
        self.assertAlmostEqual(c1.ductility_factor(0.12, 0.03), 4.0)
        # overstrength factor = first significant yield strength / design base shear
        self.assertAlmostEqual(c1.overstrength_factor(1400.0, 1000.0), 1.4)
        for fn in (c1.ductility_factor, c1.overstrength_factor):
            for args in ((1.0, 0.0), (0.0, 1.0), (-1.0, 1.0), (float("nan"), 1.0)):
                with self.assertRaises(ValueError):
                    fn(*args)

    def test_eccentricity(self):
        # distance between centre of mass and centre of stiffness: 3-4-5
        self.assertAlmostEqual(c1.eccentricity_m((0.0, 0.0), (3.0, 4.0)), 5.0)
        self.assertEqual(c1.eccentricity_m((1.0, 1.0), (1.0, 1.0)), 0.0)
        for bad in (((0.0, 0.0), (1.0,)), ((0.0, float("nan")), (1.0, 1.0)), (None, (1.0, 1.0))):
            with self.assertRaises(ValueError):
                c1.eccentricity_m(*bad)


if __name__ == "__main__":
    unittest.main()
