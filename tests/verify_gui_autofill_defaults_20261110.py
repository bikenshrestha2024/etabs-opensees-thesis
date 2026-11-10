"""Regression checks for gravity path defaults and MRSM period-refresh controls.

These are lightweight AST/source checks suitable for CI without ETABS COM.
They do not certify engineering equivalence or exercise Windows GUI widgets.
"""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DefaultControls(unittest.TestCase):
    def test_gravity_default_stays_model_scoped_and_manual_override_survives(self):
        source = (ROOT / "components/gravity/gui_and_reports.py").read_text(encoding="utf-8")
        ast.parse(source)
        assert "def _sync_default_output_root(self):" in source
        assert "analysis_output_folder(export_dir, state or \"ULS\")" in source
        assert "self._output_is_automatic = False" in source
        assert "ETABS Node Position (76 nodes)" in source

    def test_mrsm_refresh_keeps_strict_period_preflight(self):
        source = (ROOT / "components/response_spectrum/model_analysis.py").read_text(encoding="utf-8")
        ast.parse(source)
        assert "def refresh_verified_periods():" in source
        assert "mrsm_period_defaults(folder,verified,state)" in source
        assert "Refresh verified T1 X/Y" in source
        assert "require_source_state(folder,state)" in source
        assert "T1_X','T1_Y" in source


if __name__ == "__main__":
    unittest.main()
