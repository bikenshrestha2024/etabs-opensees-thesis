"""NBC 105 Annex A/B calculations must be separate from Clauses 1–10."""
import contextlib
import io
import json
import unittest
from components.nbc105.dispatch import available_operations
from components.nbc105.dispatch import available_annex_operations, run_annex_operation
from components.nbc105.__main__ import main


class AnnexDispatch(unittest.TestCase):
    def test_annex_functions_do_not_replace_ten_clause_contract(self):
        self.assertEqual(set(available_operations()),set(range(1,11)))
        annex=available_annex_operations()
        self.assertEqual(set(annex),{"A","B"})
        self.assertIn("rc_wall_detailing_minima",annex["A"])
        self.assertIn("seismic_link_rotation_limit_rad",annex["B"])

    def test_annex_a_coupled_wall_reference(self):
        result=run_annex_operation("A","rc_wall_detailing_minima",{
            "thickness_mm":600,"wall_length_mm":12000,"coupled":True,
            "fck_mpa":30,"shear_stress_mpa":1.,
            "horizontal_ratio":.0025,"vertical_ratio":.0025,
            "bar_diameter_mm":20,"bar_spacing_mm":200,
            "reinforcement_curtains":2})
        self.assertEqual(result["annex"],"A")
        self.assertTrue(result["result"]["geometry_and_rebar_minima_pass"])
        self.assertEqual(result["status"],"CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE")

    def test_annex_b_horizontal_link_rotation(self):
        result=run_annex_operation("B","seismic_link_rotation_limit_rad",{
            "link_length_m":1.6,"mp_kNm":100,"vp_kN":100,
            "orientation":"horizontal","section_type":"I"})
        self.assertAlmostEqual(result["result"],.08)
        self.assertEqual(result["annex"],"B")

    def test_invalid_annex_operations_blocked(self):
        with self.assertRaises(ValueError):
            run_annex_operation("C","seismic_link_rotation_limit_rad",{})
        with self.assertRaises(ValueError):
            run_annex_operation("A","_positive",{})
        with self.assertRaises(ValueError):
            run_annex_operation("B","__import__",{})

    def test_cli_can_evaluate_annex_without_certifying_design(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):
            code=main(["--annex","B","--operation","seismic_link_rotation_limit_rad",
                 "--json",'{"link_length_m":1.6,"mp_kNm":100,"vp_kN":100,"orientation":"horizontal","section_type":"I"}'])
        self.assertEqual(code,0)
        result=json.loads(output.getvalue())
        self.assertEqual(result["annex"],"B")
        self.assertEqual(result["status"],"CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE")


if __name__=="__main__":
    unittest.main()
