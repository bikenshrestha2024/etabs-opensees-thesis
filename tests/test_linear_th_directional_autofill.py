"""Linear TH directional NBC §5.1.3 autofill regression (no ETABS/OpenSees required)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import sys

from components.inputs.analysis_autofill import populate_linear


class Field:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = str(value)


def gui(state="ULS"):
    return SimpleNamespace(**{key: Field() for key in
         ("t1x", "t1y", "p1", "p2", "tnx", "tny", "nmodes", "output")},
         ls=Field(state))


class LinearAdoptedPeriodTests(unittest.TestCase):
    def test_both_axes_from_shared_mrsm_resolver(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "OpenSees_Complete_Model_Data_V118.json").write_text(
                json.dumps({"nodes": {"1": [0, 0, 0], "2": [0, 0, 90]},
                            "base_z_m": 0}), encoding="utf-8")
            imported = {"values": {}, "notes": []}
            from components.response_spectrum import model_analysis
            from OpenSees_Project_Inputs_V123 import import_project_inputs
            with patch("OpenSees_Project_Inputs_V123.import_project_inputs",
                       return_value=imported), patch.object(
                       model_analysis, "mrsm_period_defaults",
                       return_value=({"T1_X": 2.0385674, "T1_Y": 1.92197978},
                                     "Reviewed source/state Rayleigh and Aw")) as resolve:
                app = gui()
                populate_linear(app, folder)
            self.assertAlmostEqual(float(app.t1x.get()), 2.0385674)
            self.assertAlmostEqual(float(app.t1y.get()), 1.92197978)
            self.assertEqual(resolve.call_args.args[0], folder)
            self.assertEqual(resolve.call_args.args[2], "ULS")
            self.assertIn("Linear TH directional adopted T1", " ".join(imported["notes"]))

    def test_missing_source_stays_blank_and_explains_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            imported = {"values": {}, "notes": []}
            from components.response_spectrum import model_analysis
            with patch("OpenSees_Project_Inputs_V123.import_project_inputs",
                       return_value=imported), patch.object(
                       model_analysis, "mrsm_period_defaults",
                       return_value=({"T1_X": "", "T1_Y": ""},
                                     "No source-verified current-model periods")):
                app = gui("ULS")
                populate_linear(app, folder)
            self.assertEqual(app.t1x.get(), "")
            self.assertEqual(app.t1y.get(), "")
            self.assertIn("BLOCKED T1", " ".join(imported["notes"]))

    def test_research_fallback_is_labeled(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            imported = {"values": {}, "notes": []}
            from components.response_spectrum import model_analysis
            with patch("OpenSees_Project_Inputs_V123.import_project_inputs",
                       return_value=imported), patch.object(
                       model_analysis, "mrsm_period_defaults",
                       return_value=({"T1_X": 2.0385, "T1_Y": 1.922},
                                     "Original ETABS-linked workbook adopted design-period references; "
                                     "fresh Rayleigh evidence unavailable. Research comparison only.")):
                app = gui()
                populate_linear(app, folder)
            self.assertIn("RESEARCH ONLY", " ".join(imported["notes"]))
            self.assertAlmostEqual(float(app.t1x.get()), 2.0385)


class AutoSelectRefreshRegression(unittest.TestCase):
    def test_successful_autoselect_still_refreshes_both_directional_periods(self):
        from components.inputs import analysis_autofill
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            model = folder / "OpenSees_Complete_Nonlinear_Model.py"
            model.write_text("# synthetic offline fixture",encoding="utf-8")
            app = gui()
            app.model = Field(str(model))
            app._output_is_automatic = False
            app.project_input_audit = {}
            lines = []
            app.log = SimpleNamespace(insert=lambda *_args: lines.append(_args))
            def selector(_gui, _folder, _role):
                return True  # Regression: previously skipped populate_linear.
            with patch.dict(sys.modules, {
                    "OpenSees_Complete_Export_V118":
                    SimpleNamespace(autoselect_inputs=selector)
                }), patch.object(analysis_autofill,"populate_linear",
                    return_value={"values": {}, "notes":["synced T1 X/Y"]}) as sync:
                analysis_autofill.populate_available(
                    app,folder,role="nonlinear_model_script")
            sync.assert_called_once_with(app,folder)

    def test_missing_model_does_not_invent_periods(self):
        from components.inputs import analysis_autofill
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            app=gui()
            app.model=Field(str(folder / "absent.py"))
            app._output_is_automatic=False
            app.project_input_audit={}
            app.log=SimpleNamespace(insert=lambda *_args: None)
            with patch.dict(sys.modules, {
                    "OpenSees_Complete_Export_V118":
                    SimpleNamespace(autoselect_inputs=lambda *_: True)
                }), patch.object(analysis_autofill,"populate_linear") as sync:
                analysis_autofill.populate_available(app,folder,role="linear_model_script")
            sync.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
