"""Only literature-identified, research-only Steel02 parameter plans are allowed."""
import math
import tempfile
import unittest
from pathlib import Path

from components.nonlinear_time_history.steel02_carreno_reference import (
    build_carreno_study, write_carreno_study
)
from components.nonlinear_time_history.research_building_materials import (
    validate_material_overrides, validate_frame_section_parameters
)


class CarrenoSteel02SourceTests(unittest.TestCase):
    def test_paper_reference_values_have_distinct_astm_grades(self):
        report=build_carreno_study()
        by_id={c["case_id"]:c for c in report["cases"]}
        self.assertEqual(report["status"],"RESEARCH_PLANNING_ONLY_NOT_CALIBRATION")
        self.assertFalse(report["project_steel_calibrated"])
        a=by_id["CARRENO_ASTM_A615_G60_REFERENCE"]["parameters"]
        b=by_id["CARRENO_ASTM_A706_G60_REFERENCE"]["parameters"]
        self.assertEqual((a["Fy_MPa"],a["E_MPa"],a["b"]),(480,202000,.02))
        self.assertEqual((b["Fy_MPa"],b["E_MPa"],b["b"]),(476,202000,.012))
        for p in (a,b):
            self.assertEqual((p["R0"],p["cR1"],p["cR2"]),(20,.9,.08))
            self.assertEqual((p["a1"],p["a2"],p["a3"],p["a4"]),(.039,1.,.029,1.))
            self.assertAlmostEqual(p["Fy_kN_m2"],p["Fy_MPa"]*1000.)
        self.assertFalse(any(c.get("auto_apply_to_building") for c in report["cases"]))

    def test_shape_only_fe500_keeps_original_strength_and_hardening(self):
        report=build_carreno_study()
        by_id={c["case_id"]:c for c in report["cases"]}
        x=by_id["FE500_SHAPE_ONLY_CARRENO_TRANSFER"]["parameters"]
        baseline=by_id["NOMINAL_FE500_EXISTING_BASELINE"]["parameters"]
        for key in ("Fy_MPa","E_MPa","b","a1","a2","a3","a4"):
            self.assertEqual(x[key],baseline[key])
        self.assertEqual((x["cR1"],x["cR2"]),(.9,.08))
        self.assertEqual(baseline["cR1"],.925)
        self.assertEqual(baseline["cR2"],.15)
        self.assertIn("NOT experimentally calibrated Fe500",report["limitations"][0])

    def test_result_never_claims_solver_execution_or_design_approval(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"REVIEW_MAIN"/"CARRENO_STUDY.json"
            report=write_carreno_study(target)
            self.assertEqual(report["status"],"RESEARCH_PLANNING_ONLY_NOT_CALIBRATION")
            self.assertTrue(target.is_file())
            self.assertFalse(report["native_opensees_executed"])
            self.assertFalse(report["engineering_design_acceptance"])
            self.assertIn("doi.org",report["reference"]["url"])

    def test_invalid_baseline_is_not_silently_repaired(self):
        for value in (True,float("nan"),-5,0,1e12):
            with self.subTest(value=value):
                with self.assertRaises((ValueError,TypeError)):
                    build_carreno_study(nominal_fy_mpa=value)

    def test_absolute_menegotto_parameter_is_not_valid_cr1(self):
        for path in ("frame.steel_cR1","wall.cR1"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError,"cR1"):
                    validate_material_overrides({path:18.5})
                self.assertEqual(validate_material_overrides({path:.9})[path],.9)

    def test_incompatible_frame_transition_fails_before_nonlinear_solver(self):
        section={"cover_fc_mpa":30.,"cover_fcu_mpa":0.,
                 "cover_epsc0":-.002,"cover_epsU":-.006,
                 "core_fcc_mpa":30.,"core_fpcu_mpa":0.,
                 "core_epsc0":-.002,"core_epsU":-.006,
                 "steel_R0":20.,"steel_cR1":18.5,"steel_cR2":.15}
        with self.assertRaisesRegex(ValueError,"cR1"):
            validate_frame_section_parameters(section)
        section["steel_cR1"]=.925
        self.assertIsNone(validate_frame_section_parameters(section))


if __name__=="__main__":
    unittest.main()
