"""Source-only tests: no experiment or OpenSeesPy backend is present."""
import unittest
from components.nonlinear_time_history.research_building_materials import (
    check_project_material_qualification)

class WallMaterialsProjectGate(unittest.TestCase):
    def test_literature_materials_are_not_thesis_approved(self):
        with self.assertRaisesRegex(ValueError, "material BLOCKED"):
            check_project_material_qualification({
                "analysis_intent": "THESIS_NLTHA",
                "material_basis": "PUBLISHED_REFERENCE"})
    def test_m30_sensitivity_is_not_calibrated(self):
        with self.assertRaisesRegex(ValueError, "material BLOCKED"):
            check_project_material_qualification({
                "analysis_intent": "THESIS_NLTHA",
                "material_basis": "M30_FE500_SENSITIVITY"})
    def test_diagnostic_materials_report_uncalibrated(self):
        result=check_project_material_qualification({
            "analysis_intent":"RESEARCH_DIAGNOSTIC"})
        self.assertEqual(result["status"],"LITERATURE_MATERIALS_RESEARCH_ONLY")
        self.assertFalse(result["project_calibrated"])
        self.assertFalse(result["native_wall_benchmark_verified"])

if __name__=="__main__":unittest.main()
