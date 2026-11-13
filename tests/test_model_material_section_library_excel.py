"""Model-library Excel export: deterministic, no ETABS/OpenSees runtime required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("library_excel", ROOT / "components" / "sections" / "library_excel.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ModelSectionLibraryExcelTests(unittest.TestCase):
    def test_four_gui_tables_and_source_evidence(self):
        try:
            from openpyxl import load_workbook
        except ImportError:
            self.skipTest("openpyxl absent in this Python environment")
        fake_tables = [
            ("Section formulations", [{"name": "RC_BEAM", "kind": "BEAM", "description": "UNVERIFIED"}]),
            ("Parameter values and citations", [
                {"family": "RC_BEAM", "parameter": "fy_rebar_mpa", "value": 550.0,
                 "unit": "MPa", "status": "Current editable template value; no project calibration evidence supplied",
                 "source": "https://opensees.github.io/OpenSeesDocumentation/"}
            ]),
            ("Current source parameters", [
                {"family": "Col 1100", "parameter": "E", "value": 33541019.9,
                 "unit": "kN/m2", "status": "CURRENT EXPORTED SOURCE VALUE; no nonlinear calibration"}
            ]),
            ("Validation and limits", [
                {"subsystem": "RC", "evidence": "illustrative", "validation": "NOT CALIBRATED"}
            ]),
        ]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "OpenSees_Complete_Model_Data_V118.json").write_text('{"frames":[]}', encoding="utf-8")
            path = Path(module.export_material_section_library(root, tables=fake_tables))
            self.assertTrue(path.is_file())
            self.assertEqual(path.parent, root / "02_MODEL" / "MATERIAL_SECTION_LIBRARY")
            self.assertIn("OpenSees_Material_Section_Library_", path.name)
            wb = load_workbook(path, read_only=True)
            self.assertEqual(wb.sheetnames, ["00_README_PROVENANCE",
                "Section formulations", "Parameter values and citations",
                "Current source parameters", "Validation and limits"])
            self.assertEqual(wb["Current source parameters"]["C2"].value, 33541019.9)
            self.assertIn("no project calibration", wb["Parameter values and citations"]["E2"].value)
            self.assertEqual(wb["Validation and limits"]["C2"].value, "NOT CALIBRATED")
            sha = module._fingerprint(root / "OpenSees_Complete_Model_Data_V118.json")
            self.assertEqual(wb["00_README_PROVENANCE"]["B5"].value, sha)
            with self.assertRaises(FileExistsError):
                module.export_material_section_library(root, path=path, tables=fake_tables)
            wb.close()

    def test_formula_strings_are_escaped(self):
        self.assertEqual(module._safe_excel_value("=HYPERLINK(\"http://bad\")"), "'=HYPERLINK(\"http://bad\")")
        self.assertEqual(module._safe_excel_value("@SUM(A1)"), "'@SUM(A1)")
        self.assertEqual(module._safe_excel_value(-0.002), -0.002)
        self.assertEqual(module._safe_excel_value("ordinary label"), "ordinary label")

    def test_cannot_export_to_unselected_missing_model(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                module.export_material_section_library(Path(d) / "does-not-exist", tables=[])


if __name__ == "__main__":
    unittest.main()
