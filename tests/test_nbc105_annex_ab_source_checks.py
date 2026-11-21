"""Source-based Annex A/B checks: only correctly scoped RC walls and steel links.

Printed NBC 105:2025 Annex A pp.76–79 and Annex B pp.95–98.
"""
import math
import unittest
from components.nbc105.annex_a_rc_detailing import (
    rc_wall_detailing_minima, rc_wall_boundary_element_requirement,
    coupling_beam_diagonal_required, rc_wall_opening_rebar_review)
from components.nbc105.annex_b_steel_detailing import seismic_link_rotation_limit_rad

class AnnexAWallTests(unittest.TestCase):
    def test_600mm_coupled_rc_wall_basic_detailing_limits(self):
        result=rc_wall_detailing_minima(
            thickness_mm=600,wall_length_mm=12000,coupled=True,
            fck_mpa=30,shear_stress_mpa=1.,
            horizontal_ratio=.0025,vertical_ratio=.0025,
            bar_diameter_mm=20,bar_spacing_mm=200,reinforcement_curtains=2)
        self.assertTrue(result["geometry_and_rebar_minima_pass"])
        self.assertEqual(result["min_thickness_mm"],300)
        self.assertEqual(result["max_bar_spacing_mm"],450)
        self.assertTrue(result["two_curtains_required"])
        self.assertEqual(result["max_bar_diameter_mm"],60)

    def test_coupled_wall_250mm_is_not_compliant(self):
        result=rc_wall_detailing_minima(
            thickness_mm=250,wall_length_mm=12000,coupled=True,
            fck_mpa=30,shear_stress_mpa=0.,
            horizontal_ratio=.0025,vertical_ratio=.0025,
            bar_diameter_mm=20,bar_spacing_mm=200,reinforcement_curtains=2)
        self.assertFalse(result["geometry_and_rebar_minima_pass"])
        self.assertIn("THICKNESS_LT_COUPLED_MINIMUM",result["violations"])

    def test_boundary_zone_compression_requirement(self):
        check=rc_wall_boundary_element_requirement(
            fck_mpa=30,extreme_compression_mpa=6.01,wall_length_mm=12000,
            longitudinal_ratio=.008)
        self.assertTrue(check["boundary_required"])
        self.assertAlmostEqual(check["boundary_length_each_end_mm"],2400)
        self.assertTrue(check["ratio_pass"])
        check=rc_wall_boundary_element_requirement(
            fck_mpa=30,extreme_compression_mpa=6.,wall_length_mm=12000,
            longitudinal_ratio=.008)
        self.assertFalse(check["boundary_required"])

    def test_coupling_beam_diagonal_rule(self):
        self.assertTrue(coupling_beam_diagonal_required(
            shear_stress_mpa=1.0,fck_mpa=30,clear_span_mm=1200,depth_mm=1000))
        self.assertFalse(coupling_beam_diagonal_required(
            shear_stress_mpa=.1,fck_mpa=30,clear_span_mm=1200,depth_mm=1000))

    def test_wall_opening_rebar_full_story_and_each_side_rule(self):
        # For 1000 mm2 interrupted in each direction, at least 500 mm2
        # additional along each side; wall-critical-plane shear also checked.
        kw=dict(interrupted_vertical_mm2=1000,interrupted_horizontal_mm2=1000,
                additional_vertical_each_side_mm2=500,
                additional_horizontal_each_side_mm2=500,
                vertical_bars_full_storey=True,
                horizontal_bars_development_length=True,
                critical_opening_plane_shear_checked=True)
        from copy import deepcopy
        self.assertTrue(rc_wall_opening_rebar_review(**kw)["checklist_pass"])
        bad=deepcopy(kw);bad["additional_horizontal_each_side_mm2"]=499.
        self.assertFalse(rc_wall_opening_rebar_review(**bad)["checklist_pass"])
        bad=deepcopy(kw);bad["critical_opening_plane_shear_checked"]=False
        self.assertIn("CRITICAL_PLANE_SHEAR_NOT_CHECKED",
                      rc_wall_opening_rebar_review(**bad)["missing"])

class AnnexBLinkTests(unittest.TestCase):
    def test_horizontal_link_classification_and_interpolation(self):
        # Mp/Vp = 1m, so short/long breakpoints are e=1.6/3.0m.
        self.assertAlmostEqual(seismic_link_rotation_limit_rad(
            link_length_m=1.6,mp_kNm=100,vp_kN=100,orientation="horizontal",section_type="I"),.08)
        self.assertAlmostEqual(seismic_link_rotation_limit_rad(
            link_length_m=3,mp_kNm=100,vp_kN=100,orientation="horizontal",section_type="I"),.02)
        self.assertAlmostEqual(seismic_link_rotation_limit_rad(
            link_length_m=2.3,mp_kNm=100,vp_kN=100,orientation="horizontal",section_type="I"),.05)
    def test_vertical_link_rotation_interpolates_with_moment_ratio(self):
        # alpha=0.5 => short/long e=1.2/2.25 m at Mp/Vp=1m
        self.assertAlmostEqual(seismic_link_rotation_limit_rad(
            link_length_m=1.2,mp_kNm=100,vp_kN=100,orientation="vertical",alpha=.5,section_type="I"),.08)
        self.assertAlmostEqual(seismic_link_rotation_limit_rad(
            link_length_m=2.25,mp_kNm=100,vp_kN=100,orientation="vertical",alpha=.5,section_type="I"),.02)
    def test_not_a_general_outrigger_damper_rotation_rule(self):
        with self.assertRaises(ValueError):
            seismic_link_rotation_limit_rad(
                link_length_m=2,mp_kNm=100,vp_kN=100,orientation="fvd",section_type="I")
    def test_shs_cannot_be_treated_as_annex_b_seismic_i_link(self):
        with self.assertRaises(ValueError):
            seismic_link_rotation_limit_rad(
                link_length_m=1.6,mp_kNm=100,vp_kN=100,
                orientation="horizontal",section_type="SHS")

    def test_invalid_geometry_or_demand_rejected(self):
        for length in (0,-1,float("inf"),float("nan")):
            with self.assertRaises(ValueError):
                seismic_link_rotation_limit_rad(
                    link_length_m=length,mp_kNm=100,vp_kN=100,orientation="horizontal")

if __name__=="__main__":
    unittest.main()
