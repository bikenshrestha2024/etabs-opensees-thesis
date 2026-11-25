"""Fast synthetic evidence tests: no ETABS or OpenSees installation required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from components.gravity.three_case_comparison import collect_cases, export_case_comparison


class TestThreeCaseGravity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.model = self.root / "OpenSees_Complete_Gravity_Model.py"
        self.model.write_text("pass\n", encoding="utf-8")

    def test_no_solved_case_never_substitutes_defaults(self):
        with patch("components.gravity.three_case_comparison.current_case_diagnostic",
                   return_value={"result":None,"status":"NO_CASE_INDEX",
                                 "reason":"fixture has no indexed runs"}):
            with self.assertRaisesRegex(ValueError, "No current separately solved"):
                collect_cases(self.root, self.model)

    def test_separate_real_cases_and_missing_status(self):
        def current(_root, _model, *, scenario, profile):
            if scenario == "CONTINUOUS_WALL_BASE_FIXED":
                return None
            n = 32 if scenario == "ETABS_NONZERO_REACTION_DIAGNOSTIC" else 76
            result = self.root / ("case_" + str(n) + ".json")
            result.write_text(json.dumps({"ok": True, "reactions": [{"node_tag": i} for i in range(n)]}))
            return {"result_path": str(result), "applied_load_kN": 100.0}
        with patch("components.gravity.three_case_comparison.current_case_diagnostic",
                   side_effect=lambda *a,**k:{
                       "result":current(*a,**k),
                       "status":"CASE_NOT_INDEXED",
                       "reason":"fixture 97 missing"}):
            available, missing = collect_cases(self.root, self.model)
        self.assertEqual(set(available), {"32", "76"})
        self.assertEqual(len(missing), 1)
        self.assertIn("97", missing[0])

    def test_partial_cases_export_missing_as_blank_not_keyerror(self):
        (self.root/'OpenSees_Complete_Story_Masters_V118.csv').write_text('elevation_m\n3.8\n',encoding='utf-8')
        def current(_root, _model, *, scenario, profile):
            if scenario == "CONTINUOUS_WALL_BASE_FIXED":
                return None
            n = 32 if scenario == "ETABS_NONZERO_REACTION_DIAGNOSTIC" else 76
            result = self.root / ("case_" + str(n) + ".json")
            result.write_text(json.dumps({
                "ok": True,
                "reactions": [{"node_tag": i, "rz_kN": 100.0 / n}
                              for i in range(n)],
                "nodes": [{"tag": i, "ux_m": 0.0, "uy_m": 0.0,
                           "uz_m": -0.001, "z_m": [0., 1.9, 3.8][i%3]}
                          for i in range(n)]
            }))
            return {"result_path": str(result), "applied_load_kN": 100.0,
                    "summed_reaction_kN": 100.0,
                    "equilibrium_error_percent": 0.0}
        with patch("components.gravity.three_case_comparison.current_case_diagnostic",
                   side_effect=lambda *a,**k:{
                       "result":current(*a,**k),
                       "status":"CASE_NOT_INDEXED",
                       "reason":"fixture 97 missing"}):
            report, directory, _figure = export_case_comparison(self.root, self.model)
        self.assertEqual(list(_figure.axes[1].lines[0].get_ydata()), [0.0, 3.8])
        self.assertEqual(_figure.axes[1].lines[0].get_linestyle(), 'None')
        self.assertEqual(set(report["available_cases"]), {"32", "76"})
        import csv
        with (directory / "Support_Reactions_32_76_97.csv").open(encoding="utf-8-sig") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 76)
        self.assertIn("rz_32_kN", rows[0])
        self.assertIn("rz_76_kN", rows[0])
        self.assertIn("rz_97_kN", rows[0])
        self.assertEqual(rows[0]["rz_97_kN"], "")
        self.assertEqual(rows[50]["rz_32_kN"], "")
        # The original exporter reversed (strategy, label) and silently
        # wrote every displacement value as a blank. Verify actual numbers,
        # including a legitimate missing-case blank for the 97-node case.
        with (directory / "Common_Node_Displacements_32_76_97.csv").open(
                encoding="utf-8-sig") as fp:
            displacements = list(csv.DictReader(fp))
        self.assertEqual(len(displacements), 32)
        first = displacements[0]
        self.assertAlmostEqual(
            float(first["uz_m_ETABS_NONZERO_REACTION_DIAGNOSTIC"]), -0.001)
        self.assertAlmostEqual(
            float(first["uz_m_ETABS_SOURCE_SUPPORTS"]), -0.001)
        self.assertEqual(first["uz_m_CONTINUOUS_WALL_BASE_FIXED"], "")

    def test_load_discrepancy_is_blocker(self):
        def current(_root, _model, *, scenario, profile):
            n = {"ETABS_NONZERO_REACTION_DIAGNOSTIC": 32,
                 "ETABS_SOURCE_SUPPORTS": 76,
                 "CONTINUOUS_WALL_BASE_FIXED": 97}[scenario]
            result = self.root / ("case_" + str(n) + ".json")
            result.write_text(json.dumps({"ok": True, "reactions": [{"node_tag": i} for i in range(n)]}))
            return {"result_path": str(result),
                    "applied_load_kN": 101.0 if n == 76 else 100.0}
        with patch("components.gravity.three_case_comparison.current_case_diagnostic",
                   side_effect=lambda *a,**k:{
                       "result":current(*a,**k),
                       "status":"CASE_NOT_INDEXED",
                       "reason":"fixture 97 missing"}):
            with self.assertRaisesRegex(ValueError, "different applied gravity"):
                collect_cases(self.root, self.model)

    def test_export_writes_solved_case_list_as_excel_text(self):
        from openpyxl import load_workbook

        result = self.root / "Gravity_Result_V110.json"
        available = {}
        for label in ("32", "76", "97"):
            entry = dict(result_path=str(result), applied_load_kN=100.0,
                         summed_reaction_kN=100.0, equilibrium_error_percent=0.0)
            payload = dict(nodes=[dict(tag=1, x_m=0., y_m=0., z_m=0., ux_m=0., uy_m=0., uz_m=0.)],
                           reactions=[dict(node_tag=1, rz_kN=100.)])
            available[label] = (entry, payload)
        metadata = {"available_solved_case_columns": ["32", "76", "97"],
                    "source_support_count": 76,
                    "opensees_76_reaction_at_source_zero_ETABS_points_kN": 42.5}
        with patch("components.gravity.three_case_comparison.collect_cases", return_value=(available, [])), \
             patch("components.gravity.three_case_comparison.join_source_etabs_reactions", return_value=([], metadata)):
            report, directory, _ = export_case_comparison(self.root, self.model)

        self.assertEqual(report["etabs_source_support_comparison"]["available_solved_case_columns"],
                         ["32", "76", "97"])
        workbook = load_workbook(directory / "Gravity_32_76_97_Comparison.xlsx", read_only=True)
        try:
            evidence = dict(workbook["Evidence status"].values)
            self.assertEqual(evidence["ETABS_SOURCE_available_solved_case_columns"], "32, 76, 97")
            self.assertEqual(evidence["ETABS_SOURCE_source_support_count"], 76)
            self.assertEqual(evidence["ETABS_SOURCE_opensees_76_reaction_at_source_zero_ETABS_points_kN"], 42.5)
        finally:
            workbook.close()


if __name__ == "__main__":
    unittest.main()
